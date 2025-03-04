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

def run_git_command(command, suppress_output=False):
    """Executes a Git command in the specified vault directory."""
    result = subprocess.run(command, cwd=VAULT_PATH, shell=True, capture_output=True, text=True)
    if result.returncode != 0 and "nothing to commit" not in result.stderr:
        print(f"Error: {result.stderr}")
    elif not suppress_output:
        print(result.stdout)

def get_conflicted_files():
    """Check for Git conflicts and return a list of files."""
    result = subprocess.run("git diff --name-only --diff-filter=U", cwd=VAULT_PATH, shell=True, capture_output=True, text=True)
    return result.stdout.strip().split("\n") if result.stdout else []

def resolve_conflict(option):
    """Resolve conflict based on the user's choice."""
    conflicted_files = get_conflicted_files()
    if not conflicted_files:
        messagebox.showinfo("No Conflicts", "No conflicts found.")
        return

    for file in conflicted_files:
        file_path = os.path.join(VAULT_PATH, file)
        
        if option == "windows":
            subprocess.run(f"git checkout --ours {file}", cwd=VAULT_PATH, shell=True)
        elif option == "linux":
            subprocess.run(f"git checkout --theirs {file}", cwd=VAULT_PATH, shell=True)
        elif option == "merge":
            # Simple merge: Append both versions in the file
            with open(file_path, "r") as f:
                content = f.read()
            merged_content = f"==== WINDOWS VERSION ====\n{content}\n==== LINUX VERSION ====\n{content}"
            with open(file_path, "w") as f:
                f.write(merged_content)

        subprocess.run(f"git add {file}", cwd=VAULT_PATH, shell=True)

    subprocess.run("git rebase --continue", cwd=VAULT_PATH, shell=True)
    subprocess.run("git push origin main", cwd=VAULT_PATH, shell=True)
    messagebox.showinfo("Conflict Resolved", "Conflict resolution applied and pushed to GitHub.")
    root.destroy()

def commit_changes():
    """Commits changes and pushes them unless a conflict is detected."""
    run_git_command("git add .")

    # Check if there are actual changes before committing
    commit_result = subprocess.run("git diff --cached --exit-code", cwd=VAULT_PATH, shell=True, capture_output=True)
    if commit_result.returncode == 0:
        print("No new changes detected.")

        # Check for unpushed commits before exiting
        pending_commits = subprocess.run("git log origin/main..HEAD", cwd=VAULT_PATH, shell=True, capture_output=True, text=True)
        if pending_commits.stdout:
            print("🔄 Detected unpushed commits! Retrying push...")
            run_git_command("git push origin main")
        else:
            print("✅ No unpushed commits. Skipping push.")
        return

    # Commit the changes
    run_git_command('git commit -m "Auto-sync: latest updates"', suppress_output=True)

    # Pull latest changes before pushing
    print("🔄 Pulling latest changes before pushing...")
    pull_result = subprocess.run("git pull --rebase origin main", cwd=VAULT_PATH, shell=True, capture_output=True, text=True)

    if pull_result.returncode != 0:
        print("⚠️ Pull failed! Possible conflict detected.")
        launch_conflict_gui()
        return

    # Push the changes
    run_git_command("git push origin main")

def launch_conflict_gui():
    """Launch the GUI when a conflict is detected."""
    global root
    root = tk.Tk()
    root.title("Obsidian Sync Conflict Resolver")
    root.geometry("400x200")

    conflicted_files = get_conflicted_files()
    if conflicted_files:
        tk.Label(root, text="Git conflict detected! Choose an action:").pack(pady=10)
        tk.Button(root, text="Keep Windows Version", command=lambda: resolve_conflict("windows")).pack(pady=5)
        tk.Button(root, text="Keep Linux Version", command=lambda: resolve_conflict("linux")).pack(pady=5)
        tk.Button(root, text="Merge Both Versions", command=lambda: resolve_conflict("merge")).pack(pady=5)
    else:
        tk.Label(root, text="No conflicts detected.").pack(pady=20)

    root.mainloop()

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
