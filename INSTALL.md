# Installation

Supported target: Windows 10/11 x64 with Python 3.12 or newer.

1. Create a virtual environment: `py -3.12 -m venv .venv`
2. Activate it: `.\\.venv\\Scripts\\Activate.ps1`
3. Install dependencies: `python -m pip install --upgrade pip` then `pip install -r requirements.txt`
4. Launch: `python main.py`

The database, settings and logs are stored in the current user's application-data folders, not in the source checkout. Run as a standard user by default; some operating-system telemetry may be unavailable without elevation.

Run tests with `pytest --cov=core --cov=modules --cov-report=term-missing`.
