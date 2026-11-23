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
- Vulnerability Scanner requires the Nmap executable installed separately and available in `PATH`. It performs a conservative TCP connect scan of the top 100 ports with service detection. The user must explicitly confirm authorization for each scan. It is a service-exposure assessment, not a CVE scanner.
- AI Assistant requires Ollama installed and running locally on `127.0.0.1:11434`. Download a model, for example with `ollama pull llama3.2`, then use **Carica modelli** in the application. The client does not use external endpoints or environment-configured HTTP proxies. Avoid entering passwords, API keys or unnecessary personal data into prompts.

The database, settings and logs are stored in the current user's application-data folders, not in the source checkout. Run as a standard user by default; some operating-system telemetry may be unavailable without elevation.

Run tests with `pytest --cov=core --cov=modules --cov-report=term-missing`.
