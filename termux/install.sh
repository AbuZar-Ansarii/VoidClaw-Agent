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

echo -e "${ORANGE}[*] Installing system dependencies...${RESET}"
# Install psutil via pkg to avoid build errors on Android
pkg install python git clang make python-psutil -y

echo -e "${ORANGE}[*] Setting up virtual environment...${RESET}"
# Create venv with system site packages so it can see pkg-installed psutil
if [ ! -d ".venv" ]; then
    python -m venv --system-site-packages .venv
fi

source .venv/bin/activate

echo -e "${ORANGE}[*] Installing Python requirements...${RESET}"
pip install --upgrade pip

# Install dependencies one by one to ensure failure of one doesn't stop others
DEPS=("pyyaml" "requests" "python-telegram-bot" "ollama" "duckduckgo-search" "python-dotenv" "flask" "flask-cors" "waitress" "youtube-transcript-api" "beautifulsoup4" "yt-dlp" "apscheduler" "numpy")

for dep in "${DEPS[@]}"; do
    echo -e "${ORANGE}[*] Installing $dep...${RESET}"
    pip install "$dep" || echo -e "${RED}[!] Failed to install $dep via pip. Checking system...${RESET}"
done

# Optional: Attempt scikit-learn
echo -e "${ORANGE}[*] Attempting scikit-learn (optional)...${RESET}"
pip install scikit-learn || echo -e "${RED}[!] Skipping scikit-learn. Local RAG will be disabled.${RESET}"

echo -e "${AMBER}[*] Starting Configuration Wizard...${RESET}"
python core/setup.py

echo -e "${ORANGE}================================================================${RESET}"
echo -e "${GREEN}[!] Setup Finished!${RESET}"
echo -e "${AMBER}[*] To run the agent, use: ./termux/run.sh${RESET}"
echo -e "${ORANGE}================================================================${RESET}"
