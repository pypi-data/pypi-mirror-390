import json
import os
from typing import Any, Dict


def load_meta(meta_path: str) -> Dict[str, Any]:
    """Load meta configuration. Supports JSON natively; YAML if PyYAML is available.

    Recommended: use .json to avoid extra deps.
    """
    if not os.path.exists(meta_path):
        raise FileNotFoundError(f"Meta file not found: {meta_path}")
    ext = os.path.splitext(meta_path)[1].lower()
    if ext in (".json", ""):
        with open(meta_path, "r") as f:
            return json.load(f)
    elif ext in (".yml", ".yaml"):
        try:
            import yaml  # type: ignore
        except Exception:
            raise RuntimeError("YAML meta provided but PyYAML is not installed. Use JSON meta instead.")
        with open(meta_path, "r") as f:
            return yaml.safe_load(f)
    else:
        raise ValueError(f"Unsupported meta file extension: {ext}. Use .json or .yaml")


def get(meta: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Helper to fetch nested keys using dotted path, e.g., 'models.ss.type'."""
    cur: Any = meta
    for part in key.split('.'):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return default
    return cur

