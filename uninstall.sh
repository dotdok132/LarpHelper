#!/usr/bin/env bash
# ===============================================================================
# LarpLinux Supreme AI OS Companion — Uninstaller (uninstall.sh)
# ===============================================================================

set -e

PINK="\033[38;2;245;169;184m"
CYAN="\033[38;2;91;206;250m"
GREEN="\033[38;2;166;227;161m"
BOLD="\033[1m"
RESET="\033[0m"

echo -e "${PINK}${BOLD}Uninstalling LarpLinux Supreme AI Companion...${RESET}"

if [ -f "/usr/local/bin/larp" ]; then
    sudo rm -f "/usr/local/bin/larp"
fi

if [ -f "/usr/bin/larp" ]; then
    sudo rm -f "/usr/bin/larp"
fi

echo -e "${CYAN}Removing shortcut aliases from ~/.bashrc...${RESET}"
if [ -f "${HOME}/.bashrc" ]; then
    sed -i '/# --- LarpLinux Shortcuts ---/d' "${HOME}/.bashrc"
    sed -i '/alias l=/d' "${HOME}/.bashrc"
    sed -i '/alias ld=/d' "${HOME}/.bashrc"
    sed -i '/alias lw=/d' "${HOME}/.bashrc"
    sed -i '/alias lc=/d' "${HOME}/.bashrc"
    sed -i '/alias lg=/d' "${HOME}/.bashrc"
    sed -i '/alias lf=/d' "${HOME}/.bashrc"
fi

echo -e "${GREEN}[+] Larp has been successfully uninstalled.${RESET}\n"
