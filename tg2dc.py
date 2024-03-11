import yaml
import requests

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters



with open("config.yaml", "r") as ymlfile:
    cfg = yaml.safe_load(ymlfile)

# Setup
tg_bot_token = cfg['telegram']['token']
tg_chat_id = cfg['telegram']['chat_id']
dc_channel_id = cfg['discord']['channel_id']
dc_bot_token = cfg['discord']['token']
test_tg_chat_id = '-114514'
# Remove the # from the next line to allow telegram bot to reply to the message in the group
# test_tg_chat_id = tg_chat_id

# Discord API request
def send_embed_to_discord_channel(channel_id, bot_token, embed):
    url = f"https://discord.com/api/channels/{channel_id}/messages"
    headers = {
        "Authorization": f"Bot {bot_token}",
    }
    json_data = {
        "embeds": [embed]
    }
    response = requests.post(url, headers=headers, json=json_data)
    return response.json()

# Telegram bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Responding to the start command'''
    text = 'Still alive.'
    await context.bot.send_message(chat_id=update.effective_chat.id,text=text)


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="DONT TOUCH")


async def tg2discord(update: Update, context: ContextTypes.DEFAULT_TYPE):
    title = 'Telegram message from: ' + update.message.from_user['first_name'] + update.message.from_user['last_name']
    content = 'Content: ' +  update.message.text
    print(title + content)
    # Only specific group can send messages to Discord.
    if update.message.chat['id'] == int(tg_chat_id):
        embed = {
            "title": title,
            "description": content,
            "color": 0x00ff00
        }
        response = send_embed_to_discord_channel(dc_channel_id, dc_bot_token, embed)
        print(response)

    # Test group
    if update.message.chat['id'] == int(test_tg_chat_id):
        await context.bot.send_message(chat_id=update.effective_chat.id, text=title + '\n' + content)


# Setup handler
start_handler = CommandHandler('start', start)
unknown_handler = MessageHandler(filters.COMMAND, unknown)
tg2discord_handler = MessageHandler(filters.TEXT, tg2discord)

# Build bot
application = ApplicationBuilder().token(tg_bot_token).build()

# Add handler
application.add_handler(start_handler)
application.add_handler(unknown_handler)
application.add_handler(tg2discord_handler)

# Run!
application.run_polling()
