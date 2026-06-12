<div align="center">
  <h1>𒆙 VoidClaw</h1>
  <p><b>An Evolutionary, Cross-Platform Autonomous AI Agent</b></p>
  <p>
    <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python" />
    <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Mac%20%7C%20Linux%20%7C%20Android-orange.svg" alt="Platforms" />
    <img src="https://img.shields.io/badge/UI-Glassmorphism-purple.svg" alt="UI" />
  </p>
</div>

---

## 📖 Overview

VoidClaw is a highly advanced, local-first AI agent framework. It acts as a continuous autonomous assistant that learns your preferences over time, interacts with your local filesystem, scrapes the web, and communicates with you via a premium Web UI, Telegram, or the Terminal.

## 🗂️ Project Structure

```text
voidclaw/
├── core/                   # Core agent logic and routing
│   ├── agent.py            # Main reasoning loop & ReAct logic
│   ├── models.py           # Universal LLM adapters
│   ├── server.py           # Waitress/Flask production web server
│   ├── setup.py            # Interactive CLI configuration wizard
│   ├── tools.py            # Autonomous tool implementations
│   └── web/                
│       └── index.html      # Premium Glassmorphism Frontend
├── common/                 # Configurations & Memory
│   ├── chats/              # Local chat history archives
│   ├── config.yaml         # API keys & model selections
│   ├── memory.md           # Agent's general memory store
│   └── user.md             # Evolutionary user profile
├── linux/                  # Linux launchers (.sh)
├── mac/                    # macOS launchers (.sh)
├── termux/                 # Android Termux scripts
├── windows/                # Windows launchers (.bat)
├── workspace/              # Sandboxed area for file/media operations
└── requirements.txt        # Python dependencies
```

## 🌟 Key Features

*   **🧠 Evolutionary Memory:** VoidClaw automatically deduces your preferences, workflows, and expertise, saving them to its permanent `user.md` memory vault to adapt its personality to you.
*   **🌐 Tri-Channel Interface:** Chat with the agent via a high-end Glassmorphism **Web UI**, remotely via **Telegram**, or directly in the **Terminal**. All channels are synced in real-time.
*   **🔌 Universal LLM Support:** Easily switch between top-tier models from **Google (Gemini), OpenAI, Claude (Anthropic), Ollama (Local), NVIDIA NIM, and OpenRouter**.
*   **🛠️ Robust Tool Arsenal:** Includes a Python Sandbox, Local RAG Semantic Search, Media Downloader (YT-DLP), Web Scraper, and more.

---

## 🚀 Installation & Setup

VoidClaw is designed to be **100% portable**. 

### 📱 Android (Termux) - Easy Setup Guide

Turn your Android phone into an autonomous AI Command Center!

1.  **Install Termux:** Download and install [Termux from F-Droid](https://f-droid.org/en/packages/com.termux/) (Do not use the Google Play Store version, it is deprecated).
2.  **Open Termux and run the following commands one by one:**
    ```bash
    # Step 1: Update packages and install git
    pkg update -y && pkg upgrade -y
    pkg install git -y

    # Step 2: Clone the VoidClaw repository
    git clone https://github.com/AbuZar-Ansarii/VoidClaw-Agent.git
    cd VoidClaw-Agent

    # Step 3: Make the installer executable and run it
    chmod +x termux/install.sh termux/run.sh
    ./termux/install.sh
    ```
3.  **Configure:** The installer will launch a beautiful Orange Setup Wizard. Follow the prompts to select your LLM provider and paste your API key.
4.  **Run:** To start the agent at any time, just open Termux and type:
    ```bash
    cd VoidClaw-Agent
    ./termux/run.sh
    ```

### 🪟 Windows Setup
1. Clone the repository.
2. Double-click `windows\install.bat`.
3. Follow the Configuration Wizard.
4. Double-click `windows\run.bat` to launch the agent.

### 🍎 macOS & 🐧 Linux Setup
```bash
git clone https://github.com/AbuZar-Ansarii/VoidClaw-Agent.git
cd VoidClaw-Agent
chmod +x linux/install.sh linux/run.sh
./linux/install.sh

# To start the agent:
./linux/run.sh
```

---

## 🖥️ The Web Command Center

When you launch VoidClaw, a production-grade Web Server starts automatically. Your browser will open the Web UI (`http://localhost:5000`).

*   **Deep Space Dark Mode:** A stunning UI with orange/amber accents.
*   **Real-Time Streaming:** Responses stream word-by-word with live "Thinking" indicators.
*   **Settings Modal:** Tweak the agent's creativity (Temperature) and System Prompt on the fly.
*   **Memory Vault:** Browse and instantly restore previous chat sessions from the sidebar.

---
<div align="center">
  <i>Conceptualized and Built by Mohd Abuzar</i>
</div>
