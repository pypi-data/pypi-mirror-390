from __future__ import annotations
import os
from datetime import datetime


def make_timestamped_output_dir(base_dir: str) -> str:
    """Create and return a timestamped subdirectory under base_dir.

    Format: MonDay_output_HHMMSS (e.g., Nov9_output_142530)
    """
    now = datetime.now()
    day_mon = f"{now.strftime('%b')}{now.day}"
    hhmmss = now.strftime("%H%M%S")
    out_dir = os.path.join(base_dir, f"{day_mon}_output_{hhmmss}")
    os.makedirs(out_dir, exist_ok=True)
    return out_dir

