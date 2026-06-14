@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title VOIDCLAW Installer

:: Reliable way to get ESC character for colors
for /f %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"
set "RED=%ESC%[91m"
set "GREEN=%ESC%[92m"
set "ORANGE=%ESC%[38;5;214m"
set "AMBER=%ESC%[93m"
set "WHITE=%ESC%[97m"
set "RESET=%ESC%[0m"

cls
echo %ORANGE%
echo ================================================================
echo.
echo      ██╗   ██╗ ██████╗ ██╗██████╗  ██████╗██╗      █████╗ ██╗    ██╗
echo      ██║   ██║██╔═══██╗██║██╔══██╗██╔════╝██║     ██╔══██╗██║    ██║
echo      ██║   ██║██║   ██║██║██║  ██║██║     ██║     ███████║██║ █╗ ██║
echo      ╚██╗ ██╔╝██║   ██║██║██║  ██║██║     ██║     ██╔══██║██║███╗██║
echo       ╚████╔╝ ╚██████╔╝██║██████╔╝╚██████╗███████╗██║  ██║╚███╔███╔╝
echo        ╚═══╝   ╚═════╝ ╚═╝╚═════╝  ╚═════╝╚══════╝╚═╝  ╚═╝ ╚══╝╚══╝
echo.
echo %AMBER%           AI Agent for Windows, Mac, Android ^& Linux
echo.
echo %ORANGE%================================================================
echo %RESET%

:: Ensure we are in the root directory
cd /d "%~dp0.."

:: 1. Check Python
echo %ORANGE%[*] Checking Python installation...%RESET%
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%[!] Python 3 is not installed or not in PATH.%RESET%
    echo %AMBER%Please install Python from https://www.python.org/%RESET%
    pause
    exit /b 1
)
echo %GREEN%[+] Python found!%RESET%
echo.

:: 2. Setup Venv
echo %ORANGE%[*] Creating virtual environment...%RESET%
if not exist .venv (
    python -m venv .venv
)
call .venv\Scripts\activate
echo %ORANGE%[*] Installing/Updating dependencies...%RESET%
python -m pip install --upgrade pip --quiet

:: Install core dependencies first
echo %ORANGE%[*] Installing core dependencies...%RESET%
pip install pyyaml requests python-telegram-bot ollama duckduckgo-search python-dotenv flask flask-cors waitress youtube-transcript-api beautifulsoup4 yt-dlp apscheduler psutil numpy --quiet

:: Try to install everything else
echo %ORANGE%[*] Finalizing installation...%RESET%
pip install -r requirements.txt --quiet

echo %GREEN%[+] Dependencies installed!%RESET%
echo.

:: 3. Configuration Wizard
echo %AMBER%Starting Configuration Wizard...%RESET%
python core/setup.py

pause
