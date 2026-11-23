import json
from pathlib import Path
from platformdirs import user_config_dir
from core.logger import get_logger
log = get_logger(__name__)

class SettingsManager:
    def __init__(self):
        self.path = Path(user_config_dir('CyberGuardian', 'CyberGuardian')) / 'settings.json'
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.values = self._load()
    def _load(self):
        defaults = {'refresh_interval_ms': 1000, 'theme': 'dark', 'telemetry_enabled': True}
        if not self.path.exists(): return defaults
        try:
            data = json.loads(self.path.read_text(encoding='utf-8'))
            if not isinstance(data, dict): raise ValueError('Settings root must be an object')
            return {**defaults, **data}
        except (OSError, ValueError, json.JSONDecodeError):
            log.exception('Unable to read settings; defaults selected'); return defaults
    def get(self, key, default=None): return self.values.get(key, default)
    def set(self, key, value): self.values[key] = value; self.save()
    def save(self):
        temporary = self.path.with_suffix('.tmp')
        temporary.write_text(json.dumps(self.values, indent=2), encoding='utf-8')
        temporary.replace(self.path)
