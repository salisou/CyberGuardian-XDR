# Architecture

The application is separated into UI (PyQt6), core services (telemetry, settings, logging, scoring and persistence), feature modules (collectors and analyzers), and tests.

Current data flow: UI requests read-only snapshots from service modules; psutil collects operating-system telemetry; core normalizes and scores indicators; the UI renders values. Potentially slow lookups and collection operations use QThread workers so they do not block the interface.

Implemented UI pages: Dashboard, process monitor, network monitor, Windows Event Viewer, Threat Intelligence, static Malware Analysis, and JSON/CSV Reports.

Implemented service foundations:
- Threat Intelligence: VirusTotal, AbuseIPDB, and AlienVault OTX read-only reputation lookups. API keys are environment variables; requests use TLS verification and bounded timeouts.
- Malware Analysis: SHA-256 and optional YARA static matching. Samples are never executed.
- Windows Event Viewer: bounded read-only collection from Windows event logs (optional pywin32).
- Reports: JSON/CSV export with row limits, atomic writes, and CSV formula-injection neutralization.

Initial SQLAlchemy schema: events, scans, processes, connections, reports and settings. Production schema evolution will use Alembic migrations.

Security boundaries: read-only by default; external scans require explicit authorization; network calls must use TLS, strict timeouts and response limits; malware samples are never executed by static analysis; secrets are never committed. Reputation and heuristic scores are triage signals, not confirmed compromise verdicts.

Not yet implemented: active vulnerability assessment, digital forensic acquisition/timeline, local AI assistant, full system monitor, secure credential vault, and advanced report templates. These are planned milestones, not available features.
