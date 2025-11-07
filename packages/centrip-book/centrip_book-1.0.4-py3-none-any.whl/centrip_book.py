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

def cmd_add(command, alias=None):
    entries = load_entries()
    index = len(entries) + 1
    alias = alias or "-"
    entries.append(f"{index} : {alias} : {command}")
    save_entries(entries)
    print(f"✅ Added #{index}: {alias} → {command}")

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

def cmd_run(target):
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
    print(f"▶ Running: {cmd}")
    os.system(cmd)

def cmd_help():
    print("📘 Command Book\n")
    print("Usage:")
    print("  book <alias|index>               → Run a saved command")
    print("  book add  \"<command>\" [alias]  → Add a new command (optional alias)")
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
        cmd_run(cmd)

if __name__ == "__main__":
    main()
