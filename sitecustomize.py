"""Ensure the finance_backend package directory is importable from the workspace root."""

from __future__ import annotations

import sys
from pathlib import Path


project_dir = Path(__file__).resolve().parent / "finance_backend"
project_dir_str = str(project_dir)

if project_dir.exists() and project_dir_str not in sys.path:
    sys.path.insert(0, project_dir_str)