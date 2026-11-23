# Architecture

The application is separated into UI (PyQt6), core services (telemetry, settings, logging, scoring, correlation and persistence), feature modules (collectors and analyzers), and tests.

Current data flow: UI requests read-only snapshots from service modules; collectors gather local operating-system telemetry and Windows events; core normalizes indicators, correlates known event patterns and persists alert state; the UI renders the resulting findings. Potentially slow collection and lookups use QThread workers so they do not block the interface.

Implemented UI pages: Dashboard, Alert Center, process monitor, network monitor, Windows Event Viewer, Threat Intelligence, Vulnerability Scanner, static Malware Analysis, local evidence inventory (Forensics), JSON/CSV Reports, and local Ollama AI Assistant.

Implemented service foundations:
- Threat Intelligence: VirusTotal, AbuseIPDB, and AlienVault OTX read-only reputation lookups. API keys are environment variables; requests use TLS verification and bounded timeouts.
- Malware Analysis: SHA-256 and optional YARA static matching. Samples are never executed.
- Windows Event Viewer: bounded read-only collection from Windows event logs (optional pywin32).
- Vulnerability Scanner: explicitly authorized, bounded Nmap TCP connect/service detection against a single host or a network of at most 256 addresses. No exploit scripts or stealth options. It identifies exposed services; it does not claim CVE validation.
- Forensics: read-only filesystem evidence manifest with metadata and optional SHA-256. This is an inventory, not a forensic disk image or a chain-of-custody acquisition.
- Reports: JSON/CSV export with row limits, atomic writes, and CSV formula-injection neutralization.
- AI Assistant: local Ollama model discovery and generation through loopback only. It does not automatically ingest event logs or secrets.
- XDR correlation: initial explainable rules for Windows events 1102, 7045 and repeated 4625 failures. Alerts are persisted with stable fingerprints, occurrence counters and OPEN/ACKNOWLEDGED/CLOSED lifecycle states. Dashboard displays the count of OPEN alerts.

Initial SQLAlchemy schema: events, alerts, scans, processes, connections, reports and settings. Production schema evolution will use Alembic migrations.

Security boundaries: read-only by default; external scans require explicit authorization; network calls must use TLS, strict timeouts and response limits; malware samples are never executed by static analysis; secrets are never committed. Reputation and heuristic scores are triage signals, not confirmed compromise verdicts.

Not yet implemented: full system monitor, secure credential vault, disk/memory acquisition, forensic timeline correlation, CVE enrichment, automated scan scheduling, broader event correlation rules, endpoint agent/central collector, and advanced report templates. These are planned milestones, not available features.
