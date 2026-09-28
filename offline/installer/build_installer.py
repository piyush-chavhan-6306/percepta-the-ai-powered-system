"""
Build script to compile PERCEPTA_Setup.exe Windows Installer Wizard.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
PYINSTALLER = ROOT / "venv" / "Scripts" / "pyinstaller.exe"
WIZARD_SCRIPT = ROOT / "offline" / "installer" / "setup_wizard.py"

if not PYINSTALLER.exists():
    PYINSTALLER = Path("pyinstaller")


def build():
    print("=" * 60)
    print("COMPILING PERCEPTA DEFENCE SETUP WIZARD (PERCEPTA_Setup.exe)")
    print("=" * 60)

    cmd = [
        str(PYINSTALLER),
        "--name=PERCEPTA_Setup",
        "--onefile",
        "--noconsole",
        "--clean",
        f"--distpath={str(ROOT / 'dist')}",
        f"--workpath={str(ROOT / 'build' / 'installer_build')}",
        str(WIZARD_SCRIPT),
    ]

    print(f"Executing: {' '.join(cmd)}")
    res = subprocess.run(cmd, cwd=str(ROOT))
    if res.returncode == 0:
        print("\nSUCCESS: PERCEPTA_Setup.exe created successfully at dist/PERCEPTA_Setup.exe")
    else:
        print(f"\nFAILED with return code: {res.returncode}")
        sys.exit(res.returncode)


if __name__ == "__main__":
    build()
