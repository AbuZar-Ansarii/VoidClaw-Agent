#!/data/data/com.termux/files/usr/bin/bash

# VoidClaw Termux Installer
# Optimized for Android

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

clear
echo -e "${CYAN}================================================================${NC}"
echo -e "${YELLOW}               VOIDCLAW ANDROID (TERMUX) SETUP                  ${NC}"
echo -e "${CYAN}================================================================${NC}"

# 1. System Update & Dependencies
echo -e "${BLUE}[*] Updating system packages...${NC}"
pkg update -y && pkg upgrade -y
pkg install -y x11-repo tur-repo
pkg update -y

echo -e "${BLUE}[*] Installing dependencies (Python, Git, Build Tools, Math Libs)...${NC}"
pkg install -y python git clang libyaml make cmake openblas ninja rust ffmpeg libxml2 libxslt libjpeg-turbo libpng
# Optional but recommended for faster installs on termux:
pkg install -y python-numpy python-lxml || echo "python-lxml not found, will compile via pip"
pkg install -y python-scikit-learn || echo "python-scikit-learn not found, will compile via pip"
pkg install -y python-pyyaml || pkg install -y python-yaml || echo "python-yaml not found, will compile via pip"

# 2. Virtual Environment
echo -e "${BLUE}[*] Setting up Python virtual environment...${NC}"
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

if [ ! -d ".venv" ]; then
    python -m venv --system-site-packages .venv
fi
source .venv/bin/activate

echo -e "${BLUE}[*] Installing/Updating pip...${NC}"
pip install --upgrade pip

echo -e "${BLUE}[*] Installing project requirements...${NC}"
# Termux sometimes needs help with certain packages
pip install wheel
# Filter requirements.txt to skip pre-installed system packages on Termux
grep -vE "numpy|scikit-learn|pyyaml|yaml|lxml" requirements.txt > termux_reqs.txt
pip install -r termux_reqs.txt
rm termux_reqs.txt

# 3. Configuration Wizard
echo -e "\n${GREEN}[+] Installation complete!${NC}"
echo -e "${YELLOW}[*] Launching Configuration Wizard...${NC}"
python core/setup.py

echo -e "\n${CYAN}================================================================${NC}"
echo -e "${GREEN}[!] Setup Finished!${NC}"
echo -e "${YELLOW}[*] To run the agent, use: ./termux/run.sh${NC}"
echo -e "${CYAN}================================================================${NC}"
