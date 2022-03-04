# Copyright @Tellybots | @ShriMadhavUk
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import random
import numpy
import os
from PIL import Image
import time

# the Strings used for this "thing"
from plugins.main import Translation
from pyrogram import Client
from plugins.config import Config
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
logging.getLogger("pyrogram").setLevel(logging.WARNING)
from pyrogram import filters
from .database.database import db
from .functions.help_Nekmo_ffmpeg import take_screen_shot


@Client.on_message(filters.private & filters.photo & ~filters.edited)
async def photo_handler(bot: Client, event: Message):

    editable = await event.reply_text("**👀 Processing...**")
    await db.set_thumbnail(event.from_user.id, thumbnail=event.photo.file_id)
    await editable.edit("**✅ Custom Thumbnail Saved Successfully!**")


@Client.on_message(filters.private & filters.command(["deletethumb", "deletethumbnail"]) & ~filters.edited)
async def delete_thumb_handler(bot: Client, event: Message):

    await db.set_thumbnail(event.from_user.id, thumbnail=None)
    await event.reply_text(
        "**🗑️ Custom Thumbnail Deleted Successfully!**",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⚙ Configure Settings 👀", callback_data="openSettings")]
        ])
    )


@Client.on_message(filters.private & filters.command(["showthumb", "showthumbnail"]) & ~filters.edited)
async def show_thumb_handler(bot: Client, event: Message):

    _thumbnail = await db.get_thumbnail(event.from_user.id)
    if _thumbnail is not None:
        try:
            await bot.send_photo(
                chat_id=event.chat.id,
                photo=_thumbnail,
                text=f"**👆🏻 Your Custom Thumbnail...**", 
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("🗑️ Delete Thumbnail", callback_data="deleteThumbnail")]]
                ),
                reply_to_message_id=event.message_id
            )
        except Exception as err:
            try:
                await bot.send_message(
                    chat_id=event.chat.id,
                    text=f"**😐 Unable to send Thumbnail! Got an unexpected Error**",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⛔ Close", callback_data="close")],[InlineKeyboardButton("📮 Report issue", url="https://t.me/Tellybots_Support")]]),
                    reply_to_message_id=event.message_id
                )
            except:
                pass
    else:
        await event.reply_text("**🤧 No Thumbnail Found, Send any image to set it as your custom Thumbnail**", quote=True)


async def Gthumb01(bot, update):
    thumb_image_path = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".jpg"
    db_thumbnail = await db.get_thumbnail(update.from_user.id)
    if db_thumbnail is not None:
        thumbnail = await bot.download_media(message=db_thumbnail, file_name=thumb_image_path)
        Image.open(thumbnail).convert("RGB").save(thumbnail)
        img = Image.open(thumbnail)
        img.resize((100, 100))
        img.save(thumbnail, "JPEG")
    else:
        thumbnail = None

    return thumbnail

async def Gthumb02(bot, update, duration, download_directory):
    thumb_image_path = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".jpg"
    db_thumbnail = await db.get_thumbnail(update.from_user.id)
    if db_thumbnail is not None:
        thumbnail = await bot.download_media(message=db_thumbnail, file_name=thumb_image_path)
    else:
        thumbnail = await take_screen_shot(download_directory, os.path.dirname(download_directory), random.randint(0, duration - 1))

    return thumbnail

async def Mdata01(download_directory):

          width = 0
          height = 0
          duration = 0
          metadata = extractMetadata(createParser(download_directory))
          if metadata is not None:
              if metadata.has("duration"):
                  duration = metadata.get('duration').seconds
              if metadata.has("width"):
                  width = metadata.get("width")
              if metadata.has("height"):
                  height = metadata.get("height")

          return width, height, duration

async def Mdata02(download_directory):

          width = 0
          duration = 0
          metadata = extractMetadata(createParser(download_directory))
          if metadata is not None:
              if metadata.has("duration"):
                  duration = metadata.get('duration').seconds
              if metadata.has("width"):
                  width = metadata.get("width")

          return width, duration

async def Mdata03(download_directory):

          duration = 0
          metadata = extractMetadata(createParser(download_directory))
          if metadata is not None:
              if metadata.has("duration"):
                  duration = metadata.get('duration').seconds

          return duration
