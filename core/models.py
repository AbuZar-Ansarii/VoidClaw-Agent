import os
import requests
import json
import ollama
import asyncio

class LLMAdapter:
    def __init__(self, config):
        self.config = config
        self.provider = config.get('default_provider', 'ollama')

    async def generate_response(self, prompt, system_prompt=""):
        # Run synchronous generate methods in a thread to avoid blocking the event loop
        if self.provider == 'ollama':
            return await asyncio.to_thread(self._ollama_generate, prompt, system_prompt)
        elif self.provider == 'openai':
            return await asyncio.to_thread(self._openai_generate, prompt, system_prompt)
        elif self.provider == 'gemini':
            return await asyncio.to_thread(self._gemini_generate, prompt, system_prompt)
        elif self.provider == 'anthropic':
            return await asyncio.to_thread(self._anthropic_generate, prompt, system_prompt)
        elif self.provider == 'openrouter':
            return await asyncio.to_thread(self._openrouter_generate, prompt, system_prompt)
        elif self.provider == 'nvidia':
            return await asyncio.to_thread(self._nvidia_generate, prompt, system_prompt)
        return "Error: Unknown Provider"

    async def generate_stream(self, prompt, system_prompt=""):
        if self.provider == 'ollama':
            client = ollama.AsyncClient(host=self.config['ollama']['host'])
            async for chunk in await client.chat(model=self.config['ollama']['model'], messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': prompt},
            ], stream=True):
                yield chunk['message']['content']
        
        elif self.provider == 'openai':
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {self.config['openai']['api_key']}", "Content-Type": "application/json"}
            data = {"model": self.config['openai']['model'], "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}], "stream": True}
            response = requests.post(url, headers=headers, json=data, stream=True)
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith("data: ") and line != "data: [DONE]":
                        try:
                            chunk = json.loads(line[6:])
                            content = chunk['choices'][0]['delta'].get('content', '')
                            if content: yield content
                        except: pass
        
        elif self.provider == 'gemini':
            # Gemini streaming via REST is a bit different, using a simplified poll for now or full content
            # For brevity in this task, we'll simulate streaming for Gemini if full response only
            full_resp = self._gemini_generate(prompt, system_prompt)
            for word in full_resp.split(' '):
                yield word + ' '
                await asyncio.sleep(0.02)
        
        else:
            # Fallback for others
            full_resp = await self.generate_response(prompt, system_prompt)
            yield full_resp

    def _ollama_generate(self, prompt, system_prompt):
        try:
            client = ollama.Client(host=self.config['ollama']['host'])
            response = client.chat(model=self.config['ollama']['model'], messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': prompt},
            ])
            return response['message']['content']
        except Exception as e:
            return f"Error connecting to Ollama: {str(e)}. Make sure Ollama is running at {self.config['ollama']['host']}"

    def _openai_generate(self, prompt, system_prompt):
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config['openai']['api_key']}"
        }
        data = {
            "model": self.config['openai']['model'],
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        return f"OpenAI Error: {response.text}"

    def _gemini_generate(self, prompt, system_prompt):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.config['gemini']['model']}:generateContent?key={self.config['gemini']['api_key']}"
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{
                "parts": [{"text": f"{system_prompt}\n\nUser: {prompt}"}]
            }]
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            try:
                return response.json()['candidates'][0]['content']['parts'][0]['text']
            except (KeyError, IndexError):
                return f"Gemini Parsing Error: {response.text}"
        return f"Gemini Error: {response.text}"

    def _anthropic_generate(self, prompt, system_prompt):
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.config['anthropic']['api_key'],
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        data = {
            "model": self.config['anthropic']['model'],
            "max_tokens": 1024,
            "system": system_prompt,
            "messages": [{"role": "user", "content": prompt}]
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['content'][0]['text']
        return f"Anthropic Error: {response.text}"

    def _openrouter_generate(self, prompt, system_prompt):
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.config['openrouter']['api_key']}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.config['openrouter']['model'],
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        return f"OpenRouter Error: {response.text}"

    def _nvidia_generate(self, prompt, system_prompt):
        url = "https://integrate.api.nvidia.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.config['nvidia']['api_key']}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.config['nvidia']['model'],
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        return f"NVIDIA NIM Error: {response.text}"
