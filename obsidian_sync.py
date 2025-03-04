import os
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox

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
    """Executes a Git command in the specified vault directory."""
    result = subprocess.run(command, cwd=VAULT_PATH, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip()

def show_dialog(title, message):
    """Displays a messagebox dialog for user notifications."""
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo(title, message)
    root.destroy()

def get_conflicted_files():
    """Check for Git conflicts and return a list of files."""
    result, _ = run_git_command("git diff --name-only --diff-filter=U")
    return result.split("\n") if result else []

def check_network():
    """Check if the device has an active internet connection."""
    result = subprocess.run("ping -c 1 google.com" if not IS_WINDOWS else "ping -n 1 google.com", shell=True, stdout=subprocess.PIPE)
    return result.returncode == 0

def commit_changes():
    """Commits changes and pushes them unless a conflict is detected."""
    run_git_command("git add .")

    # Force commit if changes are staged
    print("🔄 Checking for staged changes...")
    staged_files, _ = run_git_command("git diff --cached --name-only")
    
    if not staged_files.strip():
        print("✅ No new changes detected. Skipping commit.")
    else:
        print(f"📌 Staged files found: {staged_files}")
        run_git_command('git commit -m "Auto-sync: latest updates"')
    
    # Check if ahead of origin/main
    ahead_check, _ = run_git_command("git status --porcelain -b")
    if "ahead" in ahead_check:
        print("🔄 Local commits detected. Pushing to GitHub...")
        run_git_command("git push origin main")
        show_dialog("Sync Successful", "All changes have been committed and pushed.")
    else:
        print("✅ No unpushed commits. Skipping push.")

# Step 1: Show a dialog that sync is starting
show_dialog("Obsidian Sync", "Pulling latest changes from GitHub...")

# Step 2: Pull latest changes before opening Obsidian
pull_output, pull_error = run_git_command("git pull origin main")

# Step 3: Display new files if pulled
if pull_output:
    show_dialog("New Updates", f"Downloaded new files:\n{pull_output}")

# Step 4: Open Obsidian
print("Opening Obsidian...")
obsidian_process = subprocess.Popen(OBSIDIAN_CMD, shell=IS_WINDOWS)

# Wait for Obsidian to close
obsidian_process.wait()
print("Obsidian closed. Checking for changes...")

# Step 5: Show a dialog that sync is happening
show_dialog("Syncing Changes", "Syncing your latest changes...")

# Step 6: Commit and push changes
commit_changes()

print("Sync Completed!")
