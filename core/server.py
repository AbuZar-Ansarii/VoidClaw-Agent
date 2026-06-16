import os
import yaml
import json
import logging
import asyncio
import webbrowser
import queue
from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
from werkzeug.utils import secure_filename
from waitress import serve

app = Flask(__name__, static_folder='web')
CORS(app)

# Global agent instance and multi-client notification system
agent = None
clients = []

# Configure upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'workspace')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')
    
    def generate():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        gen = agent.process_message_stream(user_message)
        
        try:
            while True:
                try:
                    chunk = loop.run_until_complete(gen.__anext__())
                    yield f"data: {chunk}\n\n"
                except StopAsyncIteration:
                    break
        finally:
            loop.close()
            
    return Response(generate(), mimetype='text/event-stream')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({'message': f'File {filename} uploaded to workspace.'})

@app.route('/settings', methods=['GET', 'POST'])
def handle_settings():
    if request.method == 'GET':
        return jsonify(agent.get_settings())
    
    data = request.json
    new_prompt = data.get('system_prompt')
    new_temp = data.get('temperature')
    
    if new_prompt is not None:
        user_md_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'common', 'user.md')
        with open(user_md_path, 'w', encoding='utf-8') as f:
            f.write(new_prompt)
            
    if new_temp is not None:
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'common', 'config.yaml')
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        provider = config.get('default_provider', 'ollama')
        if provider in config:
            config[provider]['temperature'] = float(new_temp)
            
        with open(config_path, 'w') as f:
            yaml.dump(config, f)
            
    agent.reload_config()
    return jsonify({'message': 'Settings updated successfully.'})

@app.route('/history', methods=['GET'])
def history():
    chats_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'common', 'chats')
    if not os.path.exists(chats_dir):
        return jsonify([])
    logs = sorted([f for f in os.listdir(chats_dir) if f.endswith('.md')], reverse=True)
    return jsonify(logs)

@app.route('/chat-detail/<filename>', methods=['GET'])
def chat_detail(filename):
    chats_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'common', 'chats')
    file_path = os.path.join(chats_dir, filename)
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return jsonify({'content': content})

@app.route('/status', methods=['GET'])
def status():
    return jsonify({
        'provider': agent.config['default_provider'],
        'model': agent.config[agent.config['default_provider']]['model'],
        'channels': ['Terminal', 'Web UI'] + (['Telegram'] if agent.config.get('telegram_token') != "YOUR_TELEGRAM_BOT_TOKEN" else [])
    })

@app.route('/dashboard-stats', methods=['GET'])
def dashboard_stats():
    return jsonify(agent.get_dashboard_stats())

@app.route('/new-session', methods=['POST'])
def new_session():
    msg = agent.clear_session()
    return jsonify({'message': msg})

@app.route('/stop', methods=['POST'])
def stop_generation():
    agent.interrupted = True
    return jsonify({'message': 'Interruption signal sent.'})

@app.route('/notifications')
def notifications():
    def stream():
        q = queue.Queue()
        clients.append(q)
        try:
            while True:
                try:
                    # Block for 20s to wait for message, then send keep-alive
                    msg = q.get(timeout=20)
                    yield f"data: {json.dumps(msg)}\n\n"
                except queue.Empty:
                    yield ": keep-alive\n\n"
        finally:
            if q in clients:
                clients.remove(q)
    return Response(stream(), mimetype='text/event-stream')

def push_notification(content):
    for q in clients:
        q.put({'content': content})

@app.route('/delete-session/<filename>', methods=['DELETE'])
def delete_session(filename):
    chats_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'common', 'chats')
    file_path = os.path.join(chats_dir, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({'message': f'Session {filename} deleted.'})
    return jsonify({'error': 'File not found'}), 404

def get_free_port(start_port):
    import socket
    port = start_port
    while port < start_port + 10:
        with socket.socket(socket.socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('0.0.0.0', port))
                return port
            except OSError:
                port += 1
    return start_port

def start_web_server(agent_instance, port=5000):
    global agent
    agent = agent_instance
    
    # Robust port selection (Fixed for macOS AirPlay conflict)
    final_port = get_free_port(port)
    
    print(f"\n\033[38;5;214m[WEB]\033[0m UI Server starting on http://localhost:{final_port} (Production Mode)")
    
    # Only open browser if not in Termux (to avoid error messages)
    if not os.path.exists('/data/data/com.termux'):
        try:
            webbrowser.open(f"http://localhost:{final_port}")
        except: pass
        
    serve(app, host='0.0.0.0', port=final_port, _quiet=True)

if __name__ == '__main__':
    pass
