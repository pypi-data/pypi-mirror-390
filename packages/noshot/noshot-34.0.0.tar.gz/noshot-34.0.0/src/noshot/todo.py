import os
import shutil
import subprocess
import pathlib
import sys

def store_file(file_path, folder_name=None, overwrite=False, loc=False, move=False):
    try:
        src = pathlib.Path(file_path)
        if not src.exists():
            print(f"Source file not found: {src}")
            return

        base_data_folder = os.path.join(os.path.dirname(__file__), "data", "storage", "assets")

        dest_folder = os.path.join(base_data_folder, folder_name) if folder_name else base_data_folder
        os.makedirs(dest_folder, exist_ok=True)

        dest = os.path.join(dest_folder, src.name)

        if os.path.exists(dest) and not overwrite:
            print(f"File already exists: {dest} (use overwrite=True to replace)")
            return

        if move:
            shutil.move(str(src), str(dest))
            print(f"File moved successfully: {src.name}")
        else:
            shutil.copy2(str(src), str(dest))
            print(f"File stored successfully: {src.name}")

        if loc:
            print("Path:", dest)

    except Exception as error:
        print("Error while storing file:", error)

def install_offline_requirements(bundle_path=None, requirements_file=None):
    try:
        store_file(file_path="noshot-28.0.0.tar.gz", folder_name="distributions", overwrite=True, loc=True, move=True)
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

        print(f"Installing offline packages from: {bundle_path}")
        print(f"Using requirements file: {requirements_file}")

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("Offline installation successful.")
        else:
            print("Offline installation failed.")
            print("stderr:\n", result.stderr)

    except Exception as e:
        print(f"Error during offline install: {e}")

if __name__ == "__main__":
    pass