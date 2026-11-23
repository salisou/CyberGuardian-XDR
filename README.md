# CyberGuardian XDR

CyberGuardian XDR is a modular Windows desktop security-monitoring platform built with Python 3.12+, PyQt6, SQLAlchemy and SQLite.

## Project status

The repository is being initialized in incremental, testable milestones. The first milestone establishes the application shell, secure configuration, centralized logging, persistence, system telemetry, process/network views and a deterministic threat-scoring engine. Advanced integrations (Windows event channels, Nmap, YARA, reputation providers, forensic artifact collectors and local LLMs) are added behind explicit service boundaries and capability checks.

## Requirements

- Windows 10/11 x64
- Python 3.12+
- Administrator privileges only for operations that genuinely require them; the application itself should run as a standard user.

## Quick start

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

## Security principles

- Read-only monitoring by default.
- No automatic remediation, process termination, registry modification or firewall changes.
- Validate all user-controlled inputs and bound network timeouts.
- Store provider credentials outside source control; prefer Windows Credential Manager in production deployments.
- Treat telemetry, filenames, process command lines and external intelligence responses as untrusted data.
- Do not execute samples during malware analysis. Use isolated, disposable sandboxes for dynamic analysis.
- Network and vulnerability scans require explicit authorization from the asset owner.

## Documentation

- [Installation](INSTALL.md)
- [Architecture](ARCHITECTURE.md)

## Disclaimer

CyberGuardian XDR is a defensive security tool. Use it only on systems and networks you own or are explicitly authorized to assess. Security scores are heuristic indicators, not proof that a system is secure or compromised.
