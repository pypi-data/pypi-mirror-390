## 💡 Usage

| Command | Description |
|----------|-------------|
| `book <alias\|index>` | Run a saved command |
| `book add "<command>" [alias]` | Add a new command (optional alias) |
| `book find <keyword>` | Search commands by keyword |
| `book rm <n\|alias>` | Remove a saved command (auto-reindexes) |

---

## 🧠 Examples

```bash
# Add and name your favorite commands
book add "sudo nginx -t && sudo systemctl reload nginx" nginx
book add "cd /var/www/live" live
book add "git status" gs

# View all saved commands
book

# Run a saved one
book nginx
book gs

# Search for related entries
book find nginx

# Remove an outdated entry
book rm nginx
```

---

## 📂 Storage Format

Commands are stored in `~/.book` in this format:

```
1 : nginx : sudo nginx -t && sudo systemctl reload nginx
2 : live  : cd /var/www/live
3 : gs    : git status
```
