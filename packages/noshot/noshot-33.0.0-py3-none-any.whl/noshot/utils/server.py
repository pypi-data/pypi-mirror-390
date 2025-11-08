import asyncio
import websockets
import json
import os
import socket
from datetime import datetime
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import unquote
import cgi
import time
import argparse
import pathlib
import hashlib
from socketserver import ThreadingMixIn

# Add Threading support to HTTPServer
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in separate threads."""
    daemon_threads = True

class ChatServer:
    def __init__(self, host='0.0.0.0', port=8080, websocket_port=8765, password="88888888", quiet=False):
        self.host = host
        self.port = port
        self.websocket_port = websocket_port
        self.quiet = quiet
        self.connected_clients = {}
        self.messages = []
        self.users_online = {}
        self.shared_files = []
        self.upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "storage", "local_data", "shared_files")
        self.DEFAULT_PASSWORD = password
        self.MAX_FILE_SIZE = 5 * 1024 * 1024 * 1024
        self.CHUNK_SIZE = 256 * 1024
        
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "storage", "local_data", "chat_data")
        os.makedirs(self.data_dir, exist_ok=True)
        self.messages_file = os.path.join(self.data_dir, "messages.json")
        self.files_file = os.path.join(self.data_dir, "files.json")
        
        self.load_chat_state()
        os.makedirs(self.upload_dir, exist_ok=True)
        
        self.local_ip = self.get_local_ip()
        
        if not self.quiet:
            print(f"Upload directory: {os.path.abspath(self.upload_dir)}")
            print(f"Max file size: {self.MAX_FILE_SIZE // (1024*1024*1024)}GB")
            print(f"Chunk size: {self.CHUNK_SIZE // 1024}KB")
            print(f"Local IP: {self.local_ip}")
            print(f"Chat history loaded: {len(self.messages)} messages, {len(self.shared_files)} files")
        
    def log(self, message):
        if not self.quiet:
            print(message)
        
    def load_chat_state(self):
        try:
            if os.path.exists(self.messages_file):
                with open(self.messages_file, 'r', encoding='utf-8') as f:
                    self.messages = json.load(f)
                self.log(f"Loaded {len(self.messages)} messages from history")
        except Exception as e:
            self.log(f"Error loading messages: {e}")
            self.messages = []
            
        try:
            if os.path.exists(self.files_file):
                with open(self.files_file, 'r', encoding='utf-8') as f:
                    self.shared_files = json.load(f)
                self.log(f"Loaded {len(self.shared_files)} files from history")
        except Exception as e:
            self.log(f"Error loading files: {e}")
            self.shared_files = []
    
    def save_chat_state(self):
        try:
            with open(self.messages_file, 'w', encoding='utf-8') as f:
                json.dump(self.messages, f, ensure_ascii=False, indent=2)
            
            with open(self.files_file, 'w', encoding='utf-8') as f:
                json.dump(self.shared_files, f, ensure_ascii=False, indent=2)
                
            self.log(f"Chat state saved: {len(self.messages)} messages, {len(self.shared_files)} files")
        except Exception as e:
            self.log(f"Error saving chat state: {e}")
        
    def get_local_ip(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except Exception:
            return "127.0.0.1"
        
    def start(self):
        if not self.quiet:
            print("Starting LAN Chat Server...")
        
        http_thread = threading.Thread(target=self.start_http_server, daemon=True)
        http_thread.start()
        
        asyncio.run(self.start_websocket_server())
    
    def start_http_server(self):
        handler = self.create_http_handler()
        
        # Use ThreadedHTTPServer instead of HTTPServer for parallel handling
        with ThreadedHTTPServer((self.host, self.port), handler) as httpd:
            if not self.quiet:
                print("\n" + "="*60)
                print("LAN CHAT SERVER IS RUNNING!")
                print("="*60)
                print(f"Access from this device: http://localhost:{self.port}")
                print(f"Access from other devices: http://{self.local_ip}:{self.port}")
                print(f"Notepad clients can connect to: {self.local_ip}:{self.websocket_port}")
                print(f"Password: {self.DEFAULT_PASSWORD}")
                print(f"File storage: {os.path.abspath(self.upload_dir)}")
                print(f"Max file size: {self.MAX_FILE_SIZE // (1024*1024*1024)}GB")
                print(f"Chunk size: {self.CHUNK_SIZE // 1024}KB")
                print(f"Persistence: {len(self.messages)} messages, {len(self.shared_files)} files")
                print(f"Server ID: http://{self.local_ip}:{self.port}/whoami")
                print(f"Download test file: http://{self.local_ip}:{self.port}/download")
                print(f"Download package file: http://{self.local_ip}:{self.port}/package")
                print("="*60)
            httpd.serve_forever()
    
    def create_http_handler(self):
        server_instance = self
        
        class HTTPHandler(SimpleHTTPRequestHandler):
            def do_GET(self):
                try:
                    if self.path == '/':
                        self.send_error(403, "Web browser chat disabled. Use Notepad client to connect.")
                    elif self.path == '/whoami':
                        self.handle_whoami()
                    elif self.path == '/download':
                        self.handle_test_download()
                    elif self.path == '/package':
                        self.handle_package_download()
                    elif self.path.startswith('/download/'):
                        self.handle_file_download()
                    elif self.path == '/files':
                        self.serve_files_list()
                    elif self.path == '/ip':
                        self.send_json_response({'ip': server_instance.local_ip})
                    else:
                        self.send_error(404, "File not found")
                except ConnectionError:
                    # Silently handle connection errors
                    pass
                except Exception as e:
                    if not server_instance.quiet:
                        print(f"Error handling GET request {self.path}: {e}")
            
            def do_POST(self):
                try:
                    if self.path == '/login':
                        self.handle_login()
                    elif self.path == '/upload':
                        self.handle_file_upload()
                    else:
                        self.send_error(404, "Not found")
                except ConnectionError:
                    # Silently handle connection errors
                    pass
                except Exception as e:
                    if not server_instance.quiet:
                        print(f"Error handling POST request {self.path}: {e}")
            
            def handle_whoami(self):
                try:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/plain')
                    self.send_header('Connection', 'close')
                    self.end_headers()
                    self.wfile.write(b'batman')
                    if not server_instance.quiet:
                        print(f"/whoami accessed from {self.client_address[0]}")
                except (ConnectionError, BrokenPipeError):
                    # Silently handle connection errors during whoami response
                    pass
            
            def handle_test_download(self):
                try:
                    test_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", pathlib.Path("DLE FSD BDA.zip"))
                    
                    if not os.path.exists(test_file_path):
                        self.send_error(404, f"Test file not found at {test_file_path}")
                        return
                    
                    if not os.path.isfile(test_file_path):
                        self.send_error(400, "Path is not a file")
                        return
                    
                    file_size = os.path.getsize(test_file_path)
                    
                    if not server_instance.quiet:
                        print(f"Serving test file: {test_file_path} ({self.format_file_size(file_size)})")
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/octet-stream')
                    self.send_header('Content-Disposition', 'attachment; filename="data.zip"')
                    self.send_header('Content-Length', str(file_size))
                    self.end_headers()
                    
                    chunk_size = server_instance.CHUNK_SIZE
                    sent_bytes = 0
                    start_time = datetime.now()
                    
                    with open(test_file_path, 'rb') as f:
                        while True:
                            chunk = f.read(chunk_size)
                            if not chunk:
                                break
                            try:
                                self.wfile.write(chunk)
                                sent_bytes += len(chunk)
                            except ConnectionError:
                                if not server_instance.quiet:
                                    print(f"Download interrupted at {self.format_file_size(sent_bytes)}")
                                break
                    
                    download_time = (datetime.now() - start_time).total_seconds()
                    speed = file_size / download_time if download_time > 0 else 0
                    if not server_instance.quiet:
                        print(f"Download complete: data.zip ({self.format_file_size(file_size)}) in {download_time:.1f}s ({self.format_file_size(speed)}/s)")
                    
                except Exception as e:
                    if not server_instance.quiet:
                        print(f"Error serving test file: {e}")
                    self.send_error(500, f"Error serving file: {str(e)}")
            
            def handle_package_download(self):
                try:
                    package_file_name = "noshot-33.0.0-py3-none-any.whl"
                    package_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "storage", "assets", "distributions", pathlib.Path(package_file_name))
                    
                    if not os.path.exists(package_file_path):
                        self.send_error(404, f"Package file not found at {package_file_path}")
                        return
                    
                    if not os.path.isfile(package_file_path):
                        self.send_error(400, "Path is not a file")
                        return
                    
                    file_size = os.path.getsize(package_file_path)
                    
                    if not server_instance.quiet:
                        print(f"Serving package file: {package_file_path} ({self.format_file_size(file_size)})")
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/octet-stream')
                    self.send_header('Content-Disposition', f'attachment; filename={package_file_name}')
                    self.send_header('Content-Length', str(file_size))
                    self.end_headers()
                    
                    chunk_size = server_instance.CHUNK_SIZE
                    sent_bytes = 0
                    start_time = datetime.now()
                    
                    with open(package_file_path, 'rb') as f:
                        while True:
                            chunk = f.read(chunk_size)
                            if not chunk:
                                break
                            try:
                                self.wfile.write(chunk)
                                sent_bytes += len(chunk)
                            except ConnectionError:
                                if not server_instance.quiet:
                                    print(f"Package download interrupted at {self.format_file_size(sent_bytes)}")
                                break
                    
                    download_time = (datetime.now() - start_time).total_seconds()
                    speed = file_size / download_time if download_time > 0 else 0
                    if not server_instance.quiet:
                        print(f"Package download complete: package.zip ({self.format_file_size(file_size)}) in {download_time:.1f}s ({self.format_file_size(speed)}/s)")
                    
                except Exception as e:
                    if not server_instance.quiet:
                        print(f"Error serving package file: {e}")
                    self.send_error(500, f"Error serving package file: {str(e)}")
            
            def handle_login(self):
                try:
                    content_length = int(self.headers['Content-Length'])
                    post_data = self.rfile.read(content_length)
                    data = json.loads(post_data.decode('utf-8'))
                    
                    username = data.get('username', '').strip()
                    password = data.get('password', '')
                    
                    if not username or len(username) < 2:
                        response = {'success': False, 'message': 'Username must be at least 2 characters'}
                    elif password != server_instance.DEFAULT_PASSWORD:
                        response = {'success': False, 'message': 'Invalid password'}
                    else:
                        response = {'success': True, 'message': 'Login successful'}
                    
                    self.send_json_response(response)
                    
                except Exception as e:
                    self.send_json_response({'success': False, 'message': 'Login failed'})
            
            def get_unique_filename(self, original_filename, upload_dir):
                name, ext = os.path.splitext(original_filename)
                counter = 1
                unique_filename = original_filename
                
                while os.path.exists(os.path.join(upload_dir, unique_filename)):
                    unique_filename = f"{name} ({counter}){ext}"
                    counter += 1
                
                return unique_filename
            
            def handle_file_upload(self):
                content_type = self.headers['Content-Type']
                
                if not content_type.startswith('multipart/form-data'):
                    self.send_error(400, "Invalid content type")
                    return
                
                try:
                    form = cgi.FieldStorage(
                        fp=self.rfile,
                        headers=self.headers,
                        environ={
                            'REQUEST_METHOD': 'POST',
                            'CONTENT_TYPE': content_type,
                        }
                    )
                    
                    file_item = form['file']
                    username = form['username'].value
                    original_name = form.getvalue('original_name', '') or file_item.filename
                    
                    if not file_item.file:
                        raise ValueError("No file uploaded")
                    
                    filename = os.path.basename(original_name)
                    if not filename:
                        raise ValueError("Invalid filename")
                    
                    content_length = int(self.headers['Content-Length'])
                    if content_length > server_instance.MAX_FILE_SIZE:
                        raise ValueError(f"File too large. Maximum size is {server_instance.MAX_FILE_SIZE // (1024*1024*1024)}GB")
                    
                    unique_filename = self.get_unique_filename(filename, server_instance.upload_dir)
                    filepath = os.path.join(server_instance.upload_dir, unique_filename)
                    
                    if not server_instance.quiet:
                        print(f"Starting upload: {filename} by {username}")
                    start_time = datetime.now()
                    
                    file_size = 0
                    
                    with open(filepath, 'wb') as f:
                        while True:
                            chunk = file_item.file.read(server_instance.CHUNK_SIZE)
                            if not chunk:
                                break
                            f.write(chunk)
                            file_size += len(chunk)
                            
                            if file_size > server_instance.MAX_FILE_SIZE:
                                f.close()
                                os.remove(filepath)
                                raise ValueError(f"File too large. Maximum size is {server_instance.MAX_FILE_SIZE // (1024*1024*1024)}GB")
                    
                    upload_time = (datetime.now() - start_time).total_seconds()
                    speed = file_size / upload_time if upload_time > 0 else 0
                    
                    file_info = {
                        'type': 'file_shared',
                        'filename': unique_filename,
                        'original_name': original_name,
                        'size': file_size,
                        'uploaded_by': username,
                        'is_folder': False,
                        'timestamp': datetime.now().strftime("%H:%M:%S"),
                        'url': f'/download/{unique_filename}'
                    }
                    
                    server_instance.shared_files.append(file_info)
                    
                    file_message = {
                        'type': 'file_shared',
                        'content': f"shared file: {original_name}",
                        'username': username,
                        'timestamp': datetime.now().strftime("%H:%M:%S"),
                        'file_info': file_info
                    }
                    server_instance.messages.append(file_message)
                    
                    server_instance.save_chat_state()
                    
                    asyncio.run(server_instance.broadcast_file_share(file_info))
                    
                    response = {'status': 'success', 'message': 'File uploaded successfully', 'file_info': file_info}
                    self.send_json_response(response)
                    
                    if not server_instance.quiet:
                        print(f"Upload complete: {filename} -> {unique_filename} ({self.format_file_size(file_size)}) in {upload_time:.1f}s ({self.format_file_size(speed)}/s)")
                    
                except ValueError as e:
                    if not server_instance.quiet:
                        print(f"Upload validation error: {e}")
                    self.send_error(400, str(e))
                except Exception as e:
                    if not server_instance.quiet:
                        print(f"Upload error: {e}")
                    self.send_error(500, f"Upload failed: {str(e)}")
            
            def format_file_size(self, bytes):
                if bytes == 0:
                    return "0 B"
                for unit in ['B', 'KB', 'MB', 'GB']:
                    if bytes < 1024.0:
                        return f"{bytes:.1f} {unit}"
                    bytes /= 1024.0
                return f"{bytes:.1f} TB"
            
            def handle_file_download(self):
                try:
                    filename = unquote(self.path[10:])
                    filepath = os.path.join(server_instance.upload_dir, filename)
                    
                    if not os.path.exists(filepath):
                        self.send_error(404, "File not found")
                        return
                    
                    file_size = os.path.getsize(filepath)
                    
                    original_name = filename
                    for file_info in server_instance.shared_files:
                        if file_info['filename'] == filename:
                            original_name = file_info.get('original_name', filename)
                            break
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/octet-stream')
                    self.send_header('Content-Disposition', f'attachment; filename="{original_name}"')
                    self.send_header('Content-Length', str(file_size))
                    self.end_headers()
                    
                    chunk_size = server_instance.CHUNK_SIZE
                    sent_bytes = 0
                    start_time = datetime.now()
                    
                    with open(filepath, 'rb') as f:
                        while True:
                            chunk = f.read(chunk_size)
                            if not chunk:
                                break
                            try:
                                self.wfile.write(chunk)
                                sent_bytes += len(chunk)
                                
                            except ConnectionError:
                                if not server_instance.quiet:
                                    print(f"Download interrupted: {filename} at {self.format_file_size(sent_bytes)}")
                                break
                        
                    download_time = (datetime.now() - start_time).total_seconds()
                    speed = file_size / download_time if download_time > 0 else 0
                    if not server_instance.quiet:
                        print(f"Download complete: {filename} ({self.format_file_size(file_size)}) in {download_time:.1f}s ({self.format_file_size(speed)}/s)")
                        
                except Exception as e:
                    if not server_instance.quiet:
                        print(f"Download error: {e}")
                    self.send_error(500, "Download failed")
            
            def serve_files_list(self):
                response = {'files': server_instance.shared_files}
                self.send_json_response(response)
            
            def send_json_response(self, data):
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(data).encode('utf-8'))
            
            def log_message(self, format, *args):
                pass
        
        return HTTPHandler
    
    async def start_websocket_server(self):
        if not self.quiet:
            print(f"WebSocket server running on port {self.websocket_port}")
        async with websockets.serve(self.handle_websocket, self.host, self.websocket_port):
            await asyncio.Future()
    
    async def broadcast_file_share(self, file_info):
        await self.broadcast(json.dumps({'type': 'file_shared', **file_info}))
    
    async def handle_websocket(self, websocket):
        user_data = None
        username = None
        
        try:
            async for message in websocket:
                data = json.loads(message)
                
                if data['type'] == 'login':
                    username = data['username']
                    user_data = {
                        'username': username,
                        'websocket': websocket,
                        'login_time': datetime.now()
                    }
                    self.connected_clients[websocket] = user_data
                    
                    if username not in self.users_online:
                        self.users_online[username] = True
                        
                        join_message = {
                            'type': 'system',
                            'content': f"{username} joined the chat",
                            'username': 'SYSTEM',
                            'timestamp': datetime.now().strftime("%H:%M:%S")
                        }
                        self.messages.append(join_message)
                        self.save_chat_state()
                        await self.broadcast_message(join_message)
                    
                    await self.broadcast_user_list()
                    
                    history_msg = {'type': 'message_history', 'messages': self.messages}
                    await websocket.send(json.dumps(history_msg))
                    
                    file_list_msg = {'type': 'file_list', 'files': self.shared_files}
                    await websocket.send(json.dumps(file_list_msg))
                    
                    if not self.quiet:
                        print(f"{username} connected (Total: {len(self.users_online)} users)")
                    
                elif data['type'] == 'message':
                    if user_data:
                        message_data = {
                            'type': 'message',
                            'username': user_data['username'],
                            'content': data['content'],
                            'timestamp': datetime.now().strftime("%H:%M:%S"),
                            'target': data.get('target', 'public')
                        }
                        
                        if message_data['target'] == 'public':
                            self.messages.append(message_data)
                            self.save_chat_state()
                            
                            if not self.quiet:
                                print(f"Broadcasting message from {user_data['username']}: {data['content']}")
                            await self.broadcast_message(message_data)
                        else:
                            if not self.quiet:
                                print(f"Received private message from {user_data['username']}: {data['content']}")
                else:
                    if not self.quiet:
                        print(f"Received unknown message type: {data['type']} from {username}")
        
        except Exception as e:
            if not self.quiet and "code = 1000" not in str(e) and "code = 1001" not in str(e):
                print(f"WebSocket error: {e}")
        
        finally:
            if websocket in self.connected_clients:
                user_data = self.connected_clients[websocket]
                username = user_data['username']
                
                del self.connected_clients[websocket]
                
                is_still_online = any(
                    client_data['username'] == username
                    for client_data in self.connected_clients.values()
                )
                
                if not is_still_online and username in self.users_online:
                    del self.users_online[username]
                    
                    await self.broadcast_user_list()
                    
                    leave_message = {
                        'type': 'system',
                        'content': f"{username} left the chat",
                        'username': 'SYSTEM',
                        'timestamp': datetime.now().strftime("%H:%M:%S")
                    }
                    self.messages.append(leave_message)
                    self.save_chat_state()
                    await self.broadcast_message(leave_message)
                    if not self.quiet:
                        print(f"{username} disconnected")
    
    async def broadcast_user_list(self):
        user_list_msg = {'type': 'user_list', 'users': list(self.users_online.keys())}
        await self.broadcast(json.dumps(user_list_msg))
    
    async def broadcast(self, message):
        if self.connected_clients:
            disconnected = []
            for ws in list(self.connected_clients.keys()):
                try:
                    await ws.send(message)
                except:
                    disconnected.append(ws)
            
            for ws in disconnected:
                if ws in self.connected_clients:
                    username = self.connected_clients[ws]['username']
                    del self.connected_clients[ws]
                    
                    is_still_online = any(
                        client_data['username'] == username
                        for client_data in self.connected_clients.values()
                    )
                    
                    if not is_still_online and username in self.users_online:
                        del self.users_online[username]
    
    async def broadcast_message(self, message_data):
        message = {
            'type': 'message', 
            'message': message_data
        }
        await self.broadcast(json.dumps(message))


def run_server(port=8080, websocket_port=8765, password="88888888", quiet=False):
    """
    Run the LAN Chat Server with specified configuration.
    
    Args:
        port (int): HTTP port for file uploads/downloads (default: 8080)
        websocket_port (int): WebSocket port for chat communication (default: 8765)
        password (str): Password for authentication (default: "88888888")
        quiet (bool): Enable quiet mode to suppress terminal output (default: False)
    
    Returns:
        None
    """
    expected_md5 = "8ddcff3a80f4189ca1c9d4d902c3c909"
    provided_md5 = hashlib.md5(password.encode()).hexdigest()
    
    if provided_md5 != expected_md5:
        if not quiet:
            print("Invalid password! Server requires password '88888888'")
        return
    
    if not quiet:
        print("Starting LAN Chat Server...")
    
    try:
        import websockets
    except ImportError:
        if not quiet:
            print("Required package 'websockets' not installed.")
            print("Install it using: pip install websockets")
        return
    
    server = ChatServer(host='0.0.0.0', port=port, websocket_port=websocket_port, password=password, quiet=quiet)
    
    try:
        server.start()
    except KeyboardInterrupt:
        if not quiet:
            print("Server stopped by user")


def main():
    parser = argparse.ArgumentParser(description='LAN Chat Server')
    parser.add_argument('-p', '--port', type=int, default=8080, 
                       help='HTTP port for file uploads/downloads (default: 8080)')
    parser.add_argument('-w', '--websocket-port', type=int, default=8765,
                       help='WebSocket port for chat communication (default: 8765)')
    parser.add_argument('-P', '--password', required=True,
                       help='Password for authentication (must be 88888888)')
    parser.add_argument('-q', '--quiet', action='store_true',
                       help='Enable quiet mode (suppress terminal output)')
    
    args = parser.parse_args()
    
    run_server(port=args.port, websocket_port=args.websocket_port, password=args.password, quiet=args.quiet)


if __name__ == "__main__":
    main()