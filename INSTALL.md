# Installation

Supported target: Windows 10/11 x64 with Python 3.12 or newer.

1. Create a virtual environment: `py -3.12 -m venv .venv`
2. Activate it: `.\\.venv\\Scripts\\Activate.ps1`
3. Install core dependencies: `python -m pip install --upgrade pip` then `pip install -r requirements.txt`
4. Optional Windows integrations: `pip install -r requirements-optional-windows.txt`
5. Launch: `python main.py`

## Optional integrations

- Windows Event Viewer requires `pywin32`. The Event Viewer page is read-only and is available only on Windows.
- YARA static scanning requires `yara-python`. Without it, the Malware Analysis page still calculates SHA-256 and displays a clear warning.
- Threat Intelligence requires provider API keys supplied as environment variables: `VIRUSTOTAL_API_KEY`, `ABUSEIPDB_API_KEY`, and optionally `OTX_API_KEY`. Never place keys in source code, screenshots, reports, or Git commits. Restart the application after setting environment variables.

The database, settings and logs are stored in the current user's application-data folders, not in the source checkout. Run as a standard user by default; some operating-system telemetry may be unavailable without elevation.

Run tests with `pytest --cov=core --cov=modules --cov-report=term-missing`.
