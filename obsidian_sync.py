import os
import subprocess
import time

# Set your Obsidian Vault path
VAULT_PATH = r"C:\Users\abiji\Personal\Project\Sync Project\obsidian_sync"

# Set the correct path to Obsidian
OBSIDIAN_PATH = r"C:\Users\abiji\AppData\Local\Programs\Obsidian\Obsidian.exe"  # Update if necessary

# Git command executor
def run_git_command(command):
    """Executes a git command in the specified vault directory."""
    result = subprocess.run(command, cwd=VAULT_PATH, shell=True, capture_output=True, text=True)
    if result.returncode != 0 and "nothing to commit" not in result.stderr:
        print(f"Error: {result.stderr}")
    else:
        print(result.stdout)

# Step 1: Pull latest changes before opening Obsidian
print("Pulling latest changes from GitHub...")
run_git_command("git pull origin main")

# Step 2: Open Obsidian and wait for it to close
print("Opening Obsidian...")
obsidian_process = subprocess.Popen(OBSIDIAN_PATH, shell=True)
obsidian_process.wait()  # Wait until Obsidian is closed before proceeding

# Step 3: Commit and push changes after closing Obsidian
print("Checking for changes...")
run_git_command("git add .")

# Check if there are actual changes before committing
commit_result = subprocess.run("git diff --cached --exit-code", cwd=VAULT_PATH, shell=True)
if commit_result.returncode == 0:
    print("No changes detected. Skipping commit and push.")
else:
    run_git_command('git commit -m "Auto-sync: latest updates"')
    print("Pushing changes to GitHub...")
    run_git_command("git push origin main")

print("Sync Completed!")
