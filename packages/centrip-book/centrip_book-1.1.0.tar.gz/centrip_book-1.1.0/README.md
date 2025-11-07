# 📘 Centrip Book

A lightweight terminal command bookmarking tool — save, search, and run your most used commands instantly.

---

## 💡 Usage

| Command | Description |
|----------|-------------|
| `book` | List all saved commands |
| `book add "<command>" [alias]` | Add a new command (optional alias) |
| `book <alias|index>` | Run a saved command |
| `book find <keyword>` | Search for commands by keyword |
| `book rm <n|alias>` | Remove a saved command |

---

## 🧠 Examples

```bash
# Add and name your favorite commands
book add "sudo nginx -t && sudo systemctl reload nginx" nginx
book add "cd /var/www/live" live

# Run by alias or index
book nginx
book 2

# Search or remove
book find nginx
book rm nginx
```

---

## 📂 Storage

Commands are stored in `~/.book` as plain text, one per line:

```
nginx → sudo nginx -t && sudo systemctl reload nginx
live → cd /var/www/live
soup
```

---

## ⚙️ Installation

```bash
pip install centrip-book --break-system-packages
```

---

## 🏷️ Version

**1.1.0** – cleaned display, reserved alias protection, and simplified storage format.
