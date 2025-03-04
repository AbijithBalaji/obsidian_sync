## **🔹 Test Case 1: Basic Sync Workflow (No Conflicts)**

✅ **Steps to Test:**

1. Edit a note (`test.md`) in **Windows Obsidian**.
2. Close **Obsidian** and check the **terminal output**.
3. Open **Raspberry Pi Obsidian**, wait for sync, and verify that the changes are present.
4. Repeat the process **in reverse** (edit in Raspberry Pi → sync to Windows).

✅ **Expected Behavior:**

- Changes **push from Windows** and **pull into Raspberry Pi**.
- **No errors appear** in the terminal.
- Obsidian **loads the updated notes** correctly.

---

## **🔹 Test Case 2: Syncing When Offline (No Internet)**

✅ **Steps to Test:**

1. **Turn off the internet** on Windows.
2. Edit a note (`offline_note.md`) and close Obsidian.
3. The **terminal should show a message** saying:
    
    pgsql
    
    CopyEdit
    
    `⚠️ Warning: No internet connection. Changes committed locally but not pushed.`
    
4. **Reconnect the internet** and **run the script again**.
5. Close Obsidian → The script should **detect and push the previous commit**.

✅ **Expected Behavior:**

- **Changes commit locally** when offline.
- **Sync resumes automatically** on the next run when the internet is restored.
- No duplicate commits or lost changes.

---

## **🔹 Test Case 3: Uncommitted Changes on Both Windows & Raspberry Pi**

✅ **Steps to Test:**

1. **Edit different files** on **Windows and Raspberry Pi** (e.g., `win_note.md` on Windows, `pi_note.md` on Raspberry Pi).
2. Close Windows Obsidian first, then close Raspberry Pi.
3. Verify that both changes sync correctly.

✅ **Expected Behavior:**

- Since different files are edited, **both versions should sync properly** without conflicts.
- No error messages or manual conflict resolution required.

---

## **🔹 Test Case 4: Editing the Same File on Both Windows & Raspberry Pi (Conflict)**

✅ **Steps to Test:**

1. **Edit the same note (`conflict_test.md`)** in **both Windows and Raspberry Pi**.
2. Close **Windows Obsidian first**, allowing it to push changes.
3. Close **Raspberry Pi Obsidian** → **A conflict should be detected.**
4. **The GUI should appear** with options:
    - **Keep Windows version**
    - **Keep Raspberry Pi version**
    - **Merge both versions**
5. Choose an option and verify that the resolved file syncs to both systems.

✅ **Expected Behavior:**

- The **GUI should pop up** when a conflict is detected.
- After resolution, the correct version should **sync to GitHub and all devices**.
- No file should be lost or overwritten incorrectly.

---

## **🔹 Test Case 5: Force Closing Obsidian Before Sync Completes**

✅ **Steps to Test:**

1. **Edit a note** (`force_close.md`) on **Windows**.
2. **Before closing Obsidian**, force close it from Task Manager (`End Task`).
3. Reopen Obsidian and check if the previous changes **were lost or committed.**
4. **Now properly close Obsidian** and check if the changes sync correctly.

✅ **Expected Behavior:**

- **If force-closed before saving**, changes **might be lost** (Obsidian behavior).
- **If force-closed after saving**, the script should **still commit & push changes on the next run**.
- No corruption or duplicated commits should happen.

---

## **🔹 Test Case 6: Losing Internet Mid-Sync**

✅ **Steps to Test:**

1. **Edit a file** (`network_failure.md`) in **Windows Obsidian**.
2. **Close Obsidian**, and **disconnect the internet immediately** while the sync script is running.
3. The script should **detect the failure** and commit changes locally.
4. **Reconnect the internet and rerun the script.**
5. The script should detect **pending commits** and push them.

✅ **Expected Behavior:**

- **No crashes** or terminal errors.
- **Local commit is stored** when sync is interrupted.
- **Sync automatically completes** on the next run.

---

## **🔹 Test Case 7: Long-Unsynced Period (Older Edits)**

✅ **Steps to Test:**

1. **Edit notes on Raspberry Pi** but **do not sync for a few days.**
2. **Meanwhile, keep making updates on Windows** and syncing them.
3. **Finally, sync Raspberry Pi** and ensure it pulls the latest changes first.
4. Confirm that **no old edits overwrite new ones**.

✅ **Expected Behavior:**

- The script should **pull before pushing** to prevent overwriting.
- No missing updates or **accidental overwrites of newer edits**.

---

## **🔹 Test Case 8: User Manually Edits Git Repo Outside of Obsidian**

✅ **Steps to Test:**

1. **Manually edit `test.md` using a text editor** (outside of Obsidian).
2. **Run the sync script manually** without opening Obsidian.
3. Check if the script detects the changes and pushes them.

✅ **Expected Behavior:**

- Manual changes should **be detected and pushed like normal edits**.
- No issues should arise from modifying the repository directly.

---

## **🔹 Test Case 9: Deleting a Note & Syncing**

✅ **Steps to Test:**

1. **Delete a note (`deleted_note.md`) in Windows** and close Obsidian.
2. **Check if it is removed from GitHub**.
3. **Open Raspberry Pi Obsidian** and check if the note disappears there too.

✅ **Expected Behavior:**

- The file should be **deleted from GitHub and all synced devices**.
- **No conflict errors** should appear.

---

## **🔹 Test Case 10: Handling Large Number of Files**

✅ **Steps to Test:**

1. **Create multiple files** (`file1.md`, `file2.md`, ..., `file50.md`).
2. **Edit them across Windows and Raspberry Pi.**
3. **Close Obsidian on both systems and check sync speed.**

✅ **Expected Behavior:**

- The script should **handle a large number of files efficiently**.
- **No crashes or long delays** in syncing.