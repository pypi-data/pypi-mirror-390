# centrip-book

📘 **Command Book** — a portable command bookmarking tool for Linux and macOS.

Save, run, search, and manage your favorite terminal commands quickly.

---

## 🚀 Installation
```bash
pip install centrip-book
```

If the command isn’t found, make sure `~/.local/bin` (or `/usr/local/bin`) is in your `$PATH`.

---

## 💡 Usage

| Command | Description |
|----------|-------------|
| `book <alias|index>` | Run a saved command |
| `book add "<command>" [alias]` | Add a new command (optional alias) |
| `book find <keyword>` | Search commands by keyword |
| `book rm <n|alias>` | Remove a command (auto-reindexes) |
| `book help` | Show usage only |

---

## 🧠 Examples
```bash
book add "ls -la" list
book add "sudo nginx -t && sudo systemctl reload nginx" nginx
book
book nginx
book find nginx
book rm list
```

---

## 📂 Storage Format
Commands are stored in `~/.book` in this format:
```text
1 : alias : command
2 : alias : command
```

---

## 🔧 Uninstall
```bash
pip uninstall centrip-book
```

---

## 🧑‍💻 Author
**Michael Sowerwine**  
MIT License  
https://github.com/yourusername/centrip-book
