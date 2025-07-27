#
# Copyright (C) 2021-2023 by ArchBots@Github, < https://github.com/ArchBots >.
# This file is part of < https://github.com/ArchBots/ArchMusic > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/ArchBots/ArchMusic/blob/master/LICENSE >
#

import asyncio
from datetime import datetime
import pytz

from pyrogram import filters
from pyrogram.enums import ChatMembersFilter
from pyrogram.types import CallbackQuery, Message

from config import BANNED_USERS, MUSIC_BOT_NAME, adminlist, lyrical, LOG_GROUP_ID
from strings import get_command
from ArchMusic import app
from ArchMusic.core.call import ArchMusic
from ArchMusic.misc import db
from ArchMusic.utils.database import get_authuser_names, get_cmode
from ArchMusic.utils.decorators import ActualAdminCB, AdminActual, language
from ArchMusic.utils.formatters import alpha_to_int

RELOAD_COMMAND = get_command("RELOAD_COMMAND")
RESTART_COMMAND = get_command("RESTART_COMMAND")


@app.on_message(filters.command(RELOAD_COMMAND) & filters.group & ~BANNED_USERS)
@language
async def reload_admin_cache(client, message: Message, _):
    try:
        chat_id = message.chat.id
        admins = app.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS)
        authusers = await get_authuser_names(chat_id)
        adminlist[chat_id] = []

        async for user in admins:
            if user.privileges.can_manage_video_chats:
                adminlist[chat_id].append(user.user.id)
        for user in authusers:
            user_id = await alpha_to_int(user)
            adminlist[chat_id].append(user_id)

        await message.reply_text(_["admin_20"])

        # Saat bilgisi (Europe/Istanbul)
        turkey_time = datetime.now(pytz.timezone("Europe/Istanbul")).strftime('%Y-%m-%d %H:%M:%S')

        # Log gruba bildirim gönder
        try:
            await app.send_message(
                LOG_GROUP_ID,
                f"♻️ <b>Admin Cache Yenilendi</b>\n"
                f"🛠️ <b>Komut:</b> /{RELOAD_COMMAND[0]}\n"
                f"🕒 <b>Zaman:</b> {turkey_time} (Europe/Istanbul)\n"
                f"👤 <b>Kullanıcı:</b> {message.from_user.mention} [`{message.from_user.id}`]\n"
                f"🗨️ <b>Sohbet:</b> {message.chat.title} [`{message.chat.id}`]"
            )
        except:
            pass

    except:
        await message.reply_text(
            "Yönetici önbelleği yeniden yüklenemedi. Bot'un yönetici olduğundan emin olun."
        )


@app.on_message(filters.command(RESTART_COMMAND) & filters.group & ~BANNED_USERS)
@AdminActual
async def restartbot(client, message: Message, _):
    mystic = await message.reply_text(
        f"Lütfen Bekleyin.. {MUSIC_BOT_NAME} sohbetiniz için yeniden başlatılıyor.."
    )
    await asyncio.sleep(1)
    try:
        db[message.chat.id] = []
        await ArchMusic.stop_stream(message.chat.id)
    except:
        pass
    chat_id = await get_cmode(message.chat.id)
    if chat_id:
        try:
            await app.get_chat(chat_id)
        except:
            pass
        try:
            db[chat_id] = []
            await ArchMusic.stop_stream(chat_id)
        except:
            pass
    await mystic.edit_text("Başarıyla yeniden başlatıldı. Şimdi oynamayı deneyin..")

    # Saat bilgisi (Europe/Istanbul)
    turkey_time = datetime.now(pytz.timezone("Europe/Istanbul")).strftime('%Y-%m-%d %H:%M:%S')

    # Log gruba bildirim gönder
    try:
        await app.send_message(
            LOG_GROUP_ID,
            f"🔄 <b>Bot Yeniden Başlatıldı</b>\n"
            f"🛠️ <b>Komut:</b> /{RESTART_COMMAND[0]}\n"
            f"🕒 <b>Zaman:</b> {turkey_time} (Europe/Istanbul)\n"
            f"👤 <b>Kullanıcı:</b> {message.from_user.mention} [`{message.from_user.id}`]\n"
            f"🗨️ <b>Sohbet:</b> {message.chat.title} [`{message.chat.id}`]"
        )
    except:
        pass


@app.on_callback_query(filters.regex("close") & ~BANNED_USERS)
async def close_menu(_, CallbackQuery):
    try:
        await CallbackQuery.message.delete()
        await CallbackQuery.answer()
    except:
        return


@app.on_callback_query(filters.regex("stop_downloading") & ~BANNED_USERS)
@ActualAdminCB
async def stop_download(client, CallbackQuery: CallbackQuery, _):
    message_id = CallbackQuery.message.message_id
    task = lyrical.get(message_id)
    if not task:
        return await CallbackQuery.answer("İndirme zaten tamamlandı.", show_alert=True)

    if task.done() or task.cancelled():
        return await CallbackQuery.answer(
            "İndirme zaten Tamamlandı veya İptal Edildi.", show_alert=True
        )

    try:
        task.cancel()
        lyrical.pop(message_id, None)
        await CallbackQuery.answer("İndirme İptal Edildi", show_alert=True)
        return await CallbackQuery.edit_message_text(
            f"İndirme İptal Edildi {CallbackQuery.from_user.mention}"
        )
    except:
        return await CallbackQuery.answer("İndirme durdurulamadı.", show_alert=True)
