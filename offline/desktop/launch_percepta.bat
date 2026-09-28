@echo off
title PERCEPTA DEFENCE C2 — NATIVE DESKTOP
cd /d "%~dp0\..\.."
echo Starting PERCEPTA C2 Native Application...
if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe offline\desktop\launcher.py
) else (
    python offline\desktop\launcher.py
)
pause
