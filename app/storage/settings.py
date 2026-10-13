import json
import os
from pathlib import Path

from app.utils.paths import app_dir


DEFAULT_SETTINGS = {
    "theme": "system",
    "geometry": "900x650",
    "always_on_top": False,
    "angle_mode": "DEG",
}


class JsonStorage:
    def __init__(self, directory=None):
        self.directory = Path(directory) if directory else app_dir()
        self.settings_path = self.directory / "settings.json"
        self.history_path = self.directory / "history.json"

    def load_settings(self):
        try:
            with self.settings_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
            if not isinstance(data, dict):
                raise ValueError("Format settings.json tidak valid")
            settings = dict(DEFAULT_SETTINGS)
            settings.update(data)
            if settings["theme"] not in ("light", "dark", "system"):
                settings["theme"] = "system"
            if settings["angle_mode"] not in ("DEG", "RAD"):
                settings["angle_mode"] = "DEG"
            return settings
        except FileNotFoundError:
            return dict(DEFAULT_SETTINGS)

    def save_settings(self, settings):
        self._write_json(self.settings_path, settings)

    def load_history(self):
        try:
            with self.history_path.open("r", encoding="utf-8") as file:
                entries = json.load(file)
            if not isinstance(entries, list):
                raise ValueError("Format history.json tidak valid")
            return [item for item in entries if isinstance(item, dict)][-100:]
        except FileNotFoundError:
            return []

    def save_history(self, entries):
        self._write_json(self.history_path, entries[-100:])

    @staticmethod
    def _write_json(path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        try:
            with temporary.open("w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
                file.flush()
                os.fsync(file.fileno())
            temporary.replace(path)
        except OSError:
            try:
                temporary.unlink()
            except OSError:
                pass
            raise
