"""Rule-based event correlation and durable alert lifecycle.

Rules are explainable triage heuristics, not proof of compromise.
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from sqlalchemy import func, select
from core.database import SecurityAlert, SessionLocal


def _fingerprint(rule_id: str, source: str) -> str:
    raw = f"{rule_id}|{source.casefold().strip()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def correlate_windows_events(events: list[dict]) -> list[dict]:
    findings: list[dict] = []
    event_ids: dict[int, int] = {}
    for event in events:
        try:
            event_id = int(event.get("event_id", -1))
        except (TypeError, ValueError):
            continue
        event_ids[event_id] = event_ids.get(event_id, 0) + 1

    if event_ids.get(1102, 0):
        findings.append({
            "rule_id": "WINDOWS-LOG-CLEARED",
            "severity": "HIGH",
            "title": "Windows Security audit log cleared",
            "source": "Windows Security",
            "details": f"Rilevato {event_ids[1102]} evento/i 1102 nel campione acquisito. Verificare autorizzazione, contesto e orario.",
        })
    if event_ids.get(7045, 0):
        findings.append({
            "rule_id": "WINDOWS-SERVICE-INSTALLED",
            "severity": "MEDIUM",
            "title": "New Windows service installation event",
            "source": "Windows System",
            "details": f"Rilevato {event_ids[7045]} evento/i 7045. Verificare nome servizio, percorso binario e change request.",
        })
    failed_logons = event_ids.get(4625, 0)
    if failed_logons >= 5:
        findings.append({
            "rule_id": "WINDOWS-FAILED-LOGONS",
            "severity": "MEDIUM" if failed_logons < 15 else "HIGH",
            "title": "Repeated failed Windows logons",
            "source": "Windows Security",
            "details": f"Rilevati {failed_logons} eventi 4625 nel campione. Correlare account, IP sorgente e finestra temporale.",
        })
    return findings


def persist_alerts(findings: list[dict], now: datetime | None = None) -> int:
    if not findings:
        return 0
    observed_at = now or datetime.now(timezone.utc)
    created_or_updated = 0
    with SessionLocal() as session:
        for item in findings:
            fingerprint = _fingerprint(item["rule_id"], item["source"])
            alert = session.scalar(select(SecurityAlert).where(SecurityAlert.fingerprint == fingerprint))
            if alert is None:
                session.add(SecurityAlert(
                    fingerprint=fingerprint, first_seen=observed_at,
                    last_seen=observed_at, severity=item["severity"],
                    title=item["title"], source=item["source"],
                    details=item["details"], occurrences=1, status="OPEN",
                ))
            else:
                alert.last_seen = observed_at
                alert.severity = item["severity"]
                alert.details = item["details"]
                alert.occurrences += 1
                if alert.status == "CLOSED":
                    alert.status = "OPEN"
            created_or_updated += 1
        session.commit()
    return created_or_updated


def list_alerts(status: str | None = None, limit: int = 500) -> list[dict]:
    limit = max(1, min(int(limit), 1000))
    with SessionLocal() as session:
        query = select(SecurityAlert).order_by(SecurityAlert.last_seen.desc()).limit(limit)
        if status in {"OPEN", "ACKNOWLEDGED", "CLOSED"}:
            query = select(SecurityAlert).where(SecurityAlert.status == status).order_by(SecurityAlert.last_seen.desc()).limit(limit)
        rows = session.scalars(query).all()
        return [{
            "id": row.id, "severity": row.severity, "title": row.title,
            "source": row.source, "details": row.details,
            "occurrences": row.occurrences, "status": row.status,
            "first_seen": row.first_seen.isoformat(), "last_seen": row.last_seen.isoformat(),
        } for row in rows]


def count_open_alerts() -> int:
    with SessionLocal() as session:
        return int(session.scalar(
            select(func.count(SecurityAlert.id)).where(SecurityAlert.status == "OPEN")
        ) or 0)


def update_alert_status(alert_id: int, status: str) -> bool:
    if status not in {"ACKNOWLEDGED", "CLOSED", "OPEN"}:
        raise ValueError("Stato alert non valido")
    with SessionLocal() as session:
        alert = session.get(SecurityAlert, int(alert_id))
        if alert is None:
            return False
        alert.status = status
        session.commit()
        return True
