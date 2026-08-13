# 🌸 LarpLinux Supreme AI Companion (`larp`)

> **Next-Generation Autonomous AI Companion, Hands-Free Voice Assistant, and System Automation Engine for any Linux distribution.**

[![License: MIT](https://img.shields.io/badge/License-MIT-f5a9b8.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/Python-3.8%2B-5bcefa.svg)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Linux%20(Arch%20%7C%20Void%20%7C%20Debian%20%7C%20Fedora%20%7C%20Alpine)-purple.svg)]()
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Standard%20Library%20Only-green.svg)]()

```text
  ╭───╮    █░░ █▀█ █▀█ █▀█ █░░ ░▀█ █▄░█ █░█ █░█
  │   │    █▄▄ █▀█ █▀▄ █▀▀ █▄▄ █▄█ █░▀█ █▄█ ▄▀▄
  ╰───╯   ─── LarpLinux OS Supreme AI Companion v4.1.0 ───
```

---

## ✨ Key Features

- **🌸 Zero Dependencies**: Built strictly using standard Python 3.8+ libraries (`urllib`, `json`, `subprocess`, `sys`, `math`, `shlex`). No `pip install` required!
- **🎙️ Hands-Free Full-Console Voice Assistant (`larp talk`)**: Interactive voice session with VAD silence auto-stop (1.1s), live mic level meter, and a **Full-Console 2D Cyberpunk Studio HUD visualizer canvas** filling all terminal rows and columns.
- **🗣️ High-Quality Neural TTS & Audio Mastering**: Supports **RHVoice** (offline natural Russian voices: Elena, Aleksandr), **OpenAI Neural Speech API** (`nova`, `shimmer`, `alloy`), **Piper Neural TTS**, and **Google Translate TTS** with FFmpeg vocal mastering filters (`atempo`, highpass/lowpass, volume compressor).
- **🧠 Multilingual STT with Auto-Language Detection**: Local offline **Whisper** module (`tiny`, `base`, `small`, `medium`) with 99+ language auto-detection and fallback to Groq/OpenAI Whisper API.
- **📦 Multi-Distro Voice Auto-Installer**: 1-click voice wizard (`larp voice setup`) with package manager detection across **Arch Linux** (`pacman`), **Void Linux** (`xbps`), **Debian/Ubuntu** (`apt`), **Fedora** (`dnf`), **Alpine** (`apk`), **Solus** (`eopkg`), **openSUSE** (`zypper`), and **Gentoo** (`emerge`).
- **🤖 Universal AI Engine**: Native support for **Ollama** (local VRAM-saver engine with `keep_alive: 0`), **OpenRouter** (one API key for ~400 models — Claude, Gemini, GPT, Llama and more), **Google Gemini API** (with dynamic model auto-discovery), **Anthropic Claude API**, and **OpenAI ChatGPT API**.
- **⚡ Integrated OS Modules**: Includes terminal copilot (`larp do`), log auto-repair engine (`larp fix`), system informer (`larp fetch`), benchmark (`larp bench`), translator (`larp translate`), cleanup wizard (`larp clean`), and package architect (`larp get-create`).
- **💬 Live Streaming Answers**: `larp why`, `larp chat`, `larp code` and `larp translate` print the answer as the model writes it, so a slow local model shows progress instead of a spinner.
- **🌸 Truecolor Glassmorphic UI**: Truecolor pastel-pink (`#F5A9B8`) and cyan (`#5BCEFA`) console palette with clean borders and emoji-free ASCII kaomoji aesthetics.
- **🛡️ Terminal Kaomoji Persona**: Cute, enthusiastic AI companion persona (`(^--^)`, `(=^.^=)`, `\(^o^)/`) configured with safe console ASCII kaomoji that render cleanly in any Linux terminal without broken font boxes.
- **🛠️ Auto-Repair Engine**: Scans system logs (`journalctl -p 3`), synthesizes exact root causes, and proposes a single-line resolution pipeline.

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

## 🛠️ Module Overview

