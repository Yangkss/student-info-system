"""Configuration management: defaults < config file < environment variables."""
import json
import os
from pathlib import Path

from src.utils.exceptions import ConfigError

# Project root (two levels above src/utils)
ROOT = Path(__file__).resolve().parents[2]

DEFAULTS = {
    "data_file": "data/students.json",
    "log_file": "logs/app.log",
    "log_level": "INFO",
    "export_dir": "exports",
}


def load_config(path=None):
    """Load settings and return them with absolute paths.

    Order of precedence (lowest to highest):
      1. built-in defaults
      2. config/config.json (or the file named in SIS_CONFIG)
      3. environment variables SIS_DATA_FILE, SIS_LOG_FILE, SIS_LOG_LEVEL
    """
    config = dict(DEFAULTS)
    config_path = Path(path or os.environ.get("SIS_CONFIG", ROOT / "config" / "config.json"))

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config.update(json.load(f))
    except FileNotFoundError:
        pass  # fall back to defaults
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Config file {config_path} is not valid JSON: {exc}") from exc

    # Environment overrides make the app easy to run in containers/cloud hosts
    for key, env_name in (("data_file", "SIS_DATA_FILE"),
                          ("log_file", "SIS_LOG_FILE"),
                          ("log_level", "SIS_LOG_LEVEL")):
        if os.environ.get(env_name):
            config[key] = os.environ[env_name]

    # Make relative paths relative to the project root
    for key in ("data_file", "log_file", "export_dir"):
        p = Path(config[key])
        config[key] = str(p if p.is_absolute() else ROOT / p)

    return config
