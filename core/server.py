import os
import yaml
import json
import logging
import asyncio
import webbrowser
from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
from werkzeug.utils import secure_filename
from waitress import serve

app = Flask(__name__, static_folder='web')
CORS(app)

# Global agent instance and notification queue
agent = None
notification_queue = asyncio.Queue()

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

@app.route('/settings', methods=['POST'])
def update_settings():
    data = request.json
    new_prompt = data.get('system_prompt')
    if new_prompt:
        user_md_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'common', 'user.md')
        with open(user_md_path, 'w', encoding='utf-8') as f:
            f.write(new_prompt)
        agent.reload_config()
        return jsonify({'message': 'System prompt updated.'})
    return jsonify({'error': 'No data provided'}), 400

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

@app.route('/new-session', methods=['POST'])
def new_session():
    msg = agent.clear_session()
    return jsonify({'message': msg})

@app.route('/notifications')
def notifications():
    def stream():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        while True:
            try:
                # We use a small timeout to allow checking for disconnects
                msg = loop.run_until_complete(notification_queue.get())
                yield f"data: {json.dumps(msg)}\n\n"
            except:
                break
    return Response(stream(), mimetype='text/event-stream')

def push_notification(content):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(notification_queue.put({'content': content}))
    loop.close()

@app.route('/delete-session/<filename>', methods=['DELETE'])
def delete_session(filename):
    chats_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'common', 'chats')
    file_path = os.path.join(chats_dir, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({'message': f'Session {filename} deleted.'})
    return jsonify({'error': 'File not found'}), 404

def start_web_server(agent_instance, port=5000):
    global agent
    agent = agent_instance
    print(f"\n\033[38;5;214m[WEB]\033[0m UI Server starting on http://localhost:{port} (Production Mode)")
    webbrowser.open(f"http://localhost:{port}")
    serve(app, host='0.0.0.0', port=port, _quiet=True)

if __name__ == '__main__':
    pass
