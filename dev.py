"""Cross-platform runner to launch both backend and frontend simultaneously."""

import sys
import os
import subprocess
import signal
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND_DIR = ROOT / "backend"
FRONTEND_DIR = ROOT / "frontend"

python_bin = sys.executable
if (BACKEND_DIR / ".venv" / "Scripts" / "python.exe").exists():
    python_bin = str(BACKEND_DIR / ".venv" / "Scripts" / "python.exe")
elif (BACKEND_DIR / ".venv" / "bin" / "python").exists():
    python_bin = str(BACKEND_DIR / ".venv" / "bin" / "python")

print("=" * 60)
print("🚀 Starting Tabify.ai Fullstack Environment")
print("=" * 60)
print(f"Backend Python: {python_bin}")
print(f"Backend URL:    http://127.0.0.1:8000")
print(f"Frontend URL:   http://127.0.0.1:5173")
print("=" * 60)

backend_proc = subprocess.Popen(
    [python_bin, "-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"],
    cwd=str(ROOT),
)

npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
frontend_proc = subprocess.Popen(
    [npm_cmd, "run", "dev", "--", "--host", "127.0.0.1", "--port", "5173"],
    cwd=str(FRONTEND_DIR),
)

def shutdown(sig, frame):
    print("\n🛑 Shutting down Tabify.ai...")
    try:
        backend_proc.terminate()
        frontend_proc.terminate()
    except Exception:
        pass
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown)
if hasattr(signal, "SIGTERM"):
    signal.signal(signal.SIGTERM, shutdown)

try:
    backend_proc.wait()
    frontend_proc.wait()
except KeyboardInterrupt:
    shutdown(None, None)
