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
echo "           A U T O N O M O U S   C O M M A N D   C E N T E R"
echo ""
echo -e "${AMBER}           AI Agent for Windows, Mac, Android & Linux${RESET}"
echo -e "${ORANGE}================================================================${RESET}"

# Ensure we are in the root directory
cd "$(dirname "$0")/.."

# Fix for Rust/Maturin/LXML build errors
export ANDROID_API_LEVEL=24

echo -e "${ORANGE}[*] Updating system packages...${RESET}"
pkg update -y && pkg upgrade -y

echo -e "${ORANGE}[*] Setting up Termux User Repository (TUR)...${RESET}"
pkg install tur-repo -y

echo -e "${ORANGE}[*] Installing system dependencies (Rust, Clang & Build Headers)...${RESET}"
# Install compilers and heavy pre-built libraries
pkg install python git clang make rust binutils \
    libxml2 libxslt libjpeg-turbo libpng \
    python-psutil python-numpy python-cryptography python-lxml -y

echo -e "${ORANGE}[*] Setting up virtual environment...${RESET}"
# Create venv with system site packages to use pkg-installed heavy dependencies
if [ ! -d ".venv" ]; then
    python -m venv --system-site-packages .venv
fi

source .venv/bin/activate

echo -e "${ORANGE}[*] Upgrading pip and build tools...${RESET}"
pip install --upgrade pip setuptools wheel

# Install dependencies one by one to ensure failure of one doesn't stop others
# Note: httpx and pydantic will be installed via pip, but ANDROID_API_LEVEL fix will help
DEPS=("pyyaml" "requests" "python-telegram-bot" "ollama" "duckduckgo-search" "python-dotenv" "flask" "flask-cors" "waitress" "youtube-transcript-api" "beautifulsoup4" "yt-dlp" "apscheduler" "tzdata")

for dep in "${DEPS[@]}"; do
    echo -e "${ORANGE}[*] Installing $dep...${RESET}"
    # Use --prefer-binary to pull pre-built wheels wherever possible
    pip install "$dep" --prefer-binary || echo -e "${RED}[!] Failed to install $dep via pip. Continuing...${RESET}"
done

# Optional: Attempt scikit-learn
echo -e "${ORANGE}[*] Attempting scikit-learn (optional)...${RESET}"
echo -e "${AMBER}[!] This usually requires a very long time to build on Android. Skipping if it takes too long.${RESET}"
pip install scikit-learn --prefer-binary || echo -e "${RED}[!] Skipping scikit-learn. Local RAG will be disabled.${RESET}"

echo -e "${AMBER}[*] Starting Configuration Wizard...${RESET}"
python core/setup.py

echo -e "${ORANGE}================================================================${RESET}"
echo -e "${GREEN}[!] Setup Finished!${RESET}"
echo -e "${AMBER}[*] To run the agent, use: ./termux/run.sh${RESET}"
echo -e "${ORANGE}================================================================${RESET}"
