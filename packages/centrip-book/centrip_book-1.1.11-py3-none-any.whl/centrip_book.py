#!/usr/bin/env python3
import os, sys, subprocess

BOOK_PATH = os.path.expanduser("~/.book")
RESERVED_ALIASES = {"add", "find", "rm", "remove", "help", "book", "list", "ls", "?", "q", "quit"}

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
            if "→" in line:
                name_part = line.split("→", 1)[0].strip()
                if name_part.lower() == alias_lower:
                    entries[i] = f"{alias} → {command}"
                    updated = True
                    break
        if not updated:
            entries.append(f"{alias} → {command}")
    else:
        entries.append(f"? → {command}")

    save_entries(entries)
    if updated:
        print(f"🔁 Updated: {alias} → {command}")
    elif alias:
        print(f"✅ Added #{len(entries)}: {alias} → {command}")
    else:
        print(f"✅ Added #{len(entries)}: {command}")

def format_line_short(i, line, width=80):
    if "→" in line:
        alias, cmd = [x.strip() for x in line.split("→", 1)]
        text = f"{i} ({alias}) → {cmd}"
    else:
        text = f"{i} → {line.strip()}"
    return text if len(text) <= width else text[:width - 3] + "..."

def print_book_header():
    print("📘 Command Book\n")
    print(" book <alias|index> [args...]     → Run a saved command (args: {1}, {2}, {all})")
    print(" book add  \"<command>\" [alias]  → Add or update a command (optional alias)")
    print(" book find <keyword>              → Search bookmarks by keyword")
    print(" book rm   <alias|index>          → Remove a command (auto-reindexes)")
    print(" book list                        → Show full command list\n")

def show_entry_multiline(i, line):
    if "→" in line:
        alias, cmd = [x.strip() for x in line.split("→", 1)]
        print(f"{i} ({alias})\n{cmd}\n")
    else:
        print(f"{i}\n{line.strip()}\n")

def cmd_show(truncate=True):
    entries = load_entries()
    print_book_header()
    print("📚 Bookmarks\n")
    if not entries:
        print("(empty)")
        return
    for i, line in enumerate(entries, start=1):
        if truncate:
            print(format_line_short(i, line))
        else:
            show_entry_multiline(i, line)

def cmd_find(keyword):
    entries = load_entries()
    found = [l for l in entries if keyword.lower() in l.lower()]
    print(f"🔍 Searching for '{keyword}'...\n")
    if not found:
        print("No matches found.")
        return
    for i, l in enumerate(found, start=1):
        show_entry_multiline(i, l)

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
            if "→" not in line:
                continue
            name = line.split("→", 1)[0].strip().lower()
            if name in {"?", ""}:
                continue
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
            if "→" not in l:
                continue
            name = l.split("→", 1)[0].strip().lower()
            if name in {"?", ""}:
                continue
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

def cmd_complete():
    entries = load_entries()
    aliases = []
    for line in entries:
        if "→" in line:
            name = line.split("→", 1)[0].strip()
            if name not in {"?", ""}:
                aliases.append(name)
    print(" ".join(aliases))

def setup_completion():
    """
    Installs bash and zsh completion automatically (macOS compatible).
    """
    completion_script = """# Bash & Zsh completion for 'book'
_book_complete() {
    COMPREPLY=()
    local cur prev opts
    cur="${COMP_WORDS[COMP_CWORD]}"
    opts="$(book --complete 2>/dev/null)"
    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
    return 0
}
complete -F _book_complete book

# Zsh compatibility
if [ -n "$ZSH_VERSION" ]; then
  autoload -U bashcompinit
  bashcompinit
fi
"""
    dest = os.path.expanduser("~/.book_completion")
    with open(dest, "w") as f:
        f.write(completion_script)
    shell_rc = os.path.expanduser("~/.zshrc" if "zsh" in os.environ.get("SHELL", "") else "~/.bashrc")
    line = f"[ -f {dest} ] && source {dest}"
    with open(shell_rc, "a") as f:
        f.write(f"\n{line}\n")
    print(f"✅ Completion installed for {shell_rc}. Restart your terminal or run:\n\n  source {shell_rc}\n")

def main():
    ensure_book()
    if len(sys.argv) == 1:
        cmd_show(truncate=True)
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
        cmd_show(truncate=True)
    elif cmd == "list":
        cmd_show(truncate=False)
    elif cmd == "--complete":
        cmd_complete()
    elif cmd == "--setup-completion":
        setup_completion()
    else:
        cmd_run(cmd, args)

if __name__ == "__main__":
    main()
