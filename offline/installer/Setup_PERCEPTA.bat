@echo off
setlocal
cd /d "%~dp0"
title PERCEPTA Defence Setup Wizard
powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "%~dp0Setup_PERCEPTA.ps1"
if %ERRORLEVEL% neq 0 (
    echo Launching Setup Wizard...
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Setup_PERCEPTA.ps1"
)
