<div align="center">
  
<!-- Main Logo -->
<img width="2167" height="406" alt="Voidclaw" src="https://github.com/user-attachments/assets/9dcf262a-956b-492b-a680-be1d01f3e8ae" />

<!-- Clean Title -->
<h1>
  <img src="https://readme-typing-svg.demolab.com?font=Inter&weight=600&size=36&duration=2000&pause=500&color=E8B81A&center=true&vCenter=true&width=550&height=60&lines=VOIDCLAW;AUTONOMOUS+AI+CORE;SELF+EVOLVING+AI+AGENT;FOR;WINDOWS;MAC;LINUX;ANDROID;BY;MOHD+ABUZAR" alt="Typing SVG" />
</h1>

<!-- Subtitle -->
<p align="center">
  <b>The Ultimate Evolutionary, Cross-Platform Autonomous AI Command Center</b>
</p>

<br/>

<!-- Professional Badges -->
<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-1a1a1a?style=flat-square&logo=python&logoColor=E8B81A&labelColor=0a0a0a" />
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Mac%20%7C%20Linux%20%7C%20Android-1a1a1a?style=flat-square&logo=matrix&logoColor=E8B81A&labelColor=0a0a0a" />
  <img src="https://img.shields.io/badge/UI-Glassmorphism-1a1a1a?style=flat-square&logo=figma&logoColor=E8B81A&labelColor=0a0a0a" />
  <img src="https://img.shields.io/badge/Control-Shizuku%20Integrated-1a1a1a?style=flat-square&logo=android&logoColor=E8B81A&labelColor=0a0a0a" />
</p>

<!-- Repository Stats -->

<p align="center">
  <img src="https://img.shields.io/github/stars/AbuZar-Ansarii/VoidClaw-Agent?style=flat-square&logo=github&labelColor=0a0a0a&color=E8B81A" />
  <img src="https://img.shields.io/github/forks/AbuZar-Ansarii/VoidClaw-Agent?style=flat-square&logo=github&labelColor=0a0a0a&color=E8B81A" />
  <img src="https://img.shields.io/github/license/AbuZar-Ansarii/VoidClaw-Agent?style=flat-square&labelColor=0a0a0a&color=E8B81A" />
</p>

<!-- Clean Divider -->
<hr width="60%">

</div>

## 📖 Overview

VoidClaw is a highly advanced, local-first AI agent framework. It acts as a continuous autonomous assistant that learns your preferences over time, interacts with your local filesystem, scrapes the web, and proactively manages your digital life. Designed for portability, it runs seamlessly on high-end PCs and Android phones alike, turning your device into an autonomous mission hub.

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

## ⚡ Lightweight & Mini-Requirements

VoidClaw is engineered to be **ultra-lightweight**. While it can harness the power of massive models, the core agent itself consumes minimal resources.

*   **Mini-Requirement:** Can run on a **$10-15 Raspberry Pi Zero 2 W or Pi 3/4/5** with as little as **512MB RAM** (when using Cloud APIs like Gemini or OpenRouter).
*   **Production Ready:** Efficiently manages background tasks without battery drain on mobile devices.

## 📋 System Requirements

| Platform | Minimum Requirements | Recommended |
| :--- | :--- | :--- |
| **Android** | Android 9+, 2GB RAM, Termux | Android 12+, 4GB RAM, Shizuku |
| **Windows** | Windows 10/11, Python 3.10+ | 8GB RAM (for local Ollama) |
| **Linux / Pi** | Debian/Ubuntu/Raspbian, 1GB RAM | Raspberry Pi 4/5 (4GB RAM) |
| **macOS** | macOS Monterey+, Intel/Apple Silicon | M1/M2/M3 Chip for local LLMs |

## 🛡️ Security & Privacy

*   **Local-First Architecture:** Your "Neural Vault" (memories, logs, and preferences) is stored **strictly on your device** in the `common/` folder. No data is ever sent to a central server.
*   **Workspace Sandboxing:** All filesystem tools are hardware-locked to the `workspace/` directory. The agent cannot modify system files outside this folder without explicit raw shell permission.
*   **Privacy by Design:** Zero telemetry. No tracking. No cloud-based logging. You own your data.
*   **Credential Safety:** API keys and tokens are stored locally in `common/config.yaml` and are never exposed in logs.

## 🌟 Major Highlights

