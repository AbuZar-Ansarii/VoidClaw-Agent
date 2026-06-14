#!/bin/bash

# Colors
ORANGE='\033[38;5;214m'
AMBER='\033[93m'
GREEN='\033[92m'
RED='\033[91m'
RESET='\033[0m'

clear
echo -e "${ORANGE}"
echo "================================================================"
echo ""
echo "      ██╗   ██╗ ██████╗ ██╗██████╗  ██████╗██╗      █████╗ ██╗    ██╗"
echo "      ██║   ██║██╔═══██╗██║██╔══██╗██╔════╝██║     ██╔══██╗██║    ██║"
echo "      ██║   ██║██║   ██║██║██║  ██║██║     ██║     ███████║██║ █╗ ██║"
echo "      ╚██╗ ██╔╝██║   ██║██║██║  ██║██║     ██║     ██╔══██║██║███╗██║"
echo "       ╚████╔╝ ╚██████╔╝██║██████╔╝╚██████╗███████╗██║  ██║╚███╔███╔╝"
echo "        ╚═══╝   ╚═════╝ ╚═╝╚═════╝  ╚═════╝╚══════╝╚═╝  ╚═╝ ╚══╝╚══╝"
echo ""
echo -e "${AMBER}           AI Agent for Windows, Mac, Android & Linux${RESET}"
echo -e "${ORANGE}================================================================${RESET}"

# Ensure we are in the root directory
cd "$(dirname "$0")/.."

echo -e "${ORANGE}[*] Updating system packages...${RESET}"
pkg update -y && pkg upgrade -y

echo -e "${ORANGE}[*] Installing dependencies...${RESET}"
pkg install python git clang make -y

# Optional but recommended for numpy/sklearn on Termux
# pkg install python-numpy python-scikit-learn -y

echo -e "${ORANGE}[*] Setting up virtual environment...${RESET}"
if [ ! -d ".venv" ]; then
    python -m venv .venv
fi

source .venv/bin/activate

echo -e "${ORANGE}[*] Installing Python requirements...${RESET}"
pip install --upgrade pip

# Install core dependencies first (these usually have wheels or are pure python)
echo -e "${ORANGE}[*] Installing core dependencies...${RESET}"
pip install pyyaml requests python-telegram-bot ollama duckduckgo-search python-dotenv flask flask-cors waitress youtube-transcript-api beautifulsoup4 yt-dlp apscheduler psutil numpy

# Attempt to install scikit-learn separately
echo -e "${ORANGE}[*] Attempting to install scikit-learn (for Local RAG)...${RESET}"
echo -e "${AMBER}[!] Note: This may fail on some Android devices due to complex build requirements.${RESET}"
pip install scikit-learn || echo -e "${RED}[!] Skipping scikit-learn. Local RAG search will be disabled, but other features will work.${RESET}"

echo -e "${AMBER}[*] Starting Configuration Wizard...${RESET}"
python core/setup.py

echo -e "${ORANGE}================================================================${RESET}"
echo -e "${GREEN}[!] Setup Finished!${RESET}"
echo -e "${AMBER}[*] To run the agent, use: ./termux/run.sh${RESET}"
echo -e "${ORANGE}================================================================${RESET}"
