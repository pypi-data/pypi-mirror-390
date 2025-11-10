import os
import shutil
import subprocess
import pathlib
import sys
import zipfile

def get_folder(folder_path, loc = False):
    src = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", pathlib.Path(folder_path))
    try:
        dest = os.path.join(os.getcwd(), pathlib.Path(folder_path))
        shutil.copytree(src, dest, symlinks=False, copy_function = shutil.copy2,
                        ignore=shutil.ignore_patterns('.ipynb_checkpoints', '__init__.py', '__pycache__'),
                        ignore_dangling_symlinks=False, dirs_exist_ok=True)
    except:
        try:
            dest = os.path.join(os.path.expanduser('~'), "Downloads", pathlib.Path(folder_path))
            shutil.copytree(src, dest, symlinks=False, copy_function = shutil.copy2,
                            ignore=shutil.ignore_patterns('.ipynb_checkpoints', '__init__.py', '__pycache__'),
                            ignore_dangling_symlinks=False, dirs_exist_ok=True)
        except Exception as error:
            print(error)
            return
    finally:
        if loc:
            print("Path:",dest)

def get_file(file_path, loc = False, open = False):
    src = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", pathlib.Path(file_path))
    try:
        dest = os.path.join(os.getcwd(), pathlib.Path(file_path).name)
        shutil.copy(src, dest)
        if open:
            subprocess.Popen(f"jupyter notebook {dest}")
    except:
        try:
            dest = os.path.join(os.path.expanduser('~'), "Downloads", pathlib.Path(file_path).name)
            shutil.copy(src, dest)
        except Exception as error:
            print(error)
    finally:
        if loc:
            print("Path:",dest)

def unzip_file(file_path, folder_path=None, loc = False):
    src = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", pathlib.Path(file_path))
    dest = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    if not os.path.exists(src):
        print(f"Error: Source zip file not found - {src}")
        return
    if os.path.exists(os.path.join(dest, pathlib.Path(folder_path))):
        return
    try:
        with zipfile.ZipFile(src, 'r') as zip_ref:
            zip_ref.extractall(dest)
        if loc:
            print("Extracted to:", os.path.join(dest, pathlib.Path(folder_path)))
    except zipfile.BadZipFile:
        print(f"Error: {zip_path} is not a valid zip file")
    except FileNotFoundError:
        print(f"Error: Zip file not found - {zip_path}")
    except Exception as e:
        print(f"Error extracting zip file: {e}")

import os
import shutil
import pathlib

def store_file(file_path, folder_name=None, overwrite=False, loc=False, move=False, verbose=True):
    try:
        src = pathlib.Path(file_path)
        if not src.exists():
            if verbose:
                print(f"Source file not found: {src}")
            return

        base_data_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "storage", "assets")

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

def remove_folder(folder_path):
    try:
        src1 = os.path.join(os.getcwd(), pathlib.Path(folder_path))
        src2 = os.path.join(os.path.expanduser('~'), "Downloads", pathlib.Path(folder_path))
        if os.path.exists(src1) or os.path.exists(src2):
            shutil.rmtree(src1, ignore_errors =  True)
            shutil.rmtree(src2, ignore_errors =  True)
            if os.path.exists(src1) or os.path.exists(src2):
                print("Deletion Impossible [File Not Closed - Shutdown File Kernel]\nGo to Home page -> Running Tab -> Click Shut Down All")
            else:
                print(f"Folder({pathlib.Path(folder_path)}) Removed Successfully")
        else:
            print(f"Folder({pathlib.Path(folder_path)}) Not Found [Repeated Iteration | Probably Removed Manually]")
    except Exception as error:
        print(error)

def clear_folder(folder_path):
    try:
        target_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", pathlib.Path(folder_path))
        
        if not os.path.exists(target_folder):
            print(f"Folder({pathlib.Path(folder_path)}) Not Found")
            return

        for item in os.listdir(target_folder):
            item_path = os.path.join(target_folder, item)
            try:
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.unlink(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            except Exception as e:
                print(f"Failed to delete {item_path}: {e}")
        print(f"Data Cleared Successfully")
    except Exception as error:
        print(error)
    
def install_offline_requirements(bundle_path=None, requirements_file=None):
    try:
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "storage", "assets", "offline")
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