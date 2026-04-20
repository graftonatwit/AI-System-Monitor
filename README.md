# 🧠 AI System Dashboard (Raspberry Pi + Ollama)

A lightweight real-time system monitoring dashboard built with **Flask**, **psutil**, and **Ollama local LLMs**.  
Designed to run on a Raspberry Pi with optional AI HAT / local inference support.

---

## 🚀 Features

- 📊 Live hardware monitoring (CPU, RAM, Disk, Temperature)
- 🧠 AI system analysis using local LLM (Ollama)
- 🔄 Manual AI refresh (no background spam)
- 🧾 Structured AI output (status + analysis + advice)
- 🔊 Voice alerts (via `espeak`)
- ⚡ Lightweight and optimized for Raspberry Pi
- 🌙 Clean dark-mode dashboard UI

---

## 🧰 Requirements

### Hardware
- Raspberry Pi (recommended Pi 4 or Pi 5)
- Optional: AI HAT 2 / local inference accelerator

### Software
- Python 3.10+
- Ollama installed and running
- Linux (Raspberry Pi OS recommended)

---

## 📦 Install Dependencies

### System packages:
```bash
sudo apt update
sudo apt install python3-pip espeak -y
