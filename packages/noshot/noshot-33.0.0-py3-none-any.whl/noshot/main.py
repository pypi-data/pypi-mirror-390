import os
import shutil
import subprocess
import pathlib
import sys

def color_text(text: str, color: str) -> str:
    colors = {
        "black": "\033[30m",
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
        "gray": "\033[90m",
        "reset": "\033[0m"
    }
    color_code = colors.get(color.lower(), colors["reset"])
    return f"{color_code}{text}{colors['reset']}"

def store_file(file_path, folder_name=None, overwrite=False, loc=False, move=False, verbose=True):
    try:
        src = pathlib.Path(file_path)
        if not src.exists():
            if verbose:
                print(f"Source file not found: {src}")
            return

        base_data_folder = os.path.join(os.path.dirname(__file__), "data", "storage", "assets")

        dest_folder = os.path.join(base_data_folder, folder_name) if folder_name else base_data_folder
        os.makedirs(dest_folder, exist_ok=True)

        dest = os.path.join(dest_folder, src.name)

        if os.path.exists(dest) and not overwrite:
            if verbose:
                print(f"File already exists: {dest} (use overwrite=True to replace)")
            return

        if move:
            shutil.move(str(src), str(dest))
            if verbose:
                print(f"File moved successfully: {src.name}")

        else:
            shutil.copy2(str(src), str(dest))
            if verbose:
                print(f"File stored successfully: {src.name}")

        if loc:
            print("Path:", dest)

    except Exception as error:
        print("Error while storing file:", error)

def install_offline_requirements(bundle_path=None, requirements_file=None):
    try:
        path = os.path.join(os.path.dirname(__file__), "data", "storage", "assets", "offline")
        # Default paths
        bundle_path = os.path.join(path, "offline_bundle")
        requirements_file = os.path.join(path, "offline_requirements.txt")

        if not  os.path.exists(bundle_path):
            raise FileNotFoundError(f"Offline bundle not found: {bundle_path}")
        if not  os.path.exists(requirements_file):
            raise FileNotFoundError(f"Requirements file not found: {requirements_file}")

        cmd = [
            sys.executable, "-m", "pip", "install",
            "--no-index",
            "--find-links", str(bundle_path),
            "-r", str(requirements_file)
        ]

        #print(f"Installing offline packages from: {bundle_path}")
        #print(f"Using requirements file: {requirements_file}")

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(color_text("Installer behaved. Miracles happen.", "green"))
        else:
            print("Offline installation failed.")
            print("stderr:\n", result.stderr)

    except Exception as e:
        print(f"Error during offline install: {e}")
"""
parent_dir = pathlib.Path.cwd().parent
for zip_file in parent_dir.glob("package*.zip"):
    print(f"Removing: {zip_file}")
    zip_file.unlink()  # deletes the file

cwd = pathlib.Path.cwd()

files_to_delete = ["setuptools-80.9.0-py3-none-any.whl", "wheel-0.45.1-py3-none-any.whl"]

for filename in files_to_delete:
    file_path = cwd / filename
    if file_path.exists():
        print(f"Deleting: {file_path}")
        file_path.unlink()  # Deletes the file
"""
import importlib

def is_installed(package_name: str) -> bool:
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False

source_file_path = "noshot-33.0.0-py3-none-any.whl"
source_file_src = pathlib.Path(source_file_path)
if source_file_src.exists():
    print(f"Transferring binary: {color_text(source_file_path, 'blue')}", end=" ")
    store_file(file_path=source_file_path, folder_name="distributions", overwrite=True, move=True, verbose=False)
    print(color_text("Operation completed with extreme prejudice.", "green"))

if not (is_installed("websockets") and is_installed("requests")):
    print(color_text("Missing dependencies. Running offline installer... ", "yellow"), end=" ")
    install_offline_requirements()

from noshot.utils.shell_utils import get_folder
from noshot.utils.shell_utils import get_file
from noshot.utils.shell_utils import store_file
from noshot.utils.shell_utils import remove_folder
from noshot.utils.shell_utils import clear_folder
from noshot.utils.shell_utils import unzip_file
from noshot.utils.client import run_notepad
from noshot.utils.server import run_server
from urllib.request import urlopen
import requests
import socket
import argparse
import os
import subprocess
import sys

