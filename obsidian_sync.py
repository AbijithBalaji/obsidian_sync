import os
import subprocess
import sys
import time

# Detect the OS
IS_WINDOWS = sys.platform.startswith("win")

# Set the vault path based on OS
if IS_WINDOWS:
    VAULT_PATH = r"C:\Users\abiji\Personal\Project\Sync Project\obsidian_sync"
    OBSIDIAN_CMD = [r"C:\Users\abiji\AppData\Local\Programs\Obsidian\Obsidian.exe"]  # Update if needed
else:
    VAULT_PATH = "/home/Abijith_PI/obsidian_sync"
    OBSIDIAN_CMD = ["flatpak", "run", "md.obsidian.Obsidian"]

def run_git_command(command, suppress_output=False):
    """Executes a git command in the specified vault directory."""
    result = subprocess.run(command, cwd=VAULT_PATH, shell=True, capture_output=True, text=True)
    if result.returncode != 0 and "nothing to commit" not in result.stderr:
        print(f"Error: {result.stderr}")
    elif not suppress_output:
        print(result.stdout)

def commit_changes():
    """Commits changes, pulls latest updates, and prevents conflicts."""
    run_git_command("git add .")

    # Check if there are actual changes before committing
    commit_result = subprocess.run("git diff --cached --exit-code", cwd=VAULT_PATH, shell=True, capture_output=True)
    if commit_result.returncode == 0:
        print("No new changes detected.")

        # NEW: Check for unpushed commits before returning
        pending_commits = subprocess.run("git log origin/main..HEAD", cwd=VAULT_PATH, shell=True, capture_output=True, text=True)
        if pending_commits.stdout:
            print("🔄 Detected unpushed commits! Retrying push...")
            push_changes()
        else:
            print("✅ No unpushed commits. Skipping push.")
        return

    # Commit the new changes
    run_git_command('git commit -m "Auto-sync: latest updates"', suppress_output=True)

    # Try pulling latest changes before pushing
    print("🔄 Pulling latest changes before pushing...")
    pull_result = subprocess.run("git pull --rebase origin main", cwd=VAULT_PATH, shell=True, capture_output=True, text=True)

    if pull_result.returncode != 0:
        print("⚠️ Pull failed! Possible conflict detected.")
        print("🔧 Resolve manually by running:")
        print(f"  cd {VAULT_PATH}")
        print("  git status  # Check which files are in conflict")
        print("  Fix the conflicts in the files")
        print("  git add . && git rebase --continue")
        print("  git push origin main")
        return

    # If pull is successful, push the changes
    push_changes()

def push_changes():
    """Pushes committed changes to GitHub."""
    print("Pushing changes to GitHub...")
    push_result = subprocess.run("git push origin main", cwd=VAULT_PATH, shell=True, capture_output=True)

    if push_result.returncode != 0:
        print("⚠️ Push failed! Possible conflict detected. Resolve manually as instructed.")
    else:
        print("✅ Changes pushed successfully.")


# Step 1: Pull latest changes before opening Obsidian
print("Pulling latest changes from GitHub...")
run_git_command("git pull origin main")

# Step 2: Open Obsidian and wait for it to close
print("Opening Obsidian...")
obsidian_process = subprocess.Popen(OBSIDIAN_CMD, shell=IS_WINDOWS)

# Wait for Obsidian to close before proceeding
obsidian_process.wait()
print("Obsidian closed. Checking for changes...")

# Step 3: Commit and push changes after closing Obsidian
commit_changes()

print("Sync Completed!")