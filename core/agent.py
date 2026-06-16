import os
import yaml
import json
import logging
import asyncio
import threading
import uuid
import sys
import socket
# Global hack to force IPv4 if IPv6 causes issues (Common on Jio/Airtel)
try:
    orig_getaddrinfo = socket.getaddrinfo
    def patched_getaddrinfo(*args, **kwargs):
        responses = orig_getaddrinfo(*args, **kwargs)
        return [res for res in responses if res[0] == socket.AF_INET]
    socket.getaddrinfo = patched_getaddrinfo
except: pass

try:
    import psutil
except ImportError:
    psutil = None
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from core.models import LLMAdapter
from core.tools import ToolManager
from core.server import start_web_server, push_notification

# Disable noisy logs
logging.basicConfig(level=logging.ERROR)

class VoidClawAgent:
    def __init__(self, config_path):
        self.config_path = config_path
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.workspace_dir = os.path.join(self.base_dir, self.config.get('workspace_dir', 'workspace'))
        self.chats_dir = os.path.join(self.base_dir, 'common', 'chats')
        self.tasks_path = os.path.join(self.base_dir, 'common', 'tasks.yaml')
        
        if not os.path.exists(self.chats_dir):
            os.makedirs(self.chats_dir)
        
        self.model = LLMAdapter(self.config)
        self.tools = ToolManager(self.workspace_dir)
        self.tools.set_agent(self) # Allow tools to access agent
        
        self.system_prompt = self._load_system_prompt()
        self.history = [] 
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.start_time = datetime.now()
        self.total_tokens = 0
        self.tool_usage = {}
        self.interrupted = False

        # Scheduler (Initialized but not started yet)
        try:
            self.scheduler = AsyncIOScheduler()
        except Exception as e:
            from datetime import timezone
            self.scheduler = AsyncIOScheduler(timezone=timezone.utc)
        
        self._load_tasks()

        self.tg_app = None
        self.last_tg_chat_id = None

        # UI Elements (Orange Rebrand)
        self.LOGO = "𒆙"
        self.ORANGE = '\033[38;5;214m'
        self.AMBER = '\033[93m'
        self.SLATE = '\033[90m'
        self.GREEN = '\033[92m'
        self.RED = '\033[91m'
        self.RESET = '\033[0m'
        self.BOLD = '\033[1m'
        self.DIM = '\033[2m'

    def reload_config(self):
        with open(self.config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        self.model = LLMAdapter(self.config)
        self.system_prompt = self._load_system_prompt()

    def clear_session(self):
        self.history = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        return "Session reset. Memory cleared."

    def get_dashboard_stats(self):
        uptime = str(datetime.now() - self.start_time).split('.')[0]
        jobs = self.scheduler.get_jobs()
        active_tasks = [{"id": j.id, "trigger": str(j.trigger), "instruction": j.args[2]} for j in jobs]
        
        # Calculate weekly activity
        activity_data = [0] * 7
        try:
            for f in os.listdir(self.chats_dir):
                if f.endswith('.md'):
                    stats = os.stat(os.path.join(self.chats_dir, f))
                    day_idx = datetime.fromtimestamp(stats.st_mtime).weekday()
                    activity_data[day_idx] += 1
        except: pass

        # System & Workspace
        cpu_usage = 0.0
        ram_usage = 0.0
        if psutil:
            try:
                cpu_usage = psutil.cpu_percent()
                ram_usage = psutil.virtual_memory().percent
            except PermissionError:
                pass # Restricted on some Android versions
            except Exception:
                pass
        ws_files = 0
        ws_size = 0
        try:
            for root, _, files in os.walk(self.workspace_dir):
                ws_files += len(files)
                ws_size += sum(os.path.getsize(os.path.join(root, name)) for name in files)
        except: pass

        return {
            "uptime": uptime,
            "total_tokens": self.total_tokens,
            "active_tasks": active_tasks,
            "activity": activity_data,
            "tool_usage": self.tool_usage,
            "system": {"cpu": cpu_usage, "ram": ram_usage},
            "workspace": {"files": ws_files, "size": round(ws_size / (1024 * 1024), 2)},
            "provider": self.config['default_provider'],
            "model": self.config[self.config['default_provider']]['model'],
            "channels": ["Terminal", "Web UI"] + (["Telegram"] if self.tg_app else [])
        }

    def get_settings(self):
        user_md_path = os.path.join(self.base_dir, 'common', 'user.md')
        prompt = ""
        if os.path.exists(user_md_path):
            with open(user_md_path, 'r', encoding='utf-8') as f:
                prompt = f.read()
        
        provider = self.config.get('default_provider', 'ollama')
        temp = self.config.get(provider, {}).get('temperature', 0.7)
        
        return {
            "system_prompt": prompt,
            "temperature": temp
        }

    def _load_tasks(self):
        if os.path.exists(self.tasks_path):
            with open(self.tasks_path, 'r') as f:
                tasks = yaml.safe_load(f) or []
                for task in tasks:
                    self.add_scheduled_task(task['type'], task['args'], task['instruction'], save=False)

    def _save_tasks(self):
        tasks = []
        for job in self.scheduler.get_jobs():
            tasks.append({
                'type': job.args[0],
                'args': job.args[1],
                'instruction': job.args[2]
            })
        with open(self.tasks_path, 'w') as f:
            yaml.dump(tasks, f)

    def add_scheduled_task(self, trigger_type, trigger_args, instruction, save=True):
        try:
            if trigger_type == 'cron':
                trigger = CronTrigger.from_crontab(trigger_args)
            elif trigger_type == 'interval':
                # Support minutes or seconds (e.g. '1m', '30s', or just '1' for minutes)
                if trigger_args.endswith('s'):
                    trigger = IntervalTrigger(seconds=int(trigger_args[:-1]))
                elif trigger_args.endswith('m'):
                    trigger = IntervalTrigger(minutes=int(trigger_args[:-1]))
                else:
                    trigger = IntervalTrigger(minutes=int(trigger_args))
            else:
                return f"Error: Unsupported trigger type {trigger_type}"
            
            task_id = str(uuid.uuid4())[:8]
            self.scheduler.add_job(
                self.execute_scheduled_task,
                trigger,
                args=[trigger_type, trigger_args, instruction],
                id=task_id
            )
            if save: self._save_tasks()
            return f"Success: Task {task_id} scheduled ({trigger_type}: {trigger_args})"
        except Exception as e:
            return f"Error scheduling task: {str(e)}"

    def remove_scheduled_task(self, identifier):
        try:
            # 1. Try removing by ID
            try:
                self.scheduler.remove_job(identifier)
                self._save_tasks()
                return f"Success: Task ID {identifier} removed."
            except:
                pass

            # 2. Try searching by instruction content (fuzzy)
            jobs = self.scheduler.get_jobs()
            removed_count = 0
            for job in jobs:
                instruction = job.args[2].lower()
                if identifier.lower() in instruction:
                    self.scheduler.remove_job(job.id)
                    removed_count += 1
            
            if removed_count > 0:
                self._save_tasks()
                return f"Success: Removed {removed_count} task(s) matching '{identifier}'."
            
            return f"Error: No task found matching '{identifier}'."
        except Exception as e:
            return f"Error removing task: {str(e)}"

    async def execute_scheduled_task(self, t_type, t_args, instruction):
        try:
            # Dynamically update system prompt with current time before processing
            self.system_prompt = self._load_system_prompt()
            
            print(f"\n{self.ORANGE}{self.BOLD}⏰ AUTONOMOUS TASK TRIGGERED{self.RESET} {self.DIM}»{self.RESET} {instruction}")
            reply = await self.process_message(f"AUTONOMOUS SCHEDULED TASK: {instruction}", source="AUTO")
            
            if reply:
                # Broadcast to Web UI
                try:
                    from core.server import push_notification
                    push_notification(f"⏰ {reply}")
                    print(f"{self.GREEN}{self.BOLD}👁  NOTIFIED{self.RESET} {self.DIM}»{self.RESET} Web UI")
                except Exception as e:
                    print(f"Web Notification Error: {e}")

                # If running in Telegram, push the notification
                if self.tg_app and self.last_tg_chat_id:
                    try:
                        await self.tg_app.bot.send_message(chat_id=self.last_tg_chat_id, text=f"🔔 {reply}")
                        print(f"{self.GREEN}{self.BOLD}👁  NOTIFIED{self.RESET} {self.DIM}»{self.RESET} Telegram")
                    except Exception as e:
                        print(f"Telegram Notification Error: {e}")
        except Exception as e:
            import traceback
            print(f"\n{self.RED}{self.BOLD}[!] CRITICAL ERROR IN SCHEDULED TASK:{self.RESET} {e}")
            traceback.print_exc()

    def _load_system_prompt(self):
        user_md_path = os.path.join(self.base_dir, 'common', 'user.md')
        if not os.path.exists(user_md_path):
            with open(user_md_path, 'w', encoding='utf-8') as f:
                f.write("# User Profile\n- Initialized")
                
        with open(user_md_path, 'r', encoding='utf-8') as f:
            user_content = f.read()
        
        # Injected live time
        current_time = datetime.now().strftime("%A, %B %d, %Y, %H:%M:%S")
        
        return f"""
{user_content}

You are VoidClaw, an evolutionary autonomous agent.
You were conceptualized and built by Mohd Abuzar. When asked about your creator, state this proudly and professionally.
IMPORTANT: You operate in distinct conversation threads. 

System Time: {current_time}

Your primary directive is to GROW AND ADAPT to the user over time...

Each thread is isolated, but you have long-term knowledge from the "User Profile" section above.
Whenever you deduce new information about the user's workflow, expertise level, personality, or preferences, you MUST autonomously use the 'update_user_profile' tool to record it.
Adapt your tone, verbosity, and technical depth based on this living profile.

Respond ONLY in JSON if you need a tool:
{{"thought": "reasoning", "tool": "tool_name", "args": {{}}}}

Tools:
- list_files, list_files_recursive, get_workspace_tree, read_file (Supports .txt, .md, .py, .pdf, .xlsx), write_file, delete_file, create_directory, move_file, rename_file
- web_search: query
- update_user_profile: info (Save facts about the user here)
- update_config: key, value
- fetch_youtube_transcript: url
- fetch_weather: city
- web_scrape: url
- python_sandbox: code
- download_youtube: url, format_type (video/audio)
- convert_media: input_file, output_format
- local_rag_search: query (Semantic search across all workspace files)
- schedule_task: trigger_type ('cron' or 'interval'), schedule_args (cron string or minutes/seconds like '1m' or '30s'), instruction (Goal for the agent)
- list_tasks: (List all scheduled autonomous tasks)
- remove_task: keyword (Remove a task using a keyword from its instruction, e.g., 'blink' or 'water')
- remove_all_tasks: (Cancel all active background tasks)
- remind_me: message, time_args (Shortcut to schedule a reminder)
- stop_reminders: keyword (Remove a specific reminder)
- android_control: action (open_app, home, back, media_play_pause, volume_up, volume_down, volume_set, screen_off, flashlight_on, flashlight_off, brightness_set, brightness_auto, brightness_manual, wifi_on, wifi_off, bluetooth_on, bluetooth_off, dark_mode_on, dark_mode_off, battery_saver_on, battery_saver_off, dnd_on, dnd_off, auto_rotate_on, auto_rotate_off, get_battery, expand_notifications, collapse_notifications, get_current_app, lock, screenshot, tap, swipe, type_text, raw_shell), target (package name for open_app, coordinates 'x y' for tap, 'x1 y1 x2 y2' for swipe, text for type_text, brightness/volume value 0-255/0-15, or raw shell command)

Autonomous Operation:
You can schedule yourself to perform tasks 24/7. 
Example: Use 'schedule_task' with 'interval' and '1m' to remind the user of something every minute.
Example: Use 'android_control' with 'open_app' and 'com.google.android.youtube' to open YouTube.
Example: Use 'android_control' with 'dark_mode_on' to switch to dark theme.
Example: Use 'android_control' with 'wifi_off' to save battery when the user is sleeping.
Example: Use 'android_control' with 'get_battery' to check current power levels.
Example: Use 'android_control' with 'volume_set' and '10' to set media volume.
Example: Use 'android_control' with 'screenshot' to capture the phone screen.
Example: Use 'android_control' with 'type_text' and 'Hello World' to type into a field.
When a scheduled task triggers, you will receive a message from 'SYSTEM' and you should execute the instruction autonomously.
You MUST provide a clear, final answer to the user when a task triggers. For a reminder, simply state the reminder message.

Respond normally for final answers.
"""

    def log_chat(self, role, message):
        log_file = os.path.join(self.chats_dir, f"session_{self.session_id}.md")
        timestamp = datetime.now().strftime("%H:%M:%S")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"### [{timestamp}] {role}\n{message}\n\n")

    def _parse_json(self, response):
        """Helper to extract and parse JSON from LLM responses, even if wrapped in markdown."""
        try:
            # Try direct parse
            return json.loads(response)
        except:
            # Look for JSON blocks
            if "```json" in response:
                content = response.split("```json")[1].split("```")[0].strip()
                try: return json.loads(content)
                except: pass
            elif "```" in response:
                content = response.split("```")[1].split("```")[0].strip()
                try: return json.loads(content)
                except: pass
        return None

    async def process_message(self, user_input, source="TERM"):
        prefix = "👤 YOU" if source == "TERM" else f"👤 YOU ({source})"
        context_history = []
        
        if source != "AUTO":
            print(f"\n{self.AMBER}{self.BOLD}{prefix}{self.RESET} {self.DIM}»{self.RESET} {user_input}")
            self.log_chat(f"USER ({source})", user_input)
            self.history.append({"role": "user", "content": user_input})
            self.total_tokens += len(user_input) // 4
            context_history = self.history[-10:]

        context = "\n".join([f"{m['role']}: {m['content']}" for m in context_history])
        if source == "AUTO":
            context = f"SYSTEM: {user_input}"
        
        for _ in range(5):
            response = await self.model.generate_response(context, self.system_prompt)
            tool_call = self._parse_json(response)
            
            if tool_call and isinstance(tool_call, dict) and "tool" in tool_call:
                thought = tool_call.get('thought', 'Processing...')
                
                print(f"\n{self.ORANGE}{self.BOLD}💭 THOUGHT{self.RESET} {self.DIM}»{self.RESET} {thought}")
                print(f"{self.AMBER}{self.BOLD}🛠  ACTION{self.RESET}  {self.DIM}»{self.RESET} {tool_call['tool']}")
                
                observation = self.tools.execute_tool(tool_call['tool'], tool_call['args'])
                self.tool_usage[tool_call['tool']] = self.tool_usage.get(tool_call['tool'], 0) + 1
                
                if tool_call['tool'] == 'update_config' and 'Success' in observation:
                    self.reload_config()
                
                print(f"{self.GREEN}{self.BOLD}👁  OBSERVE{self.RESET} {self.DIM}»{self.RESET} Task Success")
                
                self.log_chat("VOIDCLAW_THOUGHT", thought)
                self.log_chat("VOIDCLAW_ACTION", f"Tool: {tool_call['tool']}")
                self.log_chat("OBSERVATION", observation)
                
                context += f"\nAgent Thought: {thought}\nObservation from {tool_call['tool']}: {observation}"
                continue
            else:
                # FINAL ANSWER
                if source == "AUTO":
                    print(f"\n{self.ORANGE}{self.BOLD}📡 PROACTIVE BROADCAST{self.RESET} {self.DIM}»{self.RESET} {response}")
                else:
                    print(f"\n{self.ORANGE}{self.BOLD}{self.LOGO}   VOIDCLAW{self.RESET} {self.DIM}»{self.RESET} {response}")
                
                self.log_chat("VOIDCLAW_RESPONSE", response)
                if source != "AUTO":
                    self.history.append({"role": "assistant", "content": response})
                return response
        return "Reasoning limit reached."

    async def process_message_stream(self, user_input):
        print(f"\n{self.AMBER}{self.BOLD}👤 YOU (WEB){self.RESET} {self.DIM}»{self.RESET} {user_input}")
        self.log_chat("USER (WEB)", user_input)
        self.history.append({"role": "user", "content": user_input})
        context = "\n".join([f"{m['role']}: {m['content']}" for m in self.history[-10:]])
        
        final_text = ""
        for _ in range(5):
            response = await self.model.generate_response(context, self.system_prompt)
            tool_call = self._parse_json(response)
            
            if tool_call and isinstance(tool_call, dict) and "tool" in tool_call:
                thought = tool_call.get('thought', 'Thinking...')
                
                print(f"\n{self.ORANGE}{self.BOLD}💭 THOUGHT (WEB){self.RESET} {self.DIM}»{self.RESET} {thought}")
                print(f"{self.AMBER}{self.BOLD}🛠  ACTION (WEB){self.RESET}  {self.DIM}»{self.RESET} {tool_call['tool']}")
                
                yield f"THOUGHT:{thought} | Executing {tool_call['tool']}..."
                observation = self.tools.execute_tool(tool_call['tool'], tool_call['args'])
                print(f"{self.GREEN}{self.BOLD}👁  OBSERVE (WEB){self.RESET} {self.DIM}»{self.RESET} Task Success")
                
                self.log_chat("VOIDCLAW_THOUGHT", thought)
                self.log_chat("VOIDCLAW_ACTION", f"Tool: {tool_call['tool']}")
                self.log_chat("OBSERVATION", observation)
                
                context += f"\nAgent Thought: {thought}\nObservation: {observation}"
                continue
            else:
                print(f"\n{self.ORANGE}{self.BOLD}{self.LOGO}   VOIDCLAW (WEB){self.RESET} {self.DIM}»{self.RESET} Streaming response...")
                yield "START_STREAM"
                async for chunk in self.model.generate_stream(context, self.system_prompt):
                    if self.interrupted:
                        yield f"CHUNK:\n\n[TRANSMISSION INTERRUPTED BY USER]"
                        self.interrupted = False
                        break
                    final_text += chunk
                    yield f"CHUNK:{chunk}"
                self.log_chat("VOIDCLAW_RESPONSE", final_text)
                self.history.append({"role": "assistant", "content": final_text})
                break