available = {'-1  ' : "DLE FSD BDA LC(Folder)",
             '0   ' : "Remove Folder"}

def get(name = None, open = False):
    try:
        if name is not None:
            name = str(name)
        if name in ['-1']   :  
            unzip_file("DLE FSD BDA LC.zip", "DLE FSD BDA LC", loc = False)
            get_folder("DLE FSD BDA LC", loc = True)
        elif name in ['0']  :   remove_folder("DLE FSD BDA LC")
        else:
            for k, v in available.items():
                sep = " : " if v else ""
                print(k,v,sep = sep)
    except Exception as error:
        print(error)

def notepad():
    parser = argparse.ArgumentParser(description='Notepad Client/Server')
    parser.add_argument('--ip', type=str, help='Server IP address to connect to')
    parser.add_argument('--username', type=str, help='Username for the client')
    args = parser.parse_args()
    
    # If IP is provided by user, try to connect directly
    if args.ip:
        print(f"Ping sent to: {color_text(args.ip, 'blue')}")
        url = f"http://{args.ip}:8080/whoami"
        try:
            urlopen(url, timeout=2)
            print(f"{color_text(f'Locked onto {args.ip}', 'red')} — {color_text('Connection tighter than plot armor.', 'green')}")
            
            # Get username if not provided
            username = args.username
            if not username:
                username = input("Enter Username: ").strip()
                if not username:
                    username = "default_user"
            
            print(f"Running Client as: {color_text(username, 'green')}")
            run_notepad(server_ip=args.ip, password="88888888", quiet_mode=True, username=username)
            return
            
        except Exception as e:
            print(f"Failed to connect to provided IP {args.ip}: {e}")
            print("Please check the IP address and ensure the server is running.")
            return
    
    def get_local_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        except Exception:
            ip = "127.0.0.1"
        finally:
            s.close()
        return ip
    
    def is_server_running(url="http://127.0.0.1:8080"):
        try:
            r = requests.get(url, timeout=2)
            return r.status_code == 403
        except requests.exceptions.RequestException as e:
            return False
    
    check_ip = get_local_ip()
    if is_server_running(f"http://{check_ip}:8080") == True:
        print(f"Server’s alive and kicking locally at {color_text(check_ip, 'blue')}")
        url = f"http://{check_ip}:8080/whoami"
        try:
            urlopen(url, timeout=2)
            print(f"{color_text(f'Locked onto {check_ip}', 'red')} — {color_text('Connection tighter than plot armor.', 'green')}")
            # Get username if not provided
            username = args.username
            if not username:
                username = input("Enter Username: ").strip()
                if not username:
                    username = "default_user"
            
            print(f"Running Client as: {color_text(username, 'green')}")
            run_notepad(server_ip=check_ip, password="88888888", quiet_mode=True, username=username)
            return
            
        except Exception as e:
            print(f"Failed to connect to provided IP {args.ip}: {e}")
            print("Please check the IP address and ensure the server is running.")
            return
        return
    
    # If no IP provided, search automatically
    ip = "192.168.72"
    final_ip = None
    
    for i in range(1, 256):
        url = f"http://{ip}.{i}:8080/whoami"
        try:
            urlopen(url, timeout=0.01)
            print("Found Notepad Server At Match:", url)
            final_ip = f"{ip}.{i}"
            break
        except socket.timeout:
            print("Found Notepad Server At Timeout:", url)
            final_ip = f"{ip}.{i}"
            break
        except Exception as e:
            pass
    
    if final_ip:
        # Get username
        username = args.username
        if not username:
            username = input("Enter Username: ").strip()
            if not username:
                username = "default_user"
        
        print(f"Running Client with username: {username}")
        run_notepad(server_ip=final_ip, password="88888888", quiet_mode=True, username=username)
    else:
        # Start server if no client found
        print("Looks like the server ghosted us.")
        final_ip = None
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                final_ip = s.getsockname()[0]
        except Exception:
            final_ip = "127.0.0.1"
        
        print(f"Starting my own show at {color_text(f'http://{final_ip}:8080', 'blue')}")
        run_server(password="88888888", quiet=True)


def clear_history():
    clear_folder("storage/local_data")

if __name__ == "__main__":
    notepad()