import os
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from subsai import SubsAI

load_dotenv()

Bot = Client(
    "PersianTranscriberBot",
    bot_token = os.environ["BOT_TOKEN"],
    api_id = int(os.environ["API_ID"]),
    api_hash = os.environ["API_HASH"]
)

subs_ai = SubsAI()
model = subs_ai.create_model('guillaumekln/faster-whisper', {'model_type': 'base'})

START_TXT = """
Hi {}, I'm whisper Bot.

Send a video to transcribe and generate srt.
"""

START_BTN = InlineKeyboardMarkup(
        [[
        InlineKeyboardButton('Source Code', url='https://github.com/soebb/whisper-bot'),
        ]]
    )


@Bot.on_message(filters.command(["start"]))
async def start(bot, update):
    text = START_TXT.format(update.from_user.mention)
    reply_markup = START_BTN
    await update.reply_text(
        text=text,
        disable_web_page_preview=True,
        reply_markup=reply_markup
    )


@Bot.on_message(filters.private & (filters.video | filters.document))
async def from_tg_files(_, m):
    if m.document and not m.document.mime_type.startswith("video/"):
        return
    msg = await m.reply("Downloading..")
    media = await m.download()
    await msg.edit_text("Processing..")
    subs = subs_ai.transcribe(media, model)
    output_name = "out.srt"
    subs.save(output_name)
    await m.reply_document(output_name)
    await msg.delete()
    os.remove(output_name)
    os.remove(media)


Bot.run()
