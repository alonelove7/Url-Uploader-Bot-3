# © Shrimadhav Uk | @Tellybots

import os
import asyncio
import time
import psutil
import shutil
import string
from pyrogram import Client, filters
from asyncio import TimeoutError
from pyrogram.errors import MessageNotModified
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery, ForceReply
from plugins.config import Config
from plugins.button import youtube_dl_call_back
from plugins.link import ddl_call_back
from plugins.main import Translation
from plugins.database.database import db

@Client.on_callback_query()
async def button(bot, update):
    if "|" in update.data:
        await youtube_dl_call_back(bot, update)
    elif "=" in update.data:
        await ddl_call_back(bot, update)
    elif update.data == "home":
        await update.message.edit_text(
            text=Translation.START_TEXT.format(update.from_user.mention),
            reply_markup=Translation.START_BUTTONS,
            disable_web_page_preview=True
        )
    elif update.data == "help":
        await update.message.edit_text(
            text=Translation.HELP_TEXT,
            reply_markup=Translation.HELP_BUTTONS,
            disable_web_page_preview=True
        )
    elif update.data == "about":
        await update.message.edit_text(
            text=Translation.ABOUT_TEXT,
            reply_markup=Translation.ABOUT_BUTTONS,
            disable_web_page_preview=True
        )
    else:
        await update.message.delete()

async def OpenSettings(event: Message, user_id: int):
    try:
        await event.edit(
            text="**⚙ Configure My Behaviour**",
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton(f"🔰 Upload as {'File 🗃️' if ((await db.get_upload_as_doc(user_id)) is True) else 'Video 🎥'}",
                                          callback_data="triggerUploadMode")],
                    [InlineKeyboardButton("🌆 Custom Thumbnail ", callback_data="triggerThumbnail")],
                    [InlineKeyboardButton("⛔ Close Settings", callback_data="close")]
                ]
            )
        )
    except FloodWait as e:
        await asyncio.sleep(e.x)
        await OpenSettings(event, user_id)
    except MessageNotModified:
        pass

@Client.on_callback_query()
async def callback_handlers(bot: Client, cb: CallbackQuery):
    if "closeMe" in cb.data:
        await cb.message.delete(True)
        await cb.message.reply_to_message.delete()
    elif "clox" in cb.data:
        await cb.message.delete(True)
        await cb.message.reply_to_message.delete()
    elif "openSettings" in cb.data:
        await OpenSettings(cb.message, user_id=cb.from_user.id)
    elif "triggerUploadMode" in cb.data:
        upload_as_doc = await db.get_upload_as_doc(cb.from_user.id)
        if upload_as_doc is True:
            await db.set_upload_as_doc(cb.from_user.id, upload_as_doc=False)
        else:
            await db.set_upload_as_doc(cb.from_user.id, upload_as_doc=True)
        await OpenSettings(cb.message, user_id=cb.from_user.id)

    elif "triggerThumbnail" in cb.data:
        thumbnail = await db.get_thumbnail(cb.from_user.id)
        if thumbnail is None:
            await cb.answer("No Thumbnail Found... ", show_alert=True)
        else:
            await cb.answer("Trying to send your thumbnail...", show_alert=True)
            try:
                await bot.send_photo(
                    chat_id=cb.message.chat.id,
                    photo=thumbnail,
                    text=f"**👆🏻 Your Custom Thumbnail...\n© @AVBotz**",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🗑️ Delete Thumbnail", callback_data="deleteThumbnail")]])
                )
            except Exception as err:
                try:
                    await bot.send_message(
                        chat_id=cb.message.chat.id,
                        text=f"**😐 Unable to send Thumbnail! Got an unexpected Error**",
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⛔ Close", callback_data="closeMeh")],[InlineKeyboardButton("📮 Report issue", url="https://t.me/AVBotz_Support")]])
                    )
                except:
                    pass
    elif "deleteThumbnail" in cb.data:
        await db.set_thumbnail(cb.from_user.id, thumbnail=None)
        await cb.answer("Successfully Removed Custom Thumbnail!", show_alert=True)
        await cb.message.delete(True)
            
