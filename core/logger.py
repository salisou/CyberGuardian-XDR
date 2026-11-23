import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from platformdirs import user_log_dir

_CONFIGURED = False

def configure_logging(level=logging.INFO):
    global _CONFIGURED
    if _CONFIGURED: return
    folder = Path(user_log_dir('CyberGuardian', 'CyberGuardian'))
    folder.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(folder / 'cyberguardian.log', maxBytes=2_000_000, backupCount=5, encoding='utf-8')
    handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s'))
    root = logging.getLogger(); root.setLevel(level); root.addHandler(handler)
    _CONFIGURED = True

def get_logger(name): return logging.getLogger(name)
