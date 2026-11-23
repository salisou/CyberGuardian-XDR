"""Read-only reputation lookups for defensive threat intelligence.

API keys are read from environment variables; never persist secrets in settings.
All requests use TLS verification and bounded timeouts.
"""
from __future__ import annotations

import hashlib
import ipaddress
import os
import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

import requests

TIMEOUT = (4, 12)
USER_AGENT = "CyberGuardian-XDR/0.2 (defensive-security-tool)"


@dataclass
class ReputationResult:
    provider: str
    indicator: str
    indicator_type: str
    verdict: str
    score: int | None = None
    details: str = ""
    raw: dict[str, Any] | None = None


class ThreatIntelError(RuntimeError):
    pass


def _session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT, "Accept": "application/json"})
    return session


def validate_indicator(value: str, kind: str) -> str:
    value = value.strip()
    if not value or len(value) > 253:
        raise ValueError("Indicatore vuoto o troppo lungo")
    if kind == "ip":
        return str(ipaddress.ip_address(value))
    if kind == "hash":
        normalized = value.lower()
        if len(normalized) not in (32, 40, 64) or any(c not in "0123456789abcdef" for c in normalized):
            raise ValueError("Hash non valido: usare MD5, SHA-1 o SHA-256")
        return normalized
    if kind == "domain":
        if "/" in value or "://" in value or any(char in value for char in "?#@"):
            raise ValueError("Inserire un dominio, non un URL")
        domain = value.rstrip(".").lower()
        try:
            ascii_domain = domain.encode("idna").decode("ascii")
        except UnicodeError as exc:
            raise ValueError("Nome dominio non valido") from exc
        if len(ascii_domain) > 253 or not re.fullmatch(
            r"(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)(?:\.(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?))*",
            ascii_domain,
        ):
            raise ValueError("Nome dominio non valido")
        return ascii_domain
    raise ValueError("Tipo indicatore non supportato")


def sha256_file(path: str, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def lookup_virustotal(indicator: str, kind: str) -> ReputationResult:
    key = os.getenv("VIRUSTOTAL_API_KEY")
    if not key:
        raise ThreatIntelError("Configurare VIRUSTOTAL_API_KEY nelle variabili d'ambiente")
    indicator = validate_indicator(indicator, kind)
    endpoint_kind = {"ip": "ip_addresses", "hash": "files", "domain": "domains"}[kind]
    url = f"https://www.virustotal.com/api/v3/{endpoint_kind}/{quote(indicator, safe='')}"
    try:
        response = _session().get(url, headers={"x-apikey": key}, timeout=TIMEOUT)
        if response.status_code == 404:
            return ReputationResult("VirusTotal", indicator, kind, "UNKNOWN", details="Indicatore non presente")
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        raise ThreatIntelError(f"VirusTotal non raggiungibile: {exc}") from exc
    stats = payload.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
    malicious = int(stats.get("malicious", 0))
    suspicious = int(stats.get("suspicious", 0))
    total = sum(int(v) for v in stats.values() if isinstance(v, (int, float)))
    verdict = "MALICIOUS" if malicious else "SUSPICIOUS" if suspicious else "NO_DETECTION"
    return ReputationResult("VirusTotal", indicator, kind, verdict, malicious,
                             f"Rilevamenti: {malicious} malevoli, {suspicious} sospetti su {total}",
                             {"last_analysis_stats": stats})


def lookup_abuseipdb(ip: str) -> ReputationResult:
    key = os.getenv("ABUSEIPDB_API_KEY")
    if not key:
        raise ThreatIntelError("Configurare ABUSEIPDB_API_KEY nelle variabili d'ambiente")
    ip = validate_indicator(ip, "ip")
    try:
        response = _session().get(
            "https://api.abuseipdb.com/api/v2/check",
            params={"ipAddress": ip, "maxAgeInDays": "90", "verbose": "false"},
            headers={"Key": key, "Accept": "application/json"}, timeout=TIMEOUT,
        )
        response.raise_for_status()
        data = response.json().get("data", {})
    except requests.RequestException as exc:
        raise ThreatIntelError(f"AbuseIPDB non raggiungibile: {exc}") from exc
    score = int(data.get("abuseConfidenceScore", 0))
    verdict = "MALICIOUS" if score >= 75 else "SUSPICIOUS" if score >= 25 else "LOW_RISK"
    return ReputationResult("AbuseIPDB", ip, "ip", verdict, score,
                             f"Abuse confidence: {score}/100; segnalazioni: {data.get('totalReports', 0)}")


def lookup_otx(indicator: str, kind: str) -> ReputationResult:
    indicator = validate_indicator(indicator, kind)
    if kind == "ip":
        section = "IPv6" if ":" in indicator else "IPv4"
    else:
        section = {"hash": "file", "domain": "domain"}[kind]
    url = f"https://otx.alienvault.com/api/v1/indicators/{section}/{quote(indicator, safe='')}/general"
    headers = {}
    key = os.getenv("OTX_API_KEY")
    if key:
        headers["X-OTX-API-KEY"] = key
    try:
        response = _session().get(url, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        raise ThreatIntelError(f"AlienVault OTX non raggiungibile: {exc}") from exc
    count = int(data.get("pulse_info", {}).get("count", 0))
    verdict = "SUSPICIOUS" if count else "NO_PULSES"
    return ReputationResult("AlienVault OTX", indicator, kind, verdict, count,
                             f"Pulse associati: {count}")


def lookup_all(indicator: str, kind: str) -> list[ReputationResult]:
    """Query configured providers; failures are returned as explicit error rows."""
    normalized = validate_indicator(indicator, kind)
    results: list[ReputationResult] = []
    providers = [("VirusTotal", lambda: lookup_virustotal(normalized, kind)),
                 ("AlienVault OTX", lambda: lookup_otx(normalized, kind))]
    if kind == "ip":
        providers.append(("AbuseIPDB", lambda: lookup_abuseipdb(normalized)))
    for name, callback in providers:
        try:
            results.append(callback())
        except (ThreatIntelError, ValueError) as exc:
            results.append(ReputationResult(name, normalized, kind, "ERROR", details=str(exc)))
    return results
