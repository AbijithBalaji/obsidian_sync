import os
import subprocess
import time

# Set your Obsidian Vault path
VAULT_PATH = r"C:\Users\abiji\Personal\Project\Sync Project\obsidian_sync"

# Git command executor
def run_git_command(command):
    """Executes a git command in the specified vault directory."""
    result = subprocess.run(command, cwd=VAULT_PATH, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
    else:
        print(result.stdout)

# Step 1: Pull latest changes before opening Obsidian
print("Pulling latest changes from GitHub...")
run_git_command("git pull origin main")

# Step 2: Open Obsidian
print("Opening Obsidian...")
obsidian_path = r"C:\Users\abiji\AppData\Local\Programs\Obsidian\Obsidian.exe"
obsidian_process = subprocess.Popen([obsidian_path])

# Step 3: Wait for Obsidian to close
print("Waiting for Obsidian to close...")
obsidian_process.wait()

# Step 4: Commit and push changes after closing Obsidian
print("Checking for changes...")
run_git_command("git add .")
run_git_command('git commit -m "Auto-sync: latest updates"')
print("Pushing changes to GitHub...")
run_git_command("git push origin main")

print("Sync Completed!")
