import os
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import ttk

# Detect OS
IS_WINDOWS = sys.platform.startswith("win")

# Set paths
if IS_WINDOWS:
    VAULT_PATH = r"C:\Users\abiji\Personal\Project\Sync Project\obsidian_sync"
    OBSIDIAN_CMD = [r"C:\Users\abiji\AppData\Local\Programs\Obsidian\Obsidian.exe"]
else:
    VAULT_PATH = "/home/pi/obsidian_sync"
    OBSIDIAN_CMD = ["flatpak", "run", "md.obsidian.Obsidian"]

def run_git_command(command):
    """Executes a Git command in the specified vault directory and returns output."""
    result = subprocess.run(command, cwd=VAULT_PATH, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip()

def update_progress(status_text, progress_value):
    """Updates the progress bar and status message."""
    progress_label.config(text=status_text)
    progress_bar["value"] = progress_value
    root.update_idletasks()

def sync_process():
    """Handles the full sync process in a separate thread."""
    update_progress("🔄 Pulling latest changes...", 10)
    pull_output, pull_error = run_git_command("git pull origin main")

    if pull_error:
        update_progress("⚠️ Pull failed! Possible conflict.", 20)
    elif "Already up to date." in pull_output:
        update_progress("✅ Already up to date.", 30)
    else:
        update_progress("📂 Downloaded new files.", 30)

    # Open Obsidian
    update_progress("📂 Opening Obsidian...", 40)
    obsidian_process = subprocess.Popen(OBSIDIAN_CMD, shell=IS_WINDOWS)

    # Show message while waiting
    update_progress("🕒 Waiting for Obsidian to close...", 50)
    
    def check_obsidian_status():
        """Periodically checks if Obsidian is still running."""
        if obsidian_process.poll() is None:
            root.after(500, check_obsidian_status)  # Re-check after 500ms
        else:
            process_git_commit()

    root.after(500, check_obsidian_status)

def process_git_commit():
    """Handles committing and pushing changes after Obsidian is closed."""
    update_progress("🔄 Checking for changes...", 70)
    
    run_git_command("git add .")
    staged_files, _ = run_git_command("git diff --cached --name-only")

    if not staged_files.strip():
        update_progress("✅ No new changes detected.", 100)
    else:
        update_progress("📌 Committing changes...", 80)
        run_git_command('git commit -m "Auto-sync: latest updates"')

        ahead_check, _ = run_git_command("git status --porcelain -b")
        if "ahead" in ahead_check:
            update_progress("🚀 Pushing to GitHub...", 90)
            run_git_command("git push origin main")
        else:
            update_progress("✅ No new changes to push.", 100)

    # Auto-close window after sync completes
    root.after(1500, root.destroy)

def start_sync_thread():
    """Runs the sync process in a background thread to keep UI responsive."""
    threading.Thread(target=sync_process, daemon=True).start()

# Create Progress Window
root = tk.Tk()
root.title("Obsidian Sync")
root.geometry("400x150")
root.resizable(False, False)

progress_label = tk.Label(root, text="Starting sync...", font=("Arial", 12))
progress_label.pack(pady=10)

progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress_bar.pack(pady=10)
progress_bar["maximum"] = 100

root.after(100, start_sync_thread)
root.mainloop()