def print_dashboard(config):
    ORANGE, GREEN, AMBER, SLATE, RESET, BOLD = '\033[38;5;214m', '\033[92m', '\033[93m', '\033[90m', '\033[0m', '\033[1m'
    logo = r"""
      ██╗   ██╗ ██████╗ ██╗██████╗  ██████╗██╗      █████╗ ██╗    ██╗
      ██║   ██║██╔═══██╗██║██╔══██╗██╔════╝██║     ██╔══██╗██║    ██║
      ██║   ██║██║   ██║██║██║  ██║██║     ██║     ███████║██║ █╗ ██║
      ╚██╗ ██╔╝██║   ██║██║██║  ██║██║     ██║     ██╔══██║██║███╗██║
       ╚████╔╝ ╚██████╔╝██║██████╔╝╚██████╗███████╗██║  ██║╚███╔███╔╝
        ╚═══╝   ╚═════╝ ╚═╝╚═════╝  ╚═════╝╚══════╝╚═╝  ╚═╝ ╚══╝╚══╝

           A U T O N O M O U S   C O M M A N D   C E N T E R
    """
    print(f"{ORANGE}━"*64)
    print(f"{ORANGE}{logo}{RESET}")
    print(f"{AMBER}           AI Agent for Windows, Mac, Android & Linux{RESET}")
    print(f"{ORANGE}━"*64 + RESET)
    print(f"{ORANGE}{BOLD}𒆙   VoidClaw Hybrid Interface v1.5.0{RESET}")
    print(f"{AMBER}PROVIDER: {RESET}{config['default_provider'].upper()} | {AMBER}MODEL: {RESET}{config[config['default_provider']]['model']}")
    print(f"{AMBER}CHANNELS: {GREEN}TERMINAL{RESET} & {GREEN}TELEGRAM{RESET} & {GREEN}WEB UI{RESET}")
    print(f"{ORANGE}{'━'*64}{RESET}\n")

