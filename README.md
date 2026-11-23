# CyberGuardian XDR

CyberGuardian XDR is a modular Windows desktop security-monitoring and triage application built with Python 3.12+, PyQt6, SQLAlchemy and SQLite.

## Project status

The application is under active development in incremental milestones. The current develop branch includes a working application shell and service foundations for local monitoring, threat-intelligence lookups, static file analysis, Windows event review, authorized Nmap service assessment, evidence inventory, local AI assistance, event correlation and alert lifecycle management. This is an evolving development build, not a production-certified XDR platform.

## Available sections

- Dashboard with CPU/RAM telemetry, heuristic threat score and open-alert count
- Alert Center with rule-based Windows event correlation and alert acknowledgement/closure
- Process monitor and network connection viewer
- Windows Event Viewer (optional pywin32)
- Threat Intelligence: VirusTotal, AbuseIPDB and AlienVault OTX
- Vulnerability Scanner: bounded, explicitly authorized Nmap TCP/service scan
- Malware Analysis: SHA-256 and optional YARA static matching; no sample execution
- Forensics: read-only file inventory and optional SHA-256 manifest
- Reports: local security-event export to JSON or CSV
- AI Assistant: local Ollama model interface, loopback only

## Current correlation rules

- Windows Security event 1102: audit log cleared (HIGH)
- Windows System event 7045: service installation (MEDIUM)
- Windows Security event 4625: at least five failed logons in the collected sample (MEDIUM/HIGH)

The rules are explainable triage heuristics. They do not independently establish malicious intent, and event sampling is not a substitute for continuous SIEM collection.

## Requirements

- Windows 10/11 x64
- Python 3.12+
- Nmap executable for the Vulnerability Scanner
- Ollama installed locally and at least one downloaded model for AI Assistant
- Optional: pywin32, yara-python, and provider API keys for the related integrations

## Quick start

~~~powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
~~~

For optional integrations, see [Installation](INSTALL.md).

## Security principles

- Read-only monitoring by default.
- No automatic remediation, process termination, registry modification or firewall changes.
- Validate user-controlled inputs and bound network timeouts.
- Store provider credentials outside source control; production deployments should use Windows Credential Manager or DPAPI.
- Treat telemetry, filenames, process command lines and external intelligence responses as untrusted data.
- Do not execute samples during malware analysis. Use isolated, disposable sandboxes for dynamic analysis.
- Network and vulnerability scans require explicit authorization from the asset owner.
- Reputation and heuristic scores are triage signals, not proof of compromise.
- AI prompts are sent to the local Ollama service only; do not include secrets or unnecessary personal data.

## Documentation

- [Installation](INSTALL.md)
- [Architecture](ARCHITECTURE.md)
- [Security services](docs/SECURITY_SERVICES.md)

## Tests

Run the automated tests with:

~~~powershell
pytest -q
~~~

GitHub Actions is configured to run the test suite on Python 3.12 and 3.13 for pushes and pull requests to main and develop.

## Disclaimer

CyberGuardian XDR is a defensive security tool. Use it only on systems and networks you own or are explicitly authorized to assess. The project is not yet production-ready; do not rely on it as the sole security control.
