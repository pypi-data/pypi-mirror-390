import json
from pathlib import Path

CONFIG_PATH = Path.home() / ".aether_config.json"

default_config = {
    "version": "0.1.0",
    "telemetry": False,
    "theme": "dark"
}

def load_config():
    if not CONFIG_PATH.exists():
        save_config(default_config)
    return json.loads(CONFIG_PATH.read_text())

def save_config(data):
    CONFIG_PATH.write_text(json.dumps(data, indent=4))