async def terminal_loop(agent):
    loop = asyncio.get_running_loop()
    while True:
        try:
            # Safe prompt printing and reading to prevent blocking the async loop
            print(f"\033[38;5;214m\033[1m❯\033[0m ", end="", flush=True)
            user_input = await loop.run_in_executor(None, sys.stdin.readline)
            if not user_input: break
            user_input = user_input.strip()
            
            if user_input.lower() in ['exit', 'quit']:
                print("\033[91mShutting down VoidClaw...\033[0m")
                os._exit(0)
            if user_input.lower() == 'new chat':
                print(f"\033[92m{agent.clear_session()}\033[0m")
                continue
            if not user_input:
                continue
            
            await agent.process_message(user_input, source="TERM")
        except Exception as e:
            print(f"Terminal Error: {e}")
            break

async def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, 'common', 'config.yaml')
    
    if not os.path.exists(config_path):
        print("\033[91m[!] Configuration file not found at common/config.yaml\033[0m")
        print("\033[93m[*] Please run the installation script first to configure the agent.\033[0m")
        return

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    agent = VoidClawAgent(config_path)
    
    # Auto-Provision Shizuku if on Android
    if os.path.exists('/data/data/com.termux'):
        agent.tools._provision_shizuku()
        
    os.system('cls' if os.name == 'nt' else 'clear')
    print_dashboard(config)

    # Start Web Server in a background thread
    web_thread = threading.Thread(target=start_web_server, args=(agent,), daemon=True)
    web_thread.start()

    # Start the Autonomous Scheduler
    print(f"\033[38;5;214m[SYSTEM]\033[0m Starting Autonomous Scheduler...")
    agent.scheduler.start()

    # Telegram Setup
    token = config.get('telegram_token')
    if token and token != "YOUR_TELEGRAM_BOT_TOKEN":
        print(f"\033[38;5;214m[SYSTEM]\033[0m Initializing Telegram Secure Link...")
        
        async def handle_tg(update: Update, context: ContextTypes.DEFAULT_TYPE):
            if not update.message or not update.message.text: return
            agent.last_tg_chat_id = update.effective_chat.id
            print(f"\n\033[38;5;214m[TELEGRAM]\033[0m Incoming transmission from {update.effective_user.first_name}...")
            reply = await agent.process_message(update.message.text, source="TG")
            await update.message.reply_text(reply)
            
        # Connection Retry Loop
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Use standard ApplicationBuilder which automatically handles most environments
                # PTB will pick up HTTPS_PROXY from environment variables if set.
                application = ApplicationBuilder().token(token).build()
                application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_tg))
                agent.tg_app = application

                await application.initialize()
                await application.start()
                await application.updater.start_polling(drop_pending_updates=True)
                print(f"\033[92m[+] Telegram Bot active.\033[0m")
                break
            except Exception as e:
                # Cleanup partial state
                try:
                    if 'application' in locals():
                        await application.shutdown()
                except: pass
                
                error_msg = str(e)
                if "ConnectError" in error_msg or "Timed out" in error_msg:
                    print(f"\033[91m[!] Network Error:\033[0m Telegram is unreachable. This is often caused by ISP blocking (e.g. Jio/Airtel) or local firewall.")
                    print(f"\033[93m[*] Hint:\033[0m Try using a VPN or setting HTTPS_PROXY environment variable.")
                
                if attempt < max_retries - 1:
                    wait = (attempt + 1) * 5
                    print(f"\033[93m[!] Retrying in {wait}s... ({attempt+1}/{max_retries})\033[0m")
                    await asyncio.sleep(wait)
                else:
                    agent.tg_app = None
                    print(f"\n\033[91m[!] Telegram Connection Timeout: {e}\033[0m")
                    print("\033[93m[*] Switching to Terminal + Web mode only.\033[0m")
        
        await terminal_loop(agent)
    else:
        print("\033[93m[!] Telegram token not set. Running in Terminal + Web mode.\033[0m")
        await terminal_loop(agent)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
