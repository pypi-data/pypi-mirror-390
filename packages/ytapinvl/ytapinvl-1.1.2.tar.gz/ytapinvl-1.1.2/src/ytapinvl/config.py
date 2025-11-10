import json, os
from pathlib import Path

APP_DIR = Path.home() / ".config" / "ytapinvl"
APP_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_PATH = APP_DIR / "config.json"
HISTORY_PATH = APP_DIR / "history.json"

DEFAULTS = {
    "base_url": "https://ytdlpyton.nvlgroup.my.id",
    "wa": None,
    "last_ip": None,
    "apikey": None
}

def load_config():
    if CONFIG_PATH.exists():
        try:
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            return {**DEFAULTS, **data}
        except Exception:
            return DEFAULTS.copy()
    return DEFAULTS.copy()

def save_config(data: dict):
    merged = {**load_config(), **data}
    CONFIG_PATH.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    return merged

def save_history(data: dict):
    HISTORY_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def load_history():
    if HISTORY_PATH.exists():
        try:
            return json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}