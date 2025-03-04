import os
import subprocess
import sys
import threading
import psutil
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

# Detect OS (ensuring it's Windows since this is for standalone setup)
IS_WINDOWS = sys.platform.startswith("win")

# Configurable Paths
VAULT_PATH = r"C:\Users\abiji\Personal\Project\Sync Project\obsidian_sync"
OBSIDIAN_PATH = r"C:\Users\abiji\AppData\Local\Programs\Obsidian\Obsidian.exe"

# Ensure Git is installed
def is_git_installed():
    try:
        subprocess.run(["git", "--version"], capture_output=True, text=True, check=True)
        return True
    except FileNotFoundError:
        return False

# Run Git command
def run_git_command(command):
    """Executes a Git command and returns output."""
    try:
        result = subprocess.run(command, cwd=VAULT_PATH, shell=True, capture_output=True, text=True)
        return result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return "", str(e)

# Check if Obsidian is running
def is_obsidian_running():
    return any(p.name().lower() == "obsidian.exe" for p in psutil.process_iter())

# Update UI with progress
def update_progress(status_text, progress_value):
    log_text.insert(tk.END, status_text + "\n")
    log_text.yview_moveto(1)
    progress_bar["value"] = progress_value
    root.update_idletasks()

def sync_process():
    """Handles the full sync process."""
    if not is_git_installed():
        update_progress("❌ Git is not installed! Install Git and retry.", 100)
        return

    if not os.path.exists(OBSIDIAN_PATH):
        update_progress("❌ Obsidian is not installed! Install it and retry.", 100)
        return
    
    update_progress("🔄 Pulling latest changes...", 10)
    pull_output, pull_error = run_git_command("git pull origin main")

    if pull_error:
        update_progress(f"⚠️ Pull failed! {pull_error}", 20)
    elif "Already up to date." in pull_output:
        update_progress("✅ Already up to date.", 30)
    else:
        update_progress("📂 Downloaded new files.", 30)

    update_progress("📂 Opening Obsidian...", 40)
    obsidian_process = subprocess.Popen([OBSIDIAN_PATH], shell=True)
    update_progress("🕒 Waiting for Obsidian to close...", 50)
    
    def check_obsidian_status():
        if is_obsidian_running():
            root.after(500, check_obsidian_status)
        else:
            process_git_commit()
    
    root.after(500, check_obsidian_status)

def process_git_commit():
    """Handles committing and pushing changes."""
    update_progress("🔄 Checking for changes...", 70)
    run_git_command("git add .")
    commit_output, commit_error = run_git_command('git commit -m "Auto-sync: latest updates"')

    if "nothing to commit" in commit_output.lower():
        update_progress("✅ No new changes detected.", 100)
    else:
        update_progress("📌 Committing changes...", 80)
        ahead_check, _ = run_git_command("git rev-list --count origin/main..HEAD")
        if ahead_check.strip() != "0":
            update_progress("🚀 Pushing to GitHub...", 90)
            run_git_command("git push origin main")
        else:
            update_progress("✅ No new changes to push.", 100)
    
    root.after(700, root.destroy)

def start_sync_thread():
    """Runs sync process in background thread."""
    threading.Thread(target=sync_process, daemon=True).start()

def cancel_sync():
    """Allows user to cancel sync mid-way."""
    if messagebox.askyesno("Cancel Sync", "Are you sure you want to cancel the sync?"):
        root.destroy()

# Modern UI
root = tk.Tk()
root.title("Obsidian Sync")
root.geometry("450x200")
root.resizable(False, False)
root.configure(bg="#1e1e1e")

progress_label = tk.Label(root, text="Starting sync...", font=("Arial", 12), bg="#1e1e1e", fg="white")
progress_label.pack(pady=10)

progress_bar = ttk.Progressbar(root, orient="horizontal", length=350, mode="determinate")
progress_bar.pack(pady=5)
progress_bar["maximum"] = 100

log_text = scrolledtext.ScrolledText(root, height=5, width=50, state="normal", bg="#282828", fg="white")
log_text.pack(pady=5)

button_frame = tk.Frame(root, bg="#1e1e1e")
button_frame.pack()

cancel_button = tk.Button(button_frame, text="Cancel", command=cancel_sync, bg="#ff4444", fg="white", width=10)
cancel_button.pack(pady=5)

root.after(100, start_sync_thread)
root.mainloop()