@echo off
echo Phone-PC Sync Emulator Pro
echo ===========================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo Starting Phone-PC Sync Emulator Launcher...
echo.

REM Start the launcher
python launcher.py

echo.
echo Application closed.
pause