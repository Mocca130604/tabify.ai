"""Tabify.ai Backend Application Package."""

import sys
from pathlib import Path

# Ensure root and backend directory are in sys.path
_app_dir = Path(__file__).resolve().parent
_backend_dir = _app_dir.parent
_repo_root = _backend_dir.parent
for _p in [str(_repo_root), str(_backend_dir)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)
