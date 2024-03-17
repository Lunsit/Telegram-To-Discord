# Telegram-To-Discord
Mirror messages from Telegram group to Discord via a Post requests.

# Example
![1](https://github.com/Lunsit/Telegram-To-Discord/assets/61680403/a9f38cbd-f809-4b86-ac72-fda0c10a189b)
![2](https://github.com/Lunsit/Telegram-To-Discord/assets/61680403/a9e2ee6b-aa9f-4491-ac6b-32f69bd93174)

# Requirements

- Python 3.9.12 or later
- Python pip -> requirements.txt
- Discord bot token
- Discord channel ID
- Telegram group ID
- Telegram API tokens

# How to run

1. Download the repo and extract to an empty folder.
2. Open a CLI ex. CMD, PS, GitBash in the directory.
3. Install requirements.

```cmd
pip install "python-telegram-bot[job-queue]"
```

4. Rename sample-config.yaml to config.yaml.
5. Edit info in config.yaml.
6. Run!

```cmd
python3 tg2dc.py
```

# Todo
- [x] Add image forward
- [x] Add group image forward
- [ ] Add file forward
- [ ] Add large file detection
- [ ] Maybe add stickers support
