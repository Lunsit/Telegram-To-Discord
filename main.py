import os
import yaml
import json
import logging
import requests

from typing import TypedDict, Literal, List, cast
from telegram import (
    Update,
    InputMediaVideo,
    InputMediaPhoto,
    InputMediaDocument,
    InputMediaAudio,
)
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    Defaults,
    filters,
    MessageHandler,
    PicklePersistence,
)
from telegram.helpers import effective_message_type


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.ERROR,
    filename="log.log",
)
logger = logging.getLogger(__name__)


with open("config.yaml", "r") as ymlfile:
    cfg = yaml.safe_load(ymlfile)

# Setup
tg_bot_token = cfg['telegram']['token']
tg_chat_id = cfg['telegram']['chat_id']
dc_channel_id = cfg['discord']['channel_id']
dc_bot_token = cfg['discord']['token']
MEDIA_GROUP_TYPES = {
    "audio": InputMediaAudio,
    "document": InputMediaDocument,
    "photo": InputMediaPhoto,
    "video": InputMediaVideo,
}
class MsgDict(TypedDict):
    media_type: Literal["video", "photo"]
    media_id: str
    msg_url : str
    caption: str
    title: str
    post_id: int

# Discord API request
def send_embed_to_discord_channel(channel_id, bot_token, title, description, msg_url, image_paths):
    url = f"https://discord.com/api/channels/{channel_id}/messages"
    headers = {
        "Authorization": f"Bot {bot_token}",
    }
    files = {}
    embeds = []
    embeds.append(
        {
            "type": "rich",
            "url": msg_url,
            "title": title,
            "description": description,
            "color": 0x00ff00
        })
    if image_paths is not None:
        for i, image_path in enumerate(image_paths):
            file_key = f'file{i}'
            files[file_key] = (image_path.split('/')[-1], open(image_path, 'rb'))
            embeds.append({
                "url": msg_url,
                "image": {"url": f"attachment://{image_path.split('/')[-1]}"}
            })

    payload = {
        'payload_json': (None, json.dumps({"embeds": embeds})),
    }
    response = requests.post(url, headers=headers, files=files, data=payload)
    return response.json()

# Telegram bot
# Bot Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Responding to the start command'''
    text = 'Still alive.'
    await context.bot.send_message(chat_id=update.effective_chat.id,text=text)

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Still alive.")

# Bot Message Handling
async def post_init(application: Application):
    if "messages" not in application.bot_data:
        application.bot_data = {"messages": {}}

# Send Media Group
async def media_group_sender(context: ContextTypes.DEFAULT_TYPE):
    context.job.data = cast(List[MsgDict], context.job.data)

    title = context.job.data[0]['title']
    msg_url = context.job.data[0]['msg_url']

    media = []
    for msg_dict in context.job.data:
        media.append(
            MEDIA_GROUP_TYPES[msg_dict["media_type"]](
                media=msg_dict["media_id"], caption=msg_dict["caption"]
            )
        )
    if not media:
        return

    media_contents = [item.media for item in media]
    caption = next((item.caption for item in media if hasattr(item, 'caption')), None)

    file_list = []
    for index, media_id in enumerate(media_contents, start=1):
        new_file = await context.bot.getFile(media_id)
        file_path = f'image/p{index}.jpg'
        file_list.append(file_path)
        await new_file.download_to_drive(custom_path=file_path)
    
    send_embed_to_discord_channel(dc_channel_id, dc_bot_token, title, caption, msg_url, file_list)

# When something new comes in.
async def new_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Only specific group can send messages to Discord.
    if update.message.chat['id'] == int(tg_chat_id):
        message = update.effective_message
        media_type = effective_message_type(message)
        title = 'Telegram message from: ' + update.message.from_user['first_name'] + \
                (update.message.from_user['last_name']) if update.message.from_user['last_name'] is not None else ''

        # If the message type is text
        if media_type == "text":
            content = 'Content: ' +  update.message.text
            response = send_embed_to_discord_channel(dc_channel_id, dc_bot_token, title, content, update.message.link, None)

        # If there is a media group
        elif message.media_group_id:
            media_id = (
                message.photo[-1].file_id
                if message.photo
                else message.effective_attachment.file_id
            )
            msg_dict = {
                "media_type": media_type,
                "media_id": media_id,
                "caption": message.caption_html,
                "post_id": message.message_id,
                "msg_url": update.message.link,
                "title" : title
            }
            jobs = context.job_queue.get_jobs_by_name(str(message.media_group_id))
            if jobs:
                jobs[0].data.append(msg_dict)
            else:
                context.job_queue.run_once(
                    callback=media_group_sender,
                    when=2,
                    data=[msg_dict],
                    name=str(message.media_group_id),
                )

        # Not the media group
        else:
            content = ('Content: ' + update.message.caption) if update.message.caption is not None else ''
            media_id = (
                message.photo[-1].file_id
                if message.photo
                else message.effective_attachment.file_id
            )

            if media_type == "photo":
                new_file = await context.bot.getFile(media_id)
                await new_file.download_to_drive(custom_path='image/p1.jpg')
                response = send_embed_to_discord_channel(dc_channel_id, dc_bot_token, title, content, update.message.link, ['image/p1.jpg'])


def main():
    # Build bot
    pers = PicklePersistence("persistence")
    defaults = Defaults(parse_mode="HTML", disable_notification=True)
    application = (
        ApplicationBuilder()
        .token(tg_bot_token)
        .persistence(pers)
        .defaults(defaults)
        .post_init(post_init)
        .build()
    )

    # Setup handler
    start_handler = CommandHandler('start', start)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    new_msg_handler = MessageHandler(filters.TEXT | filters.PHOTO, new_msg)

    # Add handler
    application.add_handler(start_handler)
    application.add_handler(unknown_handler)
    application.add_handler(new_msg_handler)

    # run!
    application.run_polling()

if __name__ == "__main__":
    # Avoiding file read/write errors
    if not os.path.exists('image'):
        os.mkdir('image')
    for i in range(1, 11):
        filename = f"image/p{i}.jpg"
        with open(filename, 'wb') as f:
            pass
    main()