<div align="center">
  <h1>𒆙 VoidClaw</h1>
  <p><b>The Ultimate Evolutionary, Cross-Platform Autonomous AI Command Center</b></p>
  <p>
    <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python" />
    <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Mac%20%7C%20Linux%20%7C%20Android-orange.svg" alt="Platforms" />
    <img src="https://img.shields.io/badge/UI-Glassmorphism-purple.svg" alt="UI" />
    <img src="https://img.shields.io/badge/Control-Shizuku%20Integrated-green.svg" alt="Shizuku" />
  </p>
</div>

---

<img width="1672" height="941" alt="voidclaw " src="https://github.com/user-attachments/assets/f1275879-da03-4b29-be83-aac846e3aac2" />


## 📖 Overview

VoidClaw is a highly advanced, local-first AI agent framework. It acts as a continuous autonomous assistant that learns your preferences over time, interacts with your local filesystem, scrapes the web, and proactively manages your digital life. Designed for portability, it runs seamlessly on high-end PCs and Android phones alike, turning your device into an autonomous mission hub.

## 🌟 Major Highlights

*   **📱 Android System Control (Shizuku):** VoidClaw is now integrated with **Shizuku**. It can autonomously open apps, navigate your phone (Home/Back), adjust volume, and execute raw `adb shell` commands directly from your chat.
*   **⏰ 24/7 Proactive Autonomy:** Set reminders, briefings, or complex tasks in seconds or minutes. VoidClaw proactively "messages" you across all channels with sound notifications and unique UI transmissions when a task triggers.
*   **🧠 Evolutionary Memory:** Automatically deduces and records your preferences, workflows, and expertise in a permanent neural vault to adapt its personality and assistance to you.
*   **🌐 Tri-Channel Interface:** Seamlessly switch between a premium **Glassmorphism Web UI**, remote control via **Telegram**, or a high-resolution **Terminal Dashboard**. All channels are synchronized in real-time.

## 🛠️ Feature Breakdown

### 🤖 Autonomous Core
- **ReAct Reasoning:** Multi-step thinking loop with live "Thought" transparency.
- **Universal LLM Adapter:** Support for **Gemini 1.5, GPT-4o, Claude 3.5, Ollama (Local), NVIDIA NIM, and OpenRouter**.
- **Mission Dashboard:** Real-time monitoring of CPU, RAM, Token usage, and active autonomous tasks.

### 🧰 The Tool Arsenal
- **Android Control:** Launch apps (e.g., YouTube), simulate hardware buttons, and touch events via Shizuku.
- **Advanced Web Tools:** Multi-stage web scraper and search with a stealth fallback system for Termux.
- **Media Suite:** High-quality YouTube downloading (Video/Audio) and automatic media conversion.
- **File Intelligence:** Sandboxed filesystem access and **Local RAG Semantic Search** across your workspace documents.
- **Smart Scheduler:** Human-friendly reminder system ("remind me every 30s") and professional Cron support.

### 🖥️ Premium Web Command Center
- **Mobile-Responsive Design:** Fully optimized for Android browsers with a slide-out Mission Hub and floating input.
- **Operational Control:** Mid-response interruption (Stop Button) and secure document attachments.
- **Memory Vault:** Browse, search, and instantly restore previous neural logs from the sidebar.

---

## 🚀 Installation & Setup

VoidClaw is designed to be **100% portable**. 

### 📱 Android (Termux) - The Mobile Command Center

1.  **Install Termux:** Download [Termux from F-Droid](https://f-droid.org/en/packages/com.termux/).
2.  **Run the Quick Setup:**
    ```bash
    pkg update -y && pkg upgrade -y
    pkg install git -y
    git clone https://github.com/AbuZar-Ansarii/VoidClaw-Agent.git
    cd VoidClaw-Agent
    chmod +x termux/install.sh termux/run.sh
    ./termux/install.sh
    ```
3.  **Enable Android Control (Optional):**
    *   Set up [Shizuku](https://shizuku.rikka.app/) on your phone.
    *   In Termux, run: `curl -sL https://raw.githubusercontent.com/RikkaApps/Shizuku-API/master/rish/rish.sh > /data/data/com.termux/files/usr/bin/rish && chmod +x /data/data/com.termux/files/usr/bin/rish`
    *   Authorize Termux in the Shizuku app.

### 🪟 Windows Setup
1. Double-click `windows\install.bat` and follow the wizard.
2. Double-click `windows\run.bat` to launch.

### 🍎 macOS / 🐧 Linux Setup
1. Run: `chmod +x linux/install.sh linux/run.sh && ./linux/install.sh`
2. To launch: `./linux/run.sh`

---

## 🗂️ Project Structure

```text
voidclaw/
├── core/                   # Core Brain (Agent, Models, Tools)
├── common/                 # Neural Vault (Memory, Logs, Configs)
├── linux/ | mac/ | termux/ # Cross-Platform Launchers
├── windows/                # Windows Execution Suite
├── workspace/              # Secure File Sandbox
└── requirements.txt        # System Dependencies
```

---
<div align="center">
  <i>Conceptualized and Built by Mohd Abuzar</i><br>
  <b>VoidClaw: Autonomous. Evolutionary. Universal.</b>
</div>
