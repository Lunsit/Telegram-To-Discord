# Telegram-To-Discord
Mirror all messages from Telegram group to Discord via a Post requests.

# Example
Note: Telegram bot replies with a message that appears only in the specified test group.

![2024-03-11_132419](https://github.com/Lunsit/Telegram-To-Discord/assets/61680403/c68aa0d7-7799-4337-9b2f-3b9f2dcff7f1)
![2024-03-11_132508](https://github.com/Lunsit/Telegram-To-Discord/assets/61680403/c7220a5f-9f4f-44e4-b932-12a7049df6e1)

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

```py
pip install -r requirements.txt
```

4. Rename sample-config.yaml to config.yaml.
5. Edit info in config.yaml.
6. Run!

```py
python3 tg2dc.py
```