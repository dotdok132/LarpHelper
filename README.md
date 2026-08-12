# 🌸 LarpLinux Supreme AI Companion (`larp`)

> **Next-Generation Autonomous AI Companion and System Automation Engine for Arch-based Linux Distributions.**

[![License: MIT](https://img.shields.io/badge/License-MIT-f5a9b8.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/Python-3.8%2B-5bcefa.svg)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Arch%20Linux%20%7C%20LarpLinux-purple.svg)]()
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Standard%20Library%20Only-green.svg)]()

```text
  ╭───╮    █░░ █▀█ █▀█ █▀█ █░░ ░▀█ █▄░█ █░█ █░█
  │   │    █▄▄ █▀█ █▀▄ █▀▀ █▄▄ █▄█ █░▀█ █▄█ ▄▀▄
  ╰───╯   ─── LarpLinux OS Supreme AI Companion v4.0 ───
```

---

## ✨ Key Features

- **🌸 Zero Dependencies**: Built strictly using standard Python 3.8+ libraries (`urllib`, `json`, `subprocess`, `sys`). No `pip install` required!
- **🤖 Universal AI Engine**: Native support for **Ollama** (local VRAM-saver engine with `keep_alive: 0`), **OpenRouter** (one API key for ~400 models — Claude, Gemini, GPT, Llama and more), **Google Gemini API** (with dynamic model auto-discovery), **Anthropic Claude API**, and **OpenAI ChatGPT API**.
- **⚡ 19 Integrated OS Modules**: Includes terminal copilot (`larp do`), log auto-repair engine (`larp fix`), system informer (`larp fetch`), benchmark (`larp bench`), translator (`larp translate`), cleanup wizard (`larp clean`), and package architect (`larp get-create`).
- **🌸 Truecolor Glassmorphic UI**: Truecolor pastel-pink (`#F5A9B8`) and cyan (`#5BCEFA`) console palette with clean borders and emoji-free aesthetics.
- **🛡️ Terminal Kaomoji Persona**: Cute, enthusiastic AI companion persona (`(^--^)`, `(=^.^=)`, `\(^o^)/`) configured with safe console ASCII kaomoji that render cleanly in any Linux terminal without broken font boxes.
- **🛠️ Auto-Repair Engine**: Scans system logs (`journalctl -p 3`), synthesizes exact root causes, and executes verified single-line resolution pipelines with quote-balancing protection.

---

## 🚀 Quick Installation

Run the automated one-line installer:

```bash
curl -sSL https://raw.githubusercontent.com/dotdok132/LarpHelper/main/install.sh | bash
```

Or clone the repository and run locally:

```bash
git clone https://github.com/dotdok132/LarpHelper.git
cd LarpHelper
chmod +x install.sh
./install.sh
```

---

## 🛠️ Module Overview (19 Modules)

| Command | Description |
|---|---|
| `larp fetch` | Aesthetic system informer (Larp Neofetch replacement) |
| `larp do <task>` | Autonomous AI terminal copilot — translates tasks into shell pipelines |
| `larp code <task>` | AI Code and script generator with syntax block formatting |
| `larp translate <text>` | Instant AI multilingual translator (RU ↔ EN) |
| `larp config` | Interactive step-by-step TUI settings menu |
| `larp config models [text]` | Browse OpenRouter model IDs, optionally filtered |
| `larp clean` | Disk cleanup wizard — pacman cache, journalctl logs & orphans |
| `larp backup` | Snapshot & config backup manager (`~/.config/larp`, `niri`, `fwm`, `waybar`) |
| `larp alias` | Installs short terminal shortcuts (`l`, `ld`, `lw`, `lc`, `lg`, `lf`) into `~/.bashrc` |
| `larp bench` | Speedtest and latency benchmark for all AI providers |
| `larp status` | Real-time system radar — CPU/RAM/Disk loads & active AI engine |
| `larp monitor` | Interactive real-time system monitoring dashboard |
| `larp history` | View recent prompt history and AI responses |
| `larp chat` | Terminal interactive conversation session with Larp AI |
| `larp why <query>` | Deep query solver using AI + DuckDuckGo + Arch DB API Search |
| `larp fix` | System log error diagnoser with 1-click Auto-Repair Engine |
| `larp get <pack>` | Install software pack or recipe from Larp-Repo |
| `larp get-list` | Registry table of available software recipes |
| `larp get-create <task>` | AI Pack Architect with live Arch/AUR package validation |
| `larp help` | Display complete command reference |

---

## ⚙️ Configuration & TUI

Launch the interactive configuration menu:

```bash
larp config
```

Or set options directly via command line:

```bash
larp config set provider gemini
larp config set gemini.api_key "YOUR_GEMINI_API_KEY"
larp config set auto_fix true
```

### Using OpenRouter

OpenRouter gives you Claude, Gemini, GPT, Llama and ~400 other models through a
single API key, so you don't need to register with each provider separately:

```bash
larp config set provider openrouter
larp config set openrouter.api_key "YOUR_OPENROUTER_KEY"
```

Model IDs are namespaced (`anthropic/claude-sonnet-5`, `google/gemini-2.5-flash`,
`meta-llama/llama-3.3-70b-instruct`). Browse and filter the list, then pick one:

```bash
larp config models              # every available model
larp config models gemini       # only models matching "gemini"
larp config set openrouter.model google/gemini-2.5-flash
```

Get a key at [openrouter.ai/keys](https://openrouter.ai/keys). The default model is
`anthropic/claude-sonnet-5`.

---

## 📄 License

Distributed under the **MIT License**. See [LICENSE](LICENSE) for details.
