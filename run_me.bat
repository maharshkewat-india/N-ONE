@echo off
setlocal
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo Python was not found on PATH. Install Python 3.10 or newer and try again.
    echo During installation, enable the option to add Python to PATH.
    pause
    exit /b 1
)

echo Setting up and starting N-ONE...
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup_and_run.ps1"
set "exit_code=%ERRORLEVEL%"

if not "%exit_code%"=="0" (
    echo.
    echo Setup or launch failed with exit code %exit_code%.
) else (
    echo.
    echo N-ONE has stopped.
)
pause
exit /b %exit_code%
