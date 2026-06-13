import os
import shutil
from duckduckgo_search import DDGS

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
            "read_file": self.read_file,
            "write_file": self.write_file,
            "delete_file": self.delete_file,
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
            "remove_task": self.remove_task
        }
        if tool_name in tools:
            return tools[tool_name](**args)
        return f"Tool {tool_name} not found."

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

    def read_file(self, filename):
        try:
            with open(self._safe_path(filename), 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return str(e)

    def write_file(self, filename, content):
        try:
            with open(self._safe_path(filename), 'w', encoding='utf-8') as f:
                f.write(content)
            return f"File {filename} written successfully."
        except Exception as e:
            return str(e)

    def delete_file(self, filename):
        try:
            os.remove(self._safe_path(filename))
            return f"File {filename} deleted."
        except Exception as e:
            return str(e)

    def web_search(self, query):
        try:
            with DDGS() as ddgs:
                results = [r for r in ddgs.text(query, max_results=5)]
                return "\n\n".join([f"Title: {r['title']}\nLink: {r['href']}\nSnippet: {r['body']}" for r in results])
        except Exception as e:
            return str(e)

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

    def remove_task(self, task_id):
        if not self.agent: return "Agent not connected."
        return self.agent.remove_scheduled_task(task_id)
