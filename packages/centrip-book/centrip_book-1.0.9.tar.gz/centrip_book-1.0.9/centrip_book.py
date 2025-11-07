#!/usr/bin/env python3
import os, sys

BOOK_PATH = os.path.expanduser("~/.book")

def ensure_book():
    if not os.path.exists(BOOK_PATH):
        open(BOOK_PATH, "w").close()

def load_entries():
    ensure_book()
    with open(BOOK_PATH) as f:
        return [line.strip() for line in f if line.strip()]

def save_entries(lines):
    with open(BOOK_PATH, "w") as f:
        for i, line in enumerate(lines, start=1):
            parts = line.split(" : ", 2)
            if len(parts) == 3:
                _, alias, cmd = parts
                f.write(f"{i} : {alias} : {cmd}\n")
            else:
                f.write(f"{i} : - : {line}\n")

def get_last_command():
    entries = load_entries()
    if not entries:
        return None
    last_line = entries[-1]
    parts = last_line.split(" : ", 2)
    return parts[2].strip() if len(parts) == 3 else parts[-1].strip()

def cmd_add(command, alias=None):
    entries = load_entries()
    alias = alias or "-"
    alias_lower = alias.lower()
    updated = False

    # Check if alias exists
    for i, line in enumerate(entries):
        parts = line.split(" : ", 2)
        if len(parts) == 3 and parts[1].strip().lower() == alias_lower:
            entries[i] = f"{i+1} : {alias} : {command}"
            updated = True
            break

    if not updated:
        index = len(entries) + 1
        entries.append(f"{index} : {alias} : {command}")

    save_entries(entries)
    if updated:
        print(f"🔁 Updated: {alias} → {command}")
    else:
        print(f"✅ Added #{len(entries)}: {alias} → {command}")

def cmd_list():
    entries = load_entries()
    print("📘 Command Book\n")
    if not entries:
        print("(empty)")
        return
    for line in entries:
        print(line)

def cmd_find(keyword):
    entries = load_entries()
    found = [l for l in entries if keyword.lower() in l.lower()]
    print(f"🔍 Searching for '{keyword}'...\n")
    if not found:
        print("No matches found.")
    else:
        for l in found:
            print(l)

def cmd_rm(target):
    entries = load_entries()
    if target.isdigit():
        index = int(target)
        if index <= 0 or index > len(entries):
            print("❌ Invalid index.")
            return
        del entries[index - 1]
    else:
        target_lower = target.lower()
        for i, line in enumerate(entries):
            alias = line.split(" : ", 3)[1].strip().lower()
            if alias == target_lower:
                del entries[i]
                break
        else:
            print("❌ No matching alias found.")
            return
    save_entries(entries)
    print("🗑️  Removed and reindexed.")

def cmd_run(target, extra_args):
    entries = load_entries()
    line = None
    if target.isdigit():
        index = int(target)
        if 1 <= index <= len(entries):
            line = entries[index - 1]
    else:
        target_lower = target.lower()
        for l in entries:
            alias = l.split(" : ", 3)[1].strip().lower()
            if alias == target_lower:
                line = l
                break
    if not line:
        print(f"❌ No command found with alias or index '{target}'.")
        return

    cmd = line.split(" : ", 3)[2].strip()

    # Argument placeholder logic
    if "{all}" in cmd or "{" in cmd:
        all_args = " ".join(extra_args)
        for i, val in enumerate(extra_args, start=1):
            cmd = cmd.replace(f"{{{i}}}", val)
        cmd = cmd.replace("{all}", all_args)
    elif extra_args:
        cmd += " " + " ".join(extra_args)

    print(f"▶ Running: {cmd}")
    os.system(cmd)

def cmd_help():
    print("📘 Command Book\n")
    print("Usage:")
    print("  book <alias|index> [args...]     → Run a saved command (supports {1}, {2}, {all})")
    print("  book add  \"<command>\" [alias]  → Add or update a command (optional alias)")
    print("  book find <keyword>              → Search bookmarks by keyword")
    print("  book rm   <n|alias>              → Remove a command (auto-reindexes)")
    print()

def main():
    ensure_book()
    if len(sys.argv) == 1:
        cmd_help()
        cmd_list()
        return

    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd == "add" and args:
        cmd_add(args[0], args[1] if len(args) > 1 else None)
    elif cmd == "find" and args:
        cmd_find(args[0])
    elif cmd == "rm" and args:
        cmd_rm(args[0])
    elif cmd == "help":
        cmd_help()
    else:
        cmd_run(cmd, args)

if __name__ == "__main__":
    main()
