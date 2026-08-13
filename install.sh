#!/usr/bin/env bash
# ===============================================================================
# LarpLinux Supreme AI OS Companion — Automated Installer (install.sh)
# ===============================================================================

set -euo pipefail

# Palette
PINK="\033[38;2;245;169;184m"
CYAN="\033[38;2;91;206;250m"
GREEN="\033[38;2;166;227;161m"
YELLOW="\033[38;2;249;226;175m"
RED="\033[38;2;243;139;168m"
BOLD="\033[1m"
RESET="\033[0m"

echo -e "${PINK}${BOLD}"
echo "  ╭───╮    █░░ █▀█ █▀█ █▀█ █░░ ░▀█ █▄░█ █░█ █░█"
echo "  │   │    █▄▄ █▀█ █▀▄ █▀▀ █▄▄ █▄█ █░▀█ █▄█ ▄▀▄"
echo "  ╰───╯   ─── LarpLinux OS Supreme AI Companion Installer ───"
echo -e "${RESET}"

# Check Python 3.8+
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[-] Error: Python 3.8+ is required to run larp.${RESET}"
    exit 1
fi

if ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)'; then
    echo -e "${RED}[-] Error: Python 3.8+ is required, found $(python3 -V).${RESET}"
    exit 1
fi
echo -e "${CYAN}[+] Found $(python3 -V)${RESET}"

# Determine installation directory.
#
# /usr/local/bin is the correct destination for locally installed software and
# is almost never writable without sudo — testing writability and silently
# falling back to /usr/bin used to drop the binary into the directory the
# distribution's package manager owns.
if [ -n "${PREFIX:-}" ]; then
    INSTALL_DIR="${PREFIX}/bin"
elif [ "$(id -u)" -eq 0 ] || command -v sudo &> /dev/null; then
    INSTALL_DIR="/usr/local/bin"
else
    INSTALL_DIR="${HOME}/.local/bin"
    echo -e "${YELLOW}[!] No sudo available — installing to ${INSTALL_DIR}.${RESET}"
fi

# When the script is piped (`curl -sSL ... | bash`) there is no local checkout
# and BASH_SOURCE is unset — which `set -u` turns into a fatal error, so this
# has to be resolved defensively rather than inline.
SCRIPT_DIR=""
if [ -n "${BASH_SOURCE[0]:-}" ] && [ -f "${BASH_SOURCE[0]}" ]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi

SOURCE_BIN=""
if [ -n "$SCRIPT_DIR" ] && [ -f "${SCRIPT_DIR}/bin/larp" ]; then
    SOURCE_BIN="${SCRIPT_DIR}/bin/larp"
fi
TMP_DIR=""

if [ -z "$SOURCE_BIN" ]; then
    echo -e "${CYAN}[+] Downloading latest larp release...${RESET}"
    TMP_DIR=$(mktemp -d)
    trap 'rm -rf "$TMP_DIR"' EXIT
    if ! curl -fsSL "https://raw.githubusercontent.com/dotdok132/LarpHelper/main/bin/larp" -o "${TMP_DIR}/larp"; then
        echo -e "${RED}[-] Download failed. Check your internet connection.${RESET}"
        exit 1
    fi
    SOURCE_BIN="${TMP_DIR}/larp"
fi

# A truncated download is worse than no install: it would be run as a shell
# helper that generates commands.
if ! python3 -c "import ast,sys; ast.parse(open(sys.argv[1]).read())" "$SOURCE_BIN"; then
    echo -e "${RED}[-] The downloaded larp script is not valid Python — aborting.${RESET}"
    exit 1
fi

echo -e "${CYAN}[+] Installing larp to ${INSTALL_DIR}/larp...${RESET}"
if [ -w "$INSTALL_DIR" ] || { mkdir -p "$INSTALL_DIR" 2>/dev/null && [ -w "$INSTALL_DIR" ]; }; then
    install -m 755 "$SOURCE_BIN" "${INSTALL_DIR}/larp"
else
    sudo install -d -m 755 "$INSTALL_DIR"
    sudo install -m 755 "$SOURCE_BIN" "${INSTALL_DIR}/larp"
fi

# The configuration is created by larp itself on first use, from a single
# in-code default. Writing a second copy here only let the two drift apart.
CONF_DIR="${HOME}/.config/larp"
mkdir -p "$CONF_DIR"
chmod 700 "$CONF_DIR"

# Optional shortcuts setup
ALIAS_MARKER="# --- LarpLinux Shortcuts ---"
BASHRC="${HOME}/.bashrc"
if [ -f "$BASHRC" ] && ! grep -qF "$ALIAS_MARKER" "$BASHRC"; then
    echo -e "${CYAN}[+] Adding short terminal aliases (l, ld, lw, lc, lg, lf) to ~/.bashrc...${RESET}"
    cat << 'EOF' >> "$BASHRC"

# --- LarpLinux Shortcuts ---
alias l='larp'
alias ld='larp do'
alias lw='larp why'
alias lc='larp chat'
alias lg='larp get'
alias lf='larp fetch'
# --- End LarpLinux Shortcuts ---
EOF
fi

case ":${PATH}:" in
    *":${INSTALL_DIR}:"*) ;;
    *) echo -e "${YELLOW}[!] ${INSTALL_DIR} is not in your PATH — add it to use 'larp' directly.${RESET}" ;;
esac

echo -e "\n${GREEN}${BOLD}[+] LarpLinux Supreme AI Companion installed successfully!${RESET}"
echo -e "${CYAN}Run ${BOLD}'larp help'${RESET}${CYAN} or ${BOLD}'larp config'${RESET}${CYAN} to get started.${RESET}\n"