| Command | Description |
|---|---|
| `larp talk` | Full-Console 2D Studio TUI Voice Assistant session (hands-free mic & speaker) |
| `larp listen [sec]` | Single voice query recorder and AI voice responder |
| `larp speak <text>` | Synthesize and play text audio with real-time speech visualizer |
| `larp voice` | Voice Assistant diagnostic dashboard & setup wizard |
| `larp voice setup` | Multi-distro interactive Voice Engine installer (RHVoice, Piper, OpenAI) |
| `larp voice test` | Interactive 4-step diagnostic test (mic, playback, STT, TTS) |
| `larp fetch` | Aesthetic system informer (Larp Neofetch replacement) |
| `larp do <task>` | Autonomous AI terminal copilot — translates tasks into shell pipelines |
| `larp code <task>` | AI Code and script generator with syntax block formatting |
| `larp translate <text>` | Instant AI multilingual translator (RU ↔ EN) |
| `larp config` | Categorized Master Control Center TUI Hub settings menu |
| `larp config models [text]` | Browse OpenRouter model IDs, optionally filtered |
| `larp fallback` | Manage the provider fallback chain (add / remove / clear) |
| `larp clean` | Disk cleanup wizard — package cache, logs & orphans (any package manager) |
| `larp backup` | Snapshot & config backup manager (`~/.config/larp`, `niri`, `fwm`, `waybar`, `kitty`) |
| `larp restore [archive]` | Restore configuration from a backup archive |
| `larp alias` | Installs short terminal shortcuts (`l`, `ld`, `lw`, `lc`, `lg`, `lf`) into shell rc |
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
| `larp version` | Print the installed larp version |

---

## 🎙️ Voice Assistant Subsystem

`larp` comes equipped with a complete hands-free Voice Assistant capable of running offline locally or in the cloud:

```bash
larp talk                      # Start interactive voice session with full-console 2D HUD
larp speak "Привет! Как дела?" # Speech output with real-time waveform visualizer
larp voice setup               # Auto-install RHVoice, Piper or configure OpenAI / Groq keys
larp voice test                # Full audio & speech recognition hardware diagnostic test
```

### What a voice session may run on its own

A spoken command is reconstructed from a speech transcript and a model's guess
at what you meant, so `larp talk` does not hand arbitrary commands to the shell:

- **Runs immediately** — launching a desktop application (`открой телеграм`,
  `запусти браузер`). These open a window and change nothing about the system.
- **Asks first** — anything else: `sudo`, package installs, file operations, or
  a command using pipes, redirections or substitutions. The command is printed
  in full and needs a `y` before it runs.
- **Refused outright** — shutdown, reboot, and the destructive patterns
  (`rm -rf /`, `mkfs`, raw writes to block devices).

### Supported Voice Engines (TTS)
- **RHVoice (Elena / Aleksandr)**: High-quality natural offline Russian speech synthesizer (`sudo pacman -S rhvoice rhvoice-voice-elena` / `sudo xbps-install -Sy RHVoice`).
- **OpenAI Neural Speech (`nova` / `shimmer` / `alloy`)**: Studio-quality human voice synthesis.
- **Piper Neural TTS**: Lightweight local neural voice engine.
- **Google Neural TTS**: Mastered with FFmpeg tempo, EQ, and dynamic volume compression filters.

---

## ⚙️ Configuration & Master Control Hub

Launch the categorized TUI Master Control Center:

```bash
larp config
```

Or set options directly via command line:

```bash
larp config set provider gemini
larp config set voice.tts_engine rhvoice
larp config set voice.rhvoice_voice Elena
larp config set auto_fix true
```

---

## 🧪 Running the tests

The suite uses only the standard library, like larp itself — no pytest, no `pip install`:

```bash
python3 -m unittest discover -s tests -v
```

CI runs the same suite on Python 3.8, 3.11 and 3.13, lints the installer scripts with `shellcheck`, and smoke-tests all commands.

---

## 📄 License

Distributed under the **MIT License**. See [LICENSE](LICENSE) for details.
