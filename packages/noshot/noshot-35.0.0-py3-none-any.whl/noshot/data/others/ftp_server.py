from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import os
import socket
import argparse
import signal
import sys

import pathlib

def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def start_ftp_server(port=2121, username="batman", password="88888888", shared_folder=None, quiet=False):
    if shared_folder is None:
        shared_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", pathlib.Path("DLE FSD BDA"))
    
    os.makedirs(shared_folder, exist_ok=True)
    
    authorizer = DummyAuthorizer()
    authorizer.add_user(username, password, shared_folder, perm="elradfmwMT")
    
    handler = FTPHandler
    handler.authorizer = authorizer
    handler.use_sendfile = False
    handler.timeout = 300
    handler.banner = "Python FTP Server Ready"
    handler.passive_ports = range(60000, 60100)
    
    host = get_ip_address()
    server = FTPServer((host, port), handler)

    def signal_handler(sig, frame):
        if not quiet:
            print("Stopping FTP server...")
        server.close_all()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    
    if not quiet:
        print("=" * 50)
        print("PYTHON FTP SERVER STARTED!")
        print("=" * 50)
        print(f"Server IP: {host}")
        print(f"FTP Port: {port}")
        print(f"Shared Folder: {shared_folder}")
        print(f"Folder Contents: {len(os.listdir(shared_folder))} items")
        
        try:
            items = os.listdir(shared_folder)
            if items:
                print("Folder contains:")
                for item in items[:10]:
                    item_path = os.path.join(shared_folder, item)
                    if os.path.isdir(item_path):
                        print(f"  [DIR] {item}/")
                    else:
                        size = os.path.getsize(item_path)
                        print(f"  [FILE] {item} ({size} bytes)")
                if len(items) > 10:
                    print(f"  ... and {len(items) - 10} more items")
            else:
                print("Folder is empty")
        except Exception as e:
            print(f"Error reading folder: {e}")
            
        print("Login Credentials:")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        print("=" * 50)
        print("FTP Connection Links:")
        print(f"   ftp://{host}:{port}")
        print(f"   ftp://{username}:{password}@{host}:{port}")
        print("=" * 50)
        print("Press Ctrl+C to stop the server")
        print("=" * 50)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        if not quiet:
            print("FTP Server stopped")
    except Exception as e:
        if not quiet:
            print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(description='Python FTP Server')
    parser.add_argument('-p', '--port', type=int, default=2121,
                       help='FTP server port (default: 2121)')
    parser.add_argument('-u', '--username', default='batman',
                       help='FTP username (default: batman)')
    parser.add_argument('-P', '--password', default='88888888',
                       help='FTP password (default: 88888888)')
    parser.add_argument('-d', '--directory',
                       help='Shared folder path (default: ~/Downloads/Test/data)')
    parser.add_argument('-q', '--quiet', action='store_true',
                       help='Enable quiet mode (suppress terminal output)')
    
    args = parser.parse_args()
    
    start_ftp_server(
        port=args.port,
        username=args.username,
        password=args.password,
        shared_folder=args.directory,
        quiet=args.quiet
    )

if __name__ == "__main__":
    main()