import os
import yaml
import sys

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_input(prompt, default=None):
    if default:
        val = input(f"{prompt} [{default}]: ").strip()
        return val if val else default
    return input(f"{prompt}: ").strip()

def run_setup():
    # Colors (Orange/Amber theme)
    ORANGE = '\033[38;5;214m'
    AMBER = '\033[93m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    WHITE = '\033[97m'
    RESET = '\033[0m'

    registry = {
        "1": {
            "name": "Google (Gemini)",
            "key": "gemini",
            "models": ["gemini-3.1-pro-preview", "gemini-3.1-flash-lite", "gemini-3.5-flash", "gemini-3-flash-preview", "gemini-2.5-flash", "gemini-2.5-flash-lite"]
        },
        "2": {
            "name": "OpenAI",
            "key": "openai",
            "models": ["gpt-5.5", "gpt-5.4", "gpt-5.4-mini", "GPT-4o", "GPT-4o-mini", "gpt-3.5-turbo", "gpt-oss-120b"]
        },
        "3": {
            "name": "Claude (Anthropic)",
            "key": "anthropic",
            "models": ["claude-fable-5", "claude-mythos-5", "claude-sonnet-4-6", "claude-opus-4-6", "claude-opus-4-7", "claude-opus-4-8"]
        },
        "4": {
            "name": "Ollama (Local/Cloud)",
            "key": "ollama",
            "models": ["gemini-3-flash-preview:cloud", "minimax-m3:cloud", "gemma4:31b-cloud", "glm-4.7:cloud", "lfm2.5", "nemotron-3-ultra:cloud", "gemma4", "qwen3.5", "qwen3.6", "qwen2.5", "qwen2.5:1.5b", "qwen2.5:3b"]
        },
        "5": {
            "name": "NVIDIA NIM",
            "key": "nvidia",
            "models": ["meta/llama3-70b-instruct", "nvidia/nemotron-4-340b-instruct", "mistralai/mixtral-8x22b-instruct"]
        },
        "6": {
            "name": "OpenRouter",
            "key": "openrouter",
            "models": ["meta-llama/llama-3-70b-instruct:free", "mistralai/mistral-7b-instruct:free", "microsoft/phi-3-medium-128k-instruct:free", "google/gemma-2-27b-it", "deepseek/deepseek-chat"]
        }
    }

    clear_screen()
    print(ORANGE + "="*64)
    print(r"""
      ██╗   ██╗ ██████╗ ██╗██████╗  ██████╗██╗      █████╗ ██╗    ██╗
      ██║   ██║██╔═══██╗██║██╔══██╗██╔════╝██║     ██╔══██╗██║    ██║
      ██║   ██║██║   ██║██║██║  ██║██║     ██║     ███████║██║ █╗ ██║
      ╚██╗ ██╔╝██║   ██║██║██║  ██║██║     ██║     ██╔══██║██║███╗██║
       ╚████╔╝ ╚██████╔╝██║██████╔╝╚██████╗███████╗██║  ██║╚███╔███╔╝
        ╚═══╝   ╚═════╝ ╚═╝╚═════╝  ╚═════╝╚══════╝╚═╝  ╚═╝ ╚══╝╚══╝
""" + RESET)
    print(AMBER + "           AI Agent for Windows, Mac, Android & Linux" + RESET)
    print(ORANGE + "="*64 + RESET)
    print()

    config_dir = 'common'
    config_path = os.path.join(config_dir, 'config.yaml')
    
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f) or {}
    else:
        # Default configuration template
        config = {
            'default_provider': 'ollama',
            'telegram_token': 'YOUR_TELEGRAM_BOT_TOKEN',
            'workspace_dir': 'workspace',
            'gemini': {'model': 'gemini-1.5-flash', 'api_key': ''},
            'openai': {'model': 'gpt-4o-mini', 'api_key': ''},
            'anthropic': {'model': 'claude-3-5-sonnet-20240620', 'api_key': ''},
            'ollama': {'model': 'llama3', 'host': 'http://localhost:11434'},
            'nvidia': {'model': 'meta/llama3-70b-instruct', 'api_key': ''},
            'openrouter': {'model': 'google/gemma-2-9b-it:free', 'api_key': ''}
        }

    print(ORANGE + "-"*64 + RESET)
    print(AMBER + "                VOIDCLAW MODEL REGISTRY                         " + RESET)
    print(ORANGE + "-"*64 + RESET)
    print()

    token = get_input(ORANGE + "[?] Enter your Telegram Bot Token" + RESET)
    config['telegram_token'] = token

    print(f"\n{AMBER}Select LLM Provider:{RESET}")
    for k, v in registry.items():
        print(f" {k}. {v['name']}")
    
    p_choice = input(ORANGE + "\nSelection: " + RESET).strip()
    if p_choice not in registry: p_choice = "1"
    
    provider_data = registry[p_choice]
    provider_key = provider_data['key']
    config['default_provider'] = provider_key

    print(f"\n{AMBER}Select Model for {provider_data['name']}:{RESET}")
    for i, m in enumerate(provider_data['models'], 1):
        print(f" {i}. {m}")
    print(f" 0. Custom Model Name")

    m_choice = input(ORANGE + "\nSelection: " + RESET).strip()
    
    if m_choice == "0":
        model_name = get_input(ORANGE + "[?] Enter Custom Model Name" + RESET)
    else:
        try:
            idx = int(m_choice) - 1
            if 0 <= idx < len(provider_data['models']):
                model_name = provider_data['models'][idx]
            else:
                model_name = provider_data['models'][0]
        except ValueError:
            model_name = provider_data['models'][0]

    config[provider_key]['model'] = model_name

    if provider_key != 'ollama':
        api_key = get_input(f"{ORANGE}[?] Enter your API Key for {provider_data['name']}{RESET}")
        if provider_key not in config: config[provider_key] = {}
        config[provider_key]['api_key'] = api_key

    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)

    run_cmd = "windows\\run.bat"
    if os.name != 'nt':
        if os.path.exists('/data/data/com.termux'): # Termux detection
            run_cmd = "./termux/run.sh"
        elif sys.platform == 'darwin':
            run_cmd = "./mac/run.sh"
        else:
            run_cmd = "./linux/run.sh"

    print(f"\n{GREEN}[+] Configuration saved successfully!{RESET}")
    print(f"{AMBER}[!] Setup complete. You can now run the agent using {run_cmd}{RESET}\n")

if __name__ == "__main__":
    try:
        run_setup()
    except KeyboardInterrupt:
        print("\nSetup cancelled.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    input("Press Enter to exit...")
