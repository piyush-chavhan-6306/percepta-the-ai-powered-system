"""
PERCEPTA OFFLINE NATIVE DESKTOP LAUNCHER
Orchestrates local services, database, AI models, and launches a native desktop C2 window.
"""
import os
import sys
import time
import subprocess
import signal
from pathlib import Path
import urllib.request

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = 8000
FRONTEND_PORT = 5000


def check_health(url: str, timeout: float = 1.0) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return response.status == 200
    except Exception:
        return False


def main():
    print("=" * 60)
    print("PERCEPTA DEFENCE C2 — OFFLINE DESKTOP ORCHESTRATOR")
    print("=" * 60)

    # 1. Environment & Directories
    os.environ["APP_ENV"] = "offline"
    os.environ["DEMO_MODE"] = "true"
    storage_dir = ROOT_DIR / "offline" / "storage"
    storage_dir.mkdir(parents=True, exist_ok=True)
    print(f"[1/5] Storage Initialized: {storage_dir}")

    # 2. Check Database & AI Models
    db_file = ROOT_DIR / "percepta.db"
    model_file = ROOT_DIR / "models" / "yolov8n.pt"
    print(f"[2/5] Database Status: {'Ready' if db_file.exists() else 'Will initialize on start'}")
    print(f"      AI Model Status: {'Ready' if model_file.exists() else 'Default model path configured'}")

    # 3. Start Backend if not already running
    backend_proc = None
    backend_url = f"http://{BACKEND_HOST}:{BACKEND_PORT}/api/health"
    if not check_health(backend_url):
        print(f"[3/5] Starting Local Perception Engine on {BACKEND_HOST}:{BACKEND_PORT}...")
        python_exe = sys.executable
        backend_proc = subprocess.Popen(
            [python_exe, "-m", "uvicorn", "backend.main:app", "--host", BACKEND_HOST, "--port", str(BACKEND_PORT)],
            cwd=str(ROOT_DIR),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        # Wait for backend
        for _ in range(20):
            if check_health(backend_url):
                print("      Backend Engine Online.")
                break
            time.sleep(0.5)
    else:
        print(f"[3/5] Backend Engine already running on {BACKEND_HOST}:{BACKEND_PORT}.")

    # 4. Check Frontend / C2 Interface
    frontend_url = f"http://localhost:{FRONTEND_PORT}"
    print(f"[4/5] Target Interface: {frontend_url}")

    # 5. Launch Native Desktop Window (Edge WebView2 App Mode)
    print("[5/5] Launching PERCEPTA C2 Native Desktop Window...")
    edge_paths = [
        Path(os.environ.get("ProgramFiles(x86)", "C:/Program Files (x86)")) / "Microsoft/Edge/Application/msedge.exe",
        Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Microsoft/Edge/Application/msedge.exe",
    ]
    edge_exe = next((p for p in edge_paths if p.exists()), None)

    try:
        if edge_exe:
            # Launch in standalone application window mode (no URL bar, no tabs)
            app_args = [
                str(edge_exe),
                f"--app={frontend_url}",
                "--window-size=1600,950",
                f"--user-data-dir={storage_dir / 'desktop_profile'}",
            ]
            desktop_proc = subprocess.Popen(app_args)
            print("PERCEPTA C2 Desktop Window active. Close the window to shut down.")
            desktop_proc.wait()
        else:
            import webbrowser
            webbrowser.open(frontend_url)
    finally:
        print("\nShutting down PERCEPTA Desktop session...")
        if backend_proc:
            backend_proc.terminate()
            try:
                backend_proc.wait(timeout=3)
            except Exception:
                backend_proc.kill()
        print("PERCEPTA session ended cleanly.")


if __name__ == "__main__":
    main()
