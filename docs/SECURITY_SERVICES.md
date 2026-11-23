# Security services — milestone 2

## Threat Intelligence

The service in `modules/threat_intel/service.py` supports read-only reputation lookups:
- VirusTotal: `VIRUSTOTAL_API_KEY`
- AbuseIPDB: `ABUSEIPDB_API_KEY` (IP addresses only)
- AlienVault OTX: optional `OTX_API_KEY`; public lookups may work without it

Set keys in the process environment. Do not commit API keys or put them in source code.
Requests verify TLS certificates and use bounded connect/read timeouts. Provider quotas and
terms apply. A missing API key is reported as an explicit provider error, not as a clean verdict.

Supported indicators are IPv4/IPv6, MD5/SHA-1/SHA-256 hashes, and domain names. URLs are not
accepted as domains. Reputation results are intelligence signals, not proof of compromise.

## Static file analysis

`modules/malware_analysis/static_scanner.py` calculates SHA-256 and optionally scans a file
with locally supplied YARA rules. It does not execute, unpack, detonate, or modify the target.
The default maximum file size is 100 MiB. YARA is optional and must be installed separately
with a trusted package source. Only use rule sets whose provenance you trust.

## Windows Event Log

`modules/windows_events/service.py` provides read-only collection of recent System log events.
It requires Windows and the optional `pywin32` package. The function has a bounded event count.
Run with the least privileges required; elevated access may expose more records.

## Reports

`modules/reports/exporter.py` exports structured records as JSON or CSV, with a 100,000-row
limit and atomic replacement. The caller is responsible for reviewing and redacting sensitive
data before sharing a report.

## Operational limitations

These modules are service-layer foundations; they are not yet wired into dedicated GUI pages.
They have not been executed on a Windows workstation in this development environment.
The CI workflow runs unit tests on Python 3.12 and 3.13 when GitHub Actions is enabled.
