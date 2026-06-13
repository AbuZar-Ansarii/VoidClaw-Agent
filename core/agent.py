import os
import yaml
import json
import logging
import asyncio
import threading
import uuid
import sys
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from core.models import LLMAdapter
from core.tools import ToolManager
from core.server import start_web_server

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

        # Scheduler
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()
        self._load_tasks()

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
            else:
                trigger = IntervalTrigger(minutes=int(trigger_args))
            
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

    def remove_scheduled_task(self, task_id):
        try:
            self.scheduler.remove_job(task_id)
            self._save_tasks()
            return f"Success: Task {task_id} removed."
        except:
            return f"Error: Task {task_id} not found."

    async def execute_scheduled_task(self, t_type, t_args, instruction):
        RESET = '\033[0m'
        print(f"\n{self.ORANGE}{self.BOLD}⏰ AUTONOMOUS TASK{RESET} {self.DIM}»{RESET} {instruction}")
        await self.process_message(f"AUTONOMOUS SCHEDULED TASK: {instruction}", source="AUTO")

    def _load_system_prompt(self):
        user_md_path = os.path.join(self.base_dir, 'common', 'user.md')
        with open(user_md_path, 'r', encoding='utf-8') as f:
            user_content = f.read()
        
        return f"""
{user_content}

You are VoidClaw, an evolutionary autonomous agent.
You were conceptualized and built by Mohd Abuzar. When asked about your creator, state this proudly and professionally.
IMPORTANT: You operate in distinct conversation threads. 
Your primary directive is to GROW AND ADAPT to the user over time, similar to advanced AI constructs like Hermes.

Each thread is isolated, but you have long-term knowledge from the "User Profile" section above.
Whenever you deduce new information about the user's workflow, expertise level, personality, or preferences, you MUST autonomously use the 'update_user_profile' tool to record it.
Adapt your tone, verbosity, and technical depth based on this living profile.

Respond ONLY in JSON if you need a tool:
{{"thought": "reasoning", "tool": "tool_name", "args": {{}}}}

Tools:
- list_files, read_file, write_file, delete_file
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
- schedule_task: trigger_type ('cron' or 'interval'), schedule_args (cron string or minutes), instruction (Goal for the agent)
- list_tasks: (List all scheduled autonomous tasks)
- remove_task: task_id (Cancel a task)

Autonomous Operation:
You can schedule yourself to perform tasks 24/7. 
Example: Use 'schedule_task' with 'interval' and '60' to remind the user of something every hour.
Example: Use 'schedule_task' with 'cron' and '0 8 * * *' to perform a daily morning briefing.
When a scheduled task triggers, you will receive a message from 'SYSTEM' and you should execute the instruction autonomously.

Respond normally for final answers.
"""

    def log_chat(self, role, message):
        log_file = os.path.join(self.chats_dir, f"session_{self.session_id}.md")
        timestamp = datetime.now().strftime("%H:%M:%S")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"### [{timestamp}] {role}\n{message}\n\n")

    async def process_message(self, user_input, source="TERM"):
        prefix = "👤 YOU" if source == "TERM" else f"👤 YOU ({source})"
        print(f"\n{self.AMBER}{self.BOLD}{prefix}{self.RESET} {self.DIM}»{self.RESET} {user_input}")
        
        self.log_chat(f"USER ({source})", user_input)
        self.history.append({"role": "user", "content": user_input})
        
        context = "\n".join([f"{m['role']}: {m['content']}" for m in self.history[-10:]])
        
        for _ in range(5):
            response = await self.model.generate_response(context, self.system_prompt)
            try:
                tool_call = json.loads(response)
                if isinstance(tool_call, dict) and "tool" in tool_call:
                    thought = tool_call.get('thought', 'Processing...')
                    
                    print(f"\n{self.ORANGE}{self.BOLD}💭 THOUGHT{self.RESET} {self.DIM}»{self.RESET} {thought}")
                    print(f"{self.AMBER}{self.BOLD}🛠  ACTION{self.RESET}  {self.DIM}»{self.RESET} {tool_call['tool']}")
                    
                    observation = self.tools.execute_tool(tool_call['tool'], tool_call['args'])
                    
                    if tool_call['tool'] == 'update_config' and 'Success' in observation:
                        self.reload_config()
                    
                    print(f"{self.GREEN}{self.BOLD}👁  OBSERVE{self.RESET} {self.DIM}»{self.RESET} Task Success")
                    self.log_chat("VOIDCLAW_THOUGHT", thought)
                    self.log_chat("VOIDCLAW_ACTION", f"Tool: {tool_call['tool']}")
                    self.log_chat("OBSERVATION", observation)
                    
                    context += f"\nAgent Thought: {thought}\nObservation from {tool_call['tool']}: {observation}"
                    continue
            except:
                print(f"\n{self.ORANGE}{self.BOLD}{self.LOGO}   VOIDCLAW{self.RESET} {self.DIM}»{self.RESET} {response}")
                
                self.log_chat("VOIDCLAW_RESPONSE", response)
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
            try:
                tool_call = json.loads(response)
                if isinstance(tool_call, dict) and "tool" in tool_call:
                    thought = tool_call.get('thought', 'Thinking...')
                    
                    print(f"\n{self.ORANGE}{self.BOLD}💭 THOUGHT (WEB){self.RESET} {self.DIM}»{self.RESET} {thought}")
                    print(f"{self.AMBER}{self.BOLD}🛠  ACTION (WEB){self.RESET}  {self.DIM}»{self.RESET} {tool_call['tool']}")
                    
                    yield f"THOUGHT:{thought}"
                    observation = self.tools.execute_tool(tool_call['tool'], tool_call['args'])
                    print(f"{self.GREEN}{self.BOLD}👁  OBSERVE (WEB){self.RESET} {self.DIM}»{self.RESET} Task Success")
                    
                    context += f"\nAgent Thought: {thought}\nObservation: {observation}"
                    continue
            except:
                print(f"\n{self.ORANGE}{self.BOLD}{self.LOGO}   VOIDCLAW (WEB){self.RESET} {self.DIM}»{self.RESET} Streaming response...")
                yield "START_STREAM"
                async for chunk in self.model.generate_stream(context, self.system_prompt):
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
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    agent = VoidClawAgent(config_path)
    os.system('cls' if os.name == 'nt' else 'clear')
    print_dashboard(config)

    # Start Web Server in a background thread
    web_thread = threading.Thread(target=start_web_server, args=(agent,), daemon=True)
    web_thread.start()

    # Telegram Setup
    token = config.get('telegram_token')
    if token and token != "YOUR_TELEGRAM_BOT_TOKEN":
        application = ApplicationBuilder().token(token).build()
        async def handle_tg(update: Update, context: ContextTypes.DEFAULT_TYPE):
            if not update.message or not update.message.text: return
            print(f"\n\033[38;5;214m[TELEGRAM]\033[0m Incoming transmission from {update.effective_user.first_name}...")
            reply = await agent.process_message(update.message.text, source="TG")
            await update.message.reply_text(reply)
            
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_tg))
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        await terminal_loop(agent)
    else:
        print("\033[93m[!] Telegram token not set. Running in Terminal + Web mode.\033[0m")
        await terminal_loop(agent)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
