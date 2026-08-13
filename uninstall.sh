#!/usr/bin/env bash
# ===============================================================================
# LarpLinux Supreme AI OS Companion — Uninstaller (uninstall.sh)
# ===============================================================================

set -euo pipefail

PINK="\033[38;2;245;169;184m"
CYAN="\033[38;2;91;206;250m"
GREEN="\033[38;2;166;227;161m"
YELLOW="\033[38;2;249;226;175m"
BOLD="\033[1m"
RESET="\033[0m"

echo -e "${PINK}${BOLD}Uninstalling LarpLinux Supreme AI Companion...${RESET}"

for BIN_PATH in "/usr/local/bin/larp" "/usr/bin/larp" "${HOME}/.local/bin/larp"; do
    if [ -f "$BIN_PATH" ]; then
        echo -e "${CYAN}Removing ${BIN_PATH}...${RESET}"
        if [ -w "$(dirname "$BIN_PATH")" ]; then
            rm -f "$BIN_PATH"
        else
            sudo rm -f "$BIN_PATH"
        fi
    fi
done

# Delete the marked block only. Deleting every line matching "alias lc=" and
# friends also removed shortcuts the user had defined themselves.
echo -e "${CYAN}Removing shortcut aliases...${RESET}"
for RC in "${HOME}/.bashrc" "${HOME}/.zshrc" "${HOME}/.config/fish/config.fish"; do
    if [ -f "$RC" ] && grep -qF "# --- LarpLinux Shortcuts ---" "$RC"; then
        cp "$RC" "${RC}.larp-backup"
        sed -i '/# --- LarpLinux Shortcuts ---/,/# --- End LarpLinux Shortcuts ---/d' "$RC"
        echo -e "${CYAN}  cleaned ${RC} (previous version saved as ${RC}.larp-backup)${RESET}"
    fi
done

# The configuration holds API keys and query history, so it is never removed
# without being asked for explicitly.
CONF_DIR="${HOME}/.config/larp"
if [ -d "$CONF_DIR" ]; then
    echo -e "${YELLOW}[!] Your configuration, API keys and backups are still in ${CONF_DIR}${RESET}"
    echo -e "${YELLOW}    Delete them with: rm -rf ${CONF_DIR}${RESET}"
fi

echo -e "${GREEN}[+] Larp has been successfully uninstalled.${RESET}\n"
