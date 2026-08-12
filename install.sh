#!/usr/bin/env bash
# ===============================================================================
# LarpLinux Supreme AI OS Companion — Automated Installer (install.sh)
# ===============================================================================

set -e

# Palette
PINK="\033[38;2;245;169;184m"
CYAN="\033[38;2;91;206;250m"
GREEN="\033[38;2;166;227;161m"
RED="\033[38;2;243;139;168m"
BOLD="\033[1m"
RESET="\033[0m"

echo -e "${PINK}${BOLD}"
echo "  ╭───╮    █░░ █▀█ █▀█ █▀█ █░░ ░▀█ █▄░█ █░█ █░█"
echo "  │   │    █▄▄ █▀█ █▀▄ █▀▀ █▄▄ █▄█ █░▀█ █▄█ ▄▀▄"
echo "  ╰───╯   ─── LarpLinux OS Supreme AI Companion Installer ───"
echo -e "${RESET}"

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[-] Error: Python 3 is required to run larp.${RESET}"
    exit 1
fi

PYTHON_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo -e "${CYAN}[+] Found Python ${PYTHON_VER}${RESET}"

# Determine installation directory
INSTALL_DIR="/usr/local/bin"
if [ ! -w "$INSTALL_DIR" ]; then
    INSTALL_DIR="/usr/bin"
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_BIN="${SCRIPT_DIR}/bin/larp"

if [ ! -f "$SOURCE_BIN" ]; then
    echo -e "${CYAN}[+] Downloading latest larp release...${RESET}"
    TMP_DIR=$(mktemp -d)
    curl -sSL "https://raw.githubusercontent.com/larplinux/larp/main/bin/larp" -o "${TMP_DIR}/larp"
    SOURCE_BIN="${TMP_DIR}/larp"
fi

echo -e "${CYAN}[+] Installing larp binary to ${INSTALL_DIR}/larp...${RESET}"
if [ -w "$INSTALL_DIR" ]; then
    cp "$SOURCE_BIN" "${INSTALL_DIR}/larp"
    chmod +x "${INSTALL_DIR}/larp"
else
    sudo cp "$SOURCE_BIN" "${INSTALL_DIR}/larp"
    sudo chmod +x "${INSTALL_DIR}/larp"
fi

# Initialize configuration
CONF_DIR="${HOME}/.config/larp"
mkdir -p "$CONF_DIR"

if [ ! -f "${CONF_DIR}/config.json" ]; then
    echo -e "${CYAN}[+] Initializing default configuration in ${CONF_DIR}...${RESET}"
    cat << 'EOF' > "${CONF_DIR}/config.json"
{
  "provider": "ollama",
  "web_search": true,
  "auto_fix": true,
  "ollama": {
    "url": "http://localhost:11434",
    "model": "mistral",
    "auto_start": true,
    "auto_stop": true,
    "keep_alive": 0
  },
  "gemini": {
    "api_key": "",
    "model": "auto"
  },
  "claude": {
    "api_key": "",
    "model": "claude-3-5-sonnet-20241022"
  },
  "openai": {
    "api_key": "",
    "model": "gpt-4o-mini"
  }
}
EOF
fi

# Optional shortcuts setup
BASHRC="${HOME}/.bashrc"
if [ -f "$BASHRC" ] && ! grep -q "alias l='larp'" "$BASHRC"; then
    echo -e "${CYAN}[+] Adding short terminal aliases (l, ld, lw, lc, lg, lf) to ~/.bashrc...${RESET}"
    cat << 'EOF' >> "$BASHRC"

# --- LarpLinux Shortcuts ---
alias l='larp'
alias ld='larp do'
alias lw='larp why'
alias lc='larp chat'
alias lg='larp get'
alias lf='larp fetch'
EOF
fi

echo -e "\n${GREEN}${BOLD}[+] LarpLinux Supreme AI Companion installed successfully!${RESET}"
echo -e "${CYAN}Run ${BOLD}'larp help'${RESET}${CYAN} or ${BOLD}'larp config'${RESET}${CYAN} to get started.${RESET}\n"
