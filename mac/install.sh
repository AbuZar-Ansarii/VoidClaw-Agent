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

echo -e "${ORANGE}[*] Checking Python installation...${RESET}"
if ! command -v python3 &> /dev/null
then
    echo -e "${RED}[!] Python3 could not be found. Please install it.${RESET}"
    exit 1
fi

echo -e "${ORANGE}[*] Setting up virtual environment...${RESET}"
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate

echo -e "${ORANGE}[*] Installing dependencies...${RESET}"
pip install --upgrade pip

# Install core dependencies
pip install pyyaml requests python-telegram-bot ollama duckduckgo-search python-dotenv flask flask-cors waitress youtube-transcript-api beautifulsoup4 yt-dlp apscheduler psutil numpy

# Install scikit-learn (can be heavy)
pip install scikit-learn || echo -e "${RED}[!] Failed to install scikit-learn. Local RAG search will be disabled.${RESET}"

echo -e "${AMBER}[*] Starting Configuration Wizard...${RESET}"
python3 core/setup.py

echo -e "${ORANGE}================================================================${RESET}"
echo -e "${GREEN}[!] Setup Finished!${RESET}"
echo -e "${AMBER}[*] To run the agent, use: ./mac/run.sh${RESET}"
echo -e "${ORANGE}================================================================${RESET}"
