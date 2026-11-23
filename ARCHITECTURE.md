# Architecture

The application is separated into UI (PyQt6), core services (telemetry, settings, logging, scoring and persistence), feature modules (collectors and analyzers), and tests.

Current data flow: UI requests a read-only snapshot from a module service; psutil collects operating-system telemetry; core normalizes and scores indicators; the UI renders values. Collection failures are isolated and logged.

Initial SQLAlchemy schema: events, scans, processes, connections, reports and settings. Production schema evolution will use Alembic migrations.

Security boundaries: read-only by default; external scans require explicit authorization; network calls must use TLS, strict timeouts and response limits; malware samples are never executed by static analysis; secrets are never committed. Heuristic scores are triage signals, not confirmed compromise verdicts.
