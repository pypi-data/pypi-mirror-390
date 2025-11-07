#!/usr/bin/env python3
import os, sys, re

BOOK_PATH = os.path.expanduser("~/.book")

RESERVED_ALIASES = {"add", "find", "rm", "remove", "help", "book", "list", "ls"}

def ensure_book():
    if not os.path.exists(BOOK_PATH):
        open(BOOK_PATH, "w").close()

def load_entries():
    ensure_book()
    with open(BOOK_PATH) as f:
        return [line.strip() for line in f if line.strip()]

def save_entries(lines):
    with open(BOOK_PATH, "w") as f:
        for line in lines:
            f.write(line.strip() + "\n")

def is_invalid_alias(alias: str) -> bool:
    if not alias:
        return False
    if alias.lower() in RESERVED_ALIASES:
        print(f"❌ Alias '{alias}' is reserved.")
        return True
    if alias.isdigit():
        print(f"❌ Alias '{alias}' cannot be a number.")
        return True
    return False

def cmd_add(command, alias=None):
    if alias and is_invalid_alias(alias):
        return

    entries = load_entries()
    updated = False

    if alias:
        alias_lower = alias.lower()
        for i, line in enumerate(entries):
            parts = line.split("→", 1)
            name_part = parts[0].strip()
            if name_part.lower() == alias_lower:
                entries[i] = f"{alias} → {command}"
                updated = True
                break
        if not updated:
            entries.append(f"{alias} → {command}")
    else:
        entries.append(command)

    save_entries(entries)
    if updated:
        print(f"🔁 Updated: {alias} → {command}")
    elif alias:
        print(f"✅ Added #{len(entries)}: {alias} → {command}")
    else:
        print(f"✅ Added #{len(entries)}: {command}")

def cmd_list():
    entries = load_entries()
    print("📘 Command Book\n")
    print("book <alias|index> [args...]     → Run a saved command args: {1}, {2}, {all}")
    print("book add  \"<command>\" [alias]  → Add or update a command (optional alias)")
    print("book find <keyword>              → Search bookmarks by keyword")
    print("book rm   <n|alias>              → Remove a command (auto-reindexes)\n")
    print("📚 Bookmarks\n")

    if not entries:
        print("(empty)")
        return

    for i, line in enumerate(entries, start=1):
        parts = line.split("→", 1)
        if len(parts) == 2:
            alias = parts[0].strip()
            cmd = parts[1].strip()
            print(f"{i} ({alias}) → {cmd}")
        else:
            cmd = parts[0].strip()
            print(f"{i} → {cmd}")

def cmd_find(keyword):
    entries = load_entries()
    found = [l for l in entries if keyword.lower() in l.lower()]
    print(f"🔍 Searching for '{keyword}'...\n")
    if not found:
        print("No matches found.")
    else:
        for i, l in enumerate(found, start=1):
            parts = l.split("→", 1)
            if len(parts) == 2:
                alias = parts[0].strip()
                cmd = parts[1].strip()
                print(f"{i} ({alias}) → {cmd}")
            else:
                cmd = parts[0].strip()
                print(f"{i} → {cmd}")

def cmd_rm(target):
    entries = load_entries()
    if target.isdigit():
        index = int(target)
        if 1 <= index <= len(entries):
            del entries[index - 1]
        else:
            print("❌ Invalid index.")
            return
    else:
        target_lower = target.lower()
        for i, line in enumerate(entries):
            name = line.split("→", 1)[0].strip().lower()
            if name == target_lower:
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
            name = l.split("→", 1)[0].strip().lower()
            if name == target_lower:
                line = l
                break
    if not line:
        print(f"❌ No command found with alias or index '{target}'.")
        return

    cmd = line.split("→", 1)[-1].strip()
    if "{all}" in cmd or "{" in cmd:
        all_args = " ".join(extra_args)
        for i, val in enumerate(extra_args, start=1):
            cmd = cmd.replace(f"{{{i}}}", val)
        cmd = cmd.replace("{all}", all_args)
    elif extra_args:
        cmd += " " + " ".join(extra_args)

    print(f"▶ Running: {cmd}")
    os.system(cmd)

def main():
    ensure_book()
    if len(sys.argv) == 1:
        cmd_list()
        return

    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd == "add" and args:
        cmd_add(args[0], args[1] if len(args) > 1 else None)
    elif cmd == "find" and args:
        cmd_find(args[0])
    elif cmd in {"rm", "remove"} and args:
        cmd_rm(args[0])
    elif cmd == "help":
        cmd_list()
    else:
        cmd_run(cmd, args)

if __name__ == "__main__":
    main()
