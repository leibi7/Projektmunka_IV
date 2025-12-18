import os
from pathlib import Path
import yaml
from typing import Any, Dict

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "settings.yaml"


def load_config(path: str | Path | None = None) -> Dict[str, Any]:
    """Load YAML config and allow environment overrides."""
    cfg_path = Path(path) if path else DEFAULT_CONFIG_PATH
    with open(cfg_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    default_cfg = data.get("default", {}) if isinstance(data, dict) else {}
    # simple env overrides
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        default_cfg["db_url"] = db_url
    return default_cfg
