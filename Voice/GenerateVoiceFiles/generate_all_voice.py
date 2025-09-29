import os
import subprocess
import sys
import shutil

# Root directory where all prompt folders are located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Central collection directory
TARGET_DIR = os.path.join(BASE_DIR, "CreacodeSAS")

LANG_FOLDERS = {"english", "german", "french", "italian", "turkish", "spanish", "russian"}

def run_script(script_path):
    """Run a Python script and stream its output"""
    print(f"[RUN ] {script_path}")
    try:
        subprocess.run([sys.executable, script_path], check=True)
        print(f"[DONE] {os.path.basename(script_path)} executed successfully")
    except subprocess.CalledProcessError as e:
        print(f"[FAIL] {script_path} exited with code {e.returncode}")

def merge_and_move(src, dst):
    """Merge contents of src into dst (overwrite duplicates), then remove src"""
    os.makedirs(dst, exist_ok=True)
    for root, _, files in os.walk(src):
        rel_path = os.path.relpath(root, src)
        target_root = os.path.join(dst, rel_path) if rel_path != "." else dst
        os.makedirs(target_root, exist_ok=True)
        for f in files:
            shutil.move(os.path.join(root, f), os.path.join(target_root, f))
    shutil.rmtree(src)

def main():
    print(f"[START] Collecting voices into {TARGET_DIR}")
    os.makedirs(TARGET_DIR, exist_ok=True)

    # Iterate all subfolders
    for folder in os.listdir(BASE_DIR):
        folder_path = os.path.join(BASE_DIR, folder)

        if os.path.isdir(folder_path):
            script_path = os.path.join(folder_path, f"{folder}.py")
            if os.path.isfile(script_path):
                run_script(script_path)

                # After running script, move language folders into TARGET_DIR
                for lang in os.listdir(folder_path):
                    if lang.lower() in LANG_FOLDERS:
                        src = os.path.join(folder_path, lang)
                        dst = os.path.join(TARGET_DIR, lang)
                        print(f"[MOVE] {src} → {dst}")
                        merge_and_move(src, dst)

    print("[END ] All voices collected into CreacodeSAS.")

if __name__ == "__main__":
    main()
