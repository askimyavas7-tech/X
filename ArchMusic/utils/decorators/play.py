#
# Copyright (C) 2021-2023 by ArchBots@Github, < https://github.com/ArchBots >.
#
# This file is part of < https://github.com/ArchBots/ArchMusic > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/ArchBots/ArchMusic/blob/master/LICENSE >
#
# All rights reserved.
#

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import PLAYLIST_IMG_URL, PRIVATE_BOT_MODE, adminlist
from strings import get_string
from ArchMusic import YouTube, app
from ArchMusic.misc import SUDOERS
from ArchMusic.utils.database import (get_cmode, get_lang,
                                       get_playmode, get_playtype,
                                       is_active_chat,
                                       is_commanddelete_on,
                                       is_served_private_chat)
from ArchMusic.utils.database.memorydatabase import is_maintenance
from ArchMusic.utils.inline.playlist import botplaylist_markup


def PlayWrapper(command):
    """
    Bu dekoratör, komutları sarmalayarak müzik çalma öncesi kontrolleri yapar.
    - Bakım modunu kontrol eder.
    - Özel bot modunu kontrol eder.
    - Komutları otomatik silebilir.
    - Medya veya URL kontrolü yapar.
    - Yetki kontrollerini uygular.
    """
    async def wrapper(client, message):
        # Bakım modu kontrolü
        if await is_maintenance() is False:
            if message.from_user.id not in SUDOERS:
                return await message.reply_text(
                    "Bot bakımda. Lütfen bir süre bekleyin..."
                )

        # Özel bot modu kontrolü
        if PRIVATE_BOT_MODE == str(True):
            if not await is_served_private_chat(message.chat.id):
                await message.reply_text(
                    "**Özel Müzik Botu**\n\nYalnızca sahibinden gelen yetkili sohbetler için. Önce sahibimden sohbetinize izin vermesini isteyin."
                )
                return await app.leave_chat(message.chat.id)

        # Komut otomatik silme
        if await is_commanddelete_on(message.chat.id):
            try:
                await message.delete()
            except:
                pass

        # Kullanıcı dili
        language = await get_lang(message.chat.id)
        _ = get_string(language)

        # Telegram mesajından medya alma
        audio_telegram = (
            (message.reply_to_message.audio or message.reply_to_message.voice)
            if message.reply_to_message
            else None
        )
        video_telegram = (
            (message.reply_to_message.video or message.reply_to_message.document)
            if message.reply_to_message
            else None
        )

        # YouTube URL kontrolü
        url = await YouTube.url(message)

        # Eğer medya veya URL yoksa
        if audio_telegram is None and video_telegram is None and url is None:
            if len(message.command) < 2:
                if "stream" in message.command:
                    return await message.reply_text(_["str_1"])
                buttons = botplaylist_markup(_)
                return await message.reply_photo(
                    photo=PLAYLIST_IMG_URL,
                    caption=_["playlist_1"],
                    reply_markup=InlineKeyboardMarkup(buttons),
                )

        # Gönderen bir kanal ise
        if message.sender_chat:
            upl = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="How to Fix this? ",
                            callback_data="AnonymousAdmin",
                        ),
                    ]
                ]
            )
            return await message.reply_text(
                _["general_4"], reply_markup=upl
            )

        # Kanal oynatma modu
        if message.command[0][0] == "c":
            chat_id = await get_cmode(message.chat.id)
            if chat_id is None:
                return await message.reply_text(_["setting_12"])
            try:
                chat = await app.get_chat(chat_id)
            except:
                return await message.reply_text(_["cplay_4"])
            channel = chat.title
        else:
            chat_id = message.chat.id
            channel = None

        # Oynatma modu ve türü
        playmode = await get_playmode(message.chat.id)
        playty = await get_playtype(message.chat.id)

        # Yetki kontrolü
        if playty != "Everyone":
            if message.from_user.id not in SUDOERS:
                admins = adminlist.get(message.chat.id)
                if not admins:
                    return await message.reply_text(_["admin_18"])
                else:
                    if message.from_user.id not in admins:
                        return await message.reply_text(_["play_4"])

        # Video kontrolü
        if message.command[0][0] == "v":
            video = True
        else:
            if "-v" in message.text:
                video = True
            else:
                video = True if message.command[0][1] == "v" else None

        # Fplay kontrolü
        if message.command[0][-1] == "e":
            if not await is_active_chat(chat_id):
                return await message.reply_text(_["play_18"])
            fplay = True
        else:
            fplay = None

        # play_logs için eksik parametreler
        duration = None       # Oynatma süresi (varsa YouTube veya medya objesinden alınabilir)
        filesize = None       # Dosya boyutu
        start_time = None     # Çalma başlangıç zamanı
        end_time = None       # Çalma bitiş zamanı
        requester = message.from_user.id  # Komutu gönderen kullanıcı

        # Komutu çalıştır
        return await command(
            client,
            message,
            _,
            chat_id,
            video,
            channel,
            playmode,
            url,
            fplay,
            duration=duration,
            filesize=filesize,
            start_time=start_time,
            end_time=end_time,
            requester=requester
        )

    return wrapper
