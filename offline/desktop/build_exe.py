"""
PERCEPTA PYINSTALLER WINDOWS EXE BUILDER
Compiles the native desktop launcher into a single executable PERCEPTA.exe
"""
import os
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent


def build():
    print("Compiling PERCEPTA.exe...")
    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--onefile",
        "--name=PERCEPTA",
        "--windowed",
        "--add-data=configs;configs",
        "--add-data=models;models",
        str(ROOT_DIR / "offline" / "desktop" / "launcher.py")
    ]
    res = subprocess.run(cmd, cwd=str(ROOT_DIR))
    if res.returncode == 0:
        print("PERCEPTA.exe built successfully in dist/PERCEPTA.exe")
    else:
        print("Build exited with code:", res.returncode)


if __name__ == "__main__":
    build()