*   **📱 Android System Control (Shizuku):** VoidClaw is now integrated with **Shizuku**. It can autonomously open apps, navigate your phone, toggle system settings (WiFi, Bluetooth, Dark Mode), simulate precision touch gestures (Tap, Swipe), and capture screenshots directly from your chat.
*   **⏰ 24/7 Proactive Autonomy:** Set reminders, briefings, or complex tasks in seconds or minutes. VoidClaw proactively "messages" you across all channels with sound notifications and unique UI transmissions when a task triggers.
*   **🧠 Evolutionary Memory:** Automatically deduces and records your preferences, workflows, and expertise in a permanent neural vault to adapt its personality and assistance to you.
*   **🌐 Tri-Channel Interface:** Seamlessly switch between a premium **Glassmorphism Web UI**, remote control via **Telegram**, or a high-resolution **Terminal Dashboard**. All channels are synchronized in real-time.

## 🛠️ Feature Breakdown

### 🤖 Autonomous Core
- **ReAct Reasoning:** Multi-step thinking loop with live "Thought" transparency.
- **Universal LLM Adapter:** Support for **Gemini 1.5, GPT-4o, Claude 3.5, Ollama (Local), NVIDIA NIM, and OpenRouter**.
- **Mission Dashboard:** Real-time monitoring of CPU, RAM, Token usage, and active autonomous tasks.

### 🧰 The Tool Arsenal
- **Advanced Android Control:** Toggle WiFi, Bluetooth, Dark Mode, and Battery Saver. Capture screenshots, simulate precision tap/swipe gestures, and type text autonomously via Shizuku.
- **Advanced Web Tools:** Multi-stage web scraper and search with a stealth fallback system for Termux.
- **Media Suite:** High-quality YouTube downloading (Video/Audio) and automatic media conversion.
- **File Intelligence:** Sandboxed filesystem access and **Local RAG Semantic Search** across your workspace documents.
- **Smart Scheduler:** Human-friendly reminder system ("remind me every 30s") and professional Cron support.

### 🖥️ Premium Web Command Center
- **Smart Connectivity:** Automatically detects and resolves port conflicts (e.g., macOS AirPlay conflict) by finding the next available port.
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
3.  **Enable Android Control (Zero-Config Shizuku Setup):**
    VoidClaw now features **Auto-Provisioning** for Shizuku. No manual file moving required!

    *   **Step A: Install Shizuku**
        Download and install the [Shizuku App](https://shizuku.rikka.app/download/) on your phone.
    *   **Step B: Start Shizuku Service**
        Open the Shizuku app and start the service (usually via **Wireless Debugging** in Android Developer Options).
    *   **Step C: Export & Grant Permission**
        1.  In Shizuku app, tap **"Use Shizuku in terminal apps"** -> **"Export files"**.
        2.  Save them into a folder named **"Shizuku"** in your phone's Internal Storage.
        3.  In Termux, run: `termux-setup-storage` and grant permission.
    *   **Step D: Launch VoidClaw**
        Start the agent in Termux: `./termux/run.sh`.
        The agent will detect the files and show: `[SYSTEM] Shizuku environment provisioned successfully.`

    *   **Step E: Manual Verification (Optional)**
        Exit the agent and type `rish` in Termux. If it shows a shell prompt (`$`), you are ready! Type `exit` to return.
        *(Note: Termux does NOT need to be toggled in 'Authorized applications' when using this method)*

### 🪟 Windows Setup
1. Clone Repo: `git clone https://github.com/AbuZar-Ansarii/VoidClaw-Agent.git`
2. Double-click `windows\install.bat` and follow the wizard.
3. Double-click `windows\run.bat` to launch.

### 🍎 macOS / 🐧 Linux Setup
1. Clone Repo: `git clone https://github.com/AbuZar-Ansarii/VoidClaw-Agent.git`
2. cd `VoidClaw-Agent`
3. Based on System(Mac/Linux) Run: `chmod +x linux/install.sh linux/run.sh && ./linux/install.sh`.                                                             `chmod +x mac/install.sh mac/run.sh && ./mac/install.sh`
4. Based on System(Mac/Linux) To launch: `./linux/run.sh` `./mac/run.sh`

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
<div align="center">
  <i>Conceptualized and Built by Mohd Abuzar</i><br>
  <b>VoidClaw: Autonomous. Evolutionary. Universal.</b>
</div>
