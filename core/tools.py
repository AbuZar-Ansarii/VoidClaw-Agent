import os
import shutil
import subprocess
from duckduckgo_search import DDGS

# Production File Support
try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    import openpyxl
except ImportError:
    openpyxl = None

class ToolManager:
    def __init__(self, workspace_dir):
        self.workspace_dir = os.path.abspath(workspace_dir)
        if not os.path.exists(self.workspace_dir):
            os.makedirs(self.workspace_dir)
        self.agent = None

    def set_agent(self, agent):
        self.agent = agent

    def execute_tool(self, tool_name, args):
        tools = {
            "list_files": self.list_files,
            "list_files_recursive": self.list_files_recursive,
            "get_workspace_tree": self.get_workspace_tree,
            "read_file": self.read_file,
            "write_file": self.write_file,
            "delete_file": self.delete_file,
            "create_directory": self.create_directory,
            "move_file": self.move_file,
            "rename_file": self.rename_file,
            "read_pdf": self.read_pdf,
            "read_excel": self.read_excel,
            "web_search": self.web_search,
            "get_memory": self.get_memory,
            "update_memory": self.update_memory,
            "update_config": self.update_config,
            "update_user_profile": self.update_user_profile,
            "fetch_youtube_transcript": self.fetch_youtube_transcript,
            "fetch_weather": self.fetch_weather,
            "web_scrape": self.web_scrape,
            "python_sandbox": self.python_sandbox,
            "download_youtube": self.download_youtube,
            "convert_media": self.convert_media,
            "local_rag_search": self.local_rag_search,
            "schedule_task": self.schedule_task,
            "list_tasks": self.list_tasks,
            "remove_task": self.remove_task,
            "remove_all_tasks": self.remove_all_tasks,
            "remind_me": self.remind_me,
            "stop_reminders": self.stop_reminders,
            "android_control": self.android_control
        }
        if tool_name in tools:
            return tools[tool_name](**args)
        return f"Tool {tool_name} not found."

    def _provision_shizuku(self):
        """Attempts to auto-import and configure Shizuku files if missing."""
        if not os.path.exists('/data/data/com.termux'):
            return None

        # Check if already in PATH
        rish_path = shutil.which('rish')
        if rish_path: return rish_path

        # Check common internal locations
        paths = ['/data/data/com.termux/files/usr/bin/rish', '/data/data/com.termux/files/home/.local/bin/rish']
        for p in paths:
            if os.path.exists(p): return p

        # Attempt auto-import from /sdcard/Shizuku/ (requires termux-setup-storage)
        src_dir = '/sdcard/Shizuku'
        dest_bin = '/data/data/com.termux/files/usr/bin'
        
        if os.path.exists(os.path.join(src_dir, 'rish')):
            try:
                # Auto-Provisioning Sequence
                os.system(f"cp {src_dir}/rish* {dest_bin}/")
                os.system(f"chmod +x {dest_bin}/rish")
                os.system(f"chmod 444 {dest_bin}/rish_shizuku.dex") # Security: must not be writable
                print(f"\033[92m[SYSTEM]\033[0m Shizuku environment provisioned successfully.")
                return os.path.join(dest_bin, 'rish')
            except Exception as e:
                print(f"\033[91m[!] Shizuku Auto-Import Failed:\033[0m {e}")
        return None

    def android_control(self, action, target=""):
        """Controls Android system using Shizuku (rish) with Auto-Provisioning"""
        is_android = os.path.exists('/data/data/com.termux')
        if not is_android:
            return "Error: Android control is only available on Android/Termux environments."

        # 1. Ensure Shizuku is Provisioned
        rish_path = self._provision_shizuku()
        if not rish_path:
            return "Error: Shizuku not set up. Please: 1. In Shizuku app, tap 'Use in terminal' -> 'Export files'. 2. Save to 'Shizuku' folder. 3. Run 'termux-setup-storage' in Termux."

        # 2. Command Execution
        cmd_map = {
            "open_app": f"monkey -p {target} -c android.intent.category.LAUNCHER 1",
            "home": "input keyevent 3",
            "back": "input keyevent 4",
            "media_play_pause": "input keyevent 85",
            "volume_up": "input keyevent 24",
            "volume_down": "input keyevent 25",
            "screen_off": "input keyevent 26",
            "flashlight_on": "cmd notification set_flashlight 1",
            "flashlight_off": "cmd notification set_flashlight 0",
            "brightness_set": f"settings put system screen_brightness {target}",
            "brightness_auto": "settings put system screen_brightness_mode 1",
            "brightness_manual": "settings put system screen_brightness_mode 0",
            "wifi_on": "svc wifi enable",
            "wifi_off": "svc wifi disable",
            "bluetooth_on": "svc bluetooth enable",
            "bluetooth_off": "svc bluetooth disable",
            "dark_mode_on": "cmd uimode night yes",
            "dark_mode_off": "cmd uimode night no",
            "battery_saver_on": "settings put global low_power 1",
            "battery_saver_off": "settings put global low_power 0",
            "dnd_on": "cmd notification set_dnd on",
            "dnd_off": "cmd notification set_dnd off",
            "auto_rotate_on": "settings put system accelerometer_rotation 1",
            "auto_rotate_off": "settings put system accelerometer_rotation 0",
            "get_battery": "dumpsys battery",
            "volume_set": f"media volume --set {target}",
            "expand_notifications": "cmd statusbar expand-notifications",
            "collapse_notifications": "cmd statusbar collapse",
            "get_current_app": "dumpsys window | grep mCurrentFocus",
            "lock": "input keyevent 26",
            "screenshot": f"screencap -p /sdcard/voidclaw_screenshot.png",
            "tap": f"input tap {target}",
            "swipe": f"input swipe {target}",
            "type_text": f"input text '{target}'",
            "raw_shell": target
        }

        if action not in cmd_map:
            return f"Error: Unsupported action '{action}'."

        final_cmd = cmd_map[action]
        try:
            # Set required environment variable for rish
            env = os.environ.copy()
            env["RISH_APPLICATION_ID"] = "com.termux"

            # Execute via sh rish to ensure shell compatibility
            result = subprocess.run(["sh", rish_path, "-c", final_cmd], capture_output=True, text=True, timeout=15, env=env)
            
            if result.returncode == 0:
                if action == "screenshot":
                    # Move from sdcard to workspace
                    src = "/sdcard/voidclaw_screenshot.png"
                    dest = os.path.join(self.workspace_dir, f"screenshot_{os.urandom(2).hex()}.png")
                    # We need rish to move it because Termux might not have direct /sdcard access without setup
                    # Actually, if termux-setup-storage is done, we can just move it.
                    # But safer to use rish to cat it to a file in workspace
                    move_cmd = f"cat {src} > {dest}" # This is wrong, dest is local path. 
                    # Correct way: capture output of rish screencap or pull it.
                    # Let's use rish to write directly to a path rish can access, then move it.
                    # Simplified: rish -c 'screencap -p' > local_file
                    
                    # RE-RUN for screenshot to capture stdout directly
                    screenshot_dest = os.path.join(self.workspace_dir, f"screenshot_{os.urandom(2).hex()}.png")
                    with open(screenshot_dest, "wb") as f:
                        subprocess.run(["sh", rish_path, "-c", "screencap -p"], stdout=f, env=env, timeout=20)
                    return f"Success: Screenshot saved to workspace as {os.path.basename(screenshot_dest)}"

                return f"Success: Action '{action}' executed."
            else:
                stderr = result.stderr.strip()
                if not stderr and result.stdout: stderr = result.stdout.strip()
                return f"Error from Android: {stderr if stderr else 'Unknown error'}"
        except subprocess.TimeoutExpired:
            return "Error: Command timed out. Is Shizuku service running?"
        except Exception as e:
            return f"Error executing rish: {str(e)}"

    def _safe_path(self, filename):
        path = os.path.abspath(os.path.join(self.workspace_dir, filename))
        if not path.startswith(self.workspace_dir):
            raise ValueError("Access outside workspace is restricted.")
        return path

    def update_config(self, key, value, subkey=None):
        try:
            import yaml
            config_path = os.path.join(os.path.dirname(self.workspace_dir), 'common', 'config.yaml')
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            if subkey:
                if key not in config: config[key] = {}
                config[key][subkey] = value
            else:
                config[key] = value
                
            with open(config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            return f"Success: {key}{'/' + subkey if subkey else ''} set to {value}. LLM changes are instant; Telegram changes require a restart."
        except Exception as e:
            return f"Error updating config: {str(e)}"

    def update_user_profile(self, info):
        try:
            user_md_path = os.path.join(os.path.dirname(self.workspace_dir), 'common', 'user.md')
            with open(user_md_path, 'a', encoding='utf-8') as f:
                f.write(f"\n- {info}")
            return "User profile updated with new information."
        except Exception as e:
            return str(e)

    def list_files(self):
        try:
            return "\n".join(os.listdir(self.workspace_dir)) or "Workspace is empty."
        except Exception as e:
            return str(e)

    def list_files_recursive(self):
        try:
            files = []
            for root, _, filenames in os.walk(self.workspace_dir):
                for filename in filenames:
                    rel_path = os.path.relpath(os.path.join(root, filename), self.workspace_dir)
                    files.append(rel_path)
            return "\n".join(files) or "Workspace is empty."
        except Exception as e:
            return str(e)

    def get_workspace_tree(self):
        try:
            tree = []
            for root, dirs, files in os.walk(self.workspace_dir):
                level = root.replace(self.workspace_dir, '').count(os.sep)
                indent = '  ' * level
                tree.append(f"{indent}{os.path.basename(root)}/")
                sub_indent = '  ' * (level + 1)
                for f in files:
                    tree.append(f"{sub_indent}{f}")
            return "\n".join(tree)
        except Exception as e:
            return str(e)

    def read_file(self, filename):
        try:
            path = self._safe_path(filename)
            ext = os.path.splitext(filename)[1].lower()
            
            if ext == '.pdf':
                return self.read_pdf(filename)
            elif ext in ['.xlsx', '.xls']:
                return self.read_excel(filename)
                
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return str(e)

    def read_pdf(self, filename):
        if not PdfReader:
            return "Error: pypdf library not installed. PDF support is currently disabled."
        try:
            reader = PdfReader(self._safe_path(filename))
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text[:10000] # Cap output
        except Exception as e:
            return f"Error reading PDF: {str(e)}"

    def read_excel(self, filename):
        if not openpyxl:
            return "Error: openpyxl library not installed. Excel support is currently disabled."
        try:
            wb = openpyxl.load_workbook(self._safe_path(filename), data_only=True)
            output = ""
            for sheet in wb.worksheets:
                output += f"--- Sheet: {sheet.title} ---\n"
                for row in sheet.iter_rows(values_only=True):
                    output += "\t".join([str(cell) if cell is not None else "" for cell in row]) + "\n"
            return output[:10000] # Cap output
        except Exception as e:
            return f"Error reading Excel: {str(e)}"

    def write_file(self, filename, content):
        try:
            path = self._safe_path(filename)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"File {filename} written successfully."
        except Exception as e:
            return str(e)

    def delete_file(self, filename):
        try:
            path = self._safe_path(filename)
            if os.path.isdir(path):
                shutil.rmtree(path)
                return f"Directory {filename} and all its contents deleted."
            os.remove(path)
            return f"File {filename} deleted."
        except Exception as e:
            return str(e)

    def create_directory(self, path):
        try:
            full_path = self._safe_path(path)
            os.makedirs(full_path, exist_ok=True)
            return f"Directory '{path}' created successfully."
        except Exception as e:
            return str(e)

    def move_file(self, src, dest):
        try:
            src_path = self._safe_path(src)
            dest_path = self._safe_path(dest)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.move(src_path, dest_path)
            return f"Moved {src} to {dest}."
        except Exception as e:
            return str(e)

    def rename_file(self, old_name, new_name):
        return self.move_file(old_name, new_name)

    def web_search(self, query):
        is_termux = os.path.exists('/data/data/com.termux')
        
        # On Termux, bypass DDGS entirely to avoid process-level panics
        if not is_termux:
            try:
                with DDGS() as ddgs:
                    results = [r for r in ddgs.text(query, max_results=5)]
                    if results:
                        return "\n\n".join([f"Title: {r['title']}\nLink: {r['href']}\nSnippet: {r['body']}" for r in results])
            except Exception:
                pass # Fallback to scraper below

        # Robust Fallback Scraper (Primary on Termux)
        try:
            import requests
            from bs4 import BeautifulSoup
            
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
            url = f"https://html.duckduckgo.com/html/?q={query}"
            resp = requests.get(url, headers=headers, timeout=10)
            
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.content, "html.parser")
                results = []
                for result in soup.find_all("div", class_="result")[:5]:
                    title_tag = result.find("a", class_="result__a")
                    snippet_tag = result.find("a", class_="result__snippet")
                    if title_tag:
                        title = title_tag.get_text().strip()
                        link = title_tag.get("href")
                        snippet = snippet_tag.get_text().strip() if snippet_tag else "No snippet available."
                        results.append(f"Title: {title}\nLink: {link}\nSnippet: {snippet}")
                
                if results:
                    return "\n\n".join(results)
        except Exception as e:
            return f"Search Error: {str(e)}"
        
        return "No results found."

    def get_memory(self):
        try:
            memory_path = os.path.join(os.path.dirname(self.workspace_dir), 'common', 'memory.md')
            with open(memory_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return str(e)

    def update_memory(self, fact):
        try:
            memory_path = os.path.join(os.path.dirname(self.workspace_dir), 'common', 'memory.md')
            with open(memory_path, 'a', encoding='utf-8') as f:
                f.write(f"\n- {fact}")
            return "Memory updated."
        except Exception as e:
            return str(e)

    def fetch_youtube_transcript(self, url):
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            from urllib.parse import urlparse, parse_qs
            parsed_url = urlparse(url)
            
            video_id = None
            if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
                if parsed_url.path == '/watch':
                    video_id = parse_qs(parsed_url.query).get('v')
                    if video_id: video_id = video_id[0]
                elif parsed_url.path.startswith(('/embed/', '/v/', '/live/')):
                    video_id = parsed_url.path.split('/')[2]
            elif parsed_url.hostname == 'youtu.be':
                video_id = parsed_url.path.split('/')[1]
                
            if not video_id:
                # Fallback to simple split if hostname doesn't match expected patterns
                video_id = parsed_url.path.split('/')[-1]

            api = YouTubeTranscriptApi()
            transcript_obj = api.fetch(video_id)
            transcript_data = transcript_obj.to_raw_data()
            
            text = " ".join([t['text'] for t in transcript_data])
            return text[:4000] # Limit size to prevent token explosion
        except Exception as e:
            return f"Error fetching transcript: {str(e)}"

    def fetch_weather(self, city):
        try:
            import requests
            response = requests.get(f"https://wttr.in/{city}?format=3", timeout=5)
            return response.text.strip()
        except Exception as e:
            return f"Error fetching weather: {str(e)}"

    def web_scrape(self, url):
        try:
            from bs4 import BeautifulSoup
            import requests
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            for script in soup(["script", "style"]):
                script.extract()
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            return text[:4000] # Limit size
        except Exception as e:
            return f"Error scraping web: {str(e)}"

    def python_sandbox(self, code):
        try:
            import subprocess
            result = subprocess.run(["python", "-c", code], capture_output=True, text=True, timeout=10)
            output = result.stdout
            if result.stderr:
                output += f"\nError: {result.stderr}"
            return output[-4000:] if output else "Execution completed with no output."
        except subprocess.TimeoutExpired:
            return "Execution timed out."
        except Exception as e:
            return f"Error in sandbox: {str(e)}"

    def download_youtube(self, url, format_type="video"):
        try:
            import yt_dlp
            ydl_opts = {
                'outtmpl': os.path.join(self.workspace_dir, '%(title)s.%(ext)s'),
                'restrictfilenames': True,
                'noplaylist': True,
            }
            if format_type == "audio":
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            else:
                ydl_opts['format'] = 'bestvideo+bestaudio/best'
                ydl_opts['merge_output_format'] = 'mp4'

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                if format_type == "audio":
                    filename = filename.rsplit('.', 1)[0] + '.mp3'
                return f"Successfully downloaded media to: {os.path.basename(filename)}"
        except Exception as e:
            return f"Error downloading media (ensure ffmpeg is installed for audio/merging): {str(e)}"

    def convert_media(self, input_file, output_format):
        try:
            import subprocess
            input_path = self._safe_path(input_file)
            output_file = f"{os.path.splitext(input_file)[0]}.{output_format}"
            output_path = self._safe_path(output_file)
            
            # Check if ffmpeg exists
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            
            result = subprocess.run(['ffmpeg', '-i', input_path, output_path, '-y'], capture_output=True, text=True)
            if result.returncode == 0:
                return f"Successfully converted {input_file} to {output_file}"
            else:
                return f"FFmpeg error: {result.stderr}"
        except FileNotFoundError:
            return "Error: FFmpeg is not installed or not in system PATH."
        except Exception as e:
            return f"Error converting media: {str(e)}"

    def local_rag_search(self, query):
        try:
            import numpy as np
            from sklearn.feature_extraction.text import TfidfVectorizer
            import glob

            documents = []
            file_mapping = []
            
            search_patterns = ['*.txt', '*.md', '*.py', '*.json', '*.csv', '*.html']
            files = []
            for pattern in search_patterns:
                files.extend(glob.glob(os.path.join(self.workspace_dir, '**', pattern), recursive=True))
            
            if not files:
                return "No readable text documents found in the workspace."

            for file_path in files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        chunk_size = 1000
                        for i in range(0, len(content), chunk_size):
                            chunk = content[i:i+chunk_size]
                            if chunk.strip():
                                documents.append(chunk)
                                file_mapping.append(os.path.relpath(file_path, self.workspace_dir))
                except:
                    pass
                    
            if not documents:
                return "Could not extract text from files."

            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(documents)
            query_vec = vectorizer.transform([query])
            
            cosine_sim = (tfidf_matrix * query_vec.T).toarray().flatten()
            top_indices = cosine_sim.argsort()[-3:][::-1]
            
            results = []
            for idx in top_indices:
                if cosine_sim[idx] > 0.05:
                    results.append(f"--- File: {file_mapping[idx]} ---\n{documents[idx]}...")
                    
            if not results:
                return "No relevant information found in the workspace for this query."
                
            return "\n\n".join(results)
        except ImportError:
            return "Error: numpy or scikit-learn not installed."
        except Exception as e:
            return f"Error in RAG search: {str(e)}"

    def remind_me(self, message, time_args):
        if not self.agent: return "Agent not connected."
        # Standardize instruction for better removal later
        instruction = f"REMINDER: {message}"
        return self.agent.add_scheduled_task('interval', time_args, instruction)

    def stop_reminders(self, keyword):
        if not self.agent: return "Agent not connected."
        return self.agent.remove_scheduled_task(keyword)

    def schedule_task(self, trigger_type, schedule_args, instruction):
        if not self.agent: return "Agent not connected."
        return self.agent.add_scheduled_task(trigger_type, schedule_args, instruction)

    def list_tasks(self):
        if not self.agent: return "Agent not connected."
        jobs = self.agent.scheduler.get_jobs()
        if not jobs: return "No active scheduled tasks."
        
        task_list = []
        for job in jobs:
            task_list.append(f"ID: {job.id} | Trigger: {job.trigger} | Instruction: {job.args[2]}")
        return "\n".join(task_list)

    def remove_task(self, keyword):
        if not self.agent: return "Agent not connected."
        return self.agent.remove_scheduled_task(keyword)

    def remove_all_tasks(self):
        if not self.agent: return "Agent not connected."
        jobs = self.agent.scheduler.get_jobs()
        if not jobs: return "No active tasks to remove."
        for job in jobs:
            self.agent.scheduler.remove_job(job.id)
        self.agent._save_tasks()
        return "Success: All scheduled tasks have been terminated."
