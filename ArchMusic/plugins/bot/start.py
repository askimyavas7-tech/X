# Copyright (C) 2021-2023 by ArchBots@Github.
# This file is part of ArchMusic Project.
# Released under GNU v3.0 License.

import asyncio
from pyrogram import filters
from pyrogram.enums import ChatType, ParseMode
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from youtubesearchpython.__future__ import VideosSearch

import config
from config import BANNED_USERS
from config.config import OWNER_ID
from strings import get_command, get_string
from ArchMusic import Telegram, YouTube, app
from ArchMusic.misc import SUDOERS
from ArchMusic.plugins.play.playlist import del_plist_msg
from ArchMusic.plugins.sudo.sudoers import sudoers_list
from ArchMusic.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_assistant,
    get_lang,
    get_userss,
    is_on_off,
    is_served_private_chat,
)
from ArchMusic.utils.decorators.language import LanguageStart
from ArchMusic.utils.inline import help_pannel, private_panel, start_pannel

loop = asyncio.get_running_loop()


@app.on_message(
    filters.command(get_command("START_COMMAND"))
    & filters.private
    & ~BANNED_USERS
)
@LanguageStart
async def start_comm(client, message: Message, _):
    # 🌟 Havalı yüklenme animasyonu
    loading = await message.reply_text("🚀 Bot başlatılıyor...")
    await asyncio.sleep(0.8)
    await loading.edit("🔄 Modüller yükleniyor...")
    await asyncio.sleep(0.8)
    await loading.edit("⚙️ Panel hazırlanıyor...")
    await asyncio.sleep(0.8)
    await loading.edit("💫 Neredeyse hazır...")
    await asyncio.sleep(1)

    # Kullanıcıyı veritabanına ekle
    await add_served_user(message.from_user.id)

    # Komut parametresi varsa kontrol et
    if len(message.text.split()) > 1:
        await loading.delete()
        name = message.text.split(None, 1)[1]
        # /help start
        if name.startswith("help"):
            keyboard = help_pannel(_)
            return await message.reply_text(_["help_1"], reply_markup=keyboard)
        # /song start
        if name.startswith("song"):
            return await message.reply_text(_["song_2"])
        # /sta start
        if name.startswith("sta"):
            m = await message.reply_text("🔎 Kişisel istatistikleriniz getiriliyor...")
            stats = await get_userss(message.from_user.id)
            if not stats:
                await asyncio.sleep(1)
                return await m.edit(_["ustats_1"])

            def get_stats():
                msg = ""
                limit = 0
                results = {}
                for i in stats:
                    top_list = stats[i]["spot"]
                    results[str(i)] = top_list
                    list_arranged = dict(
                        sorted(results.items(), key=lambda item: item[1], reverse=True)
                    )
                if not results:
                    return m.edit(_["ustats_1"])
                tota = 0
                videoid = None
                for vidid, count in list_arranged.items():
                    tota += count
                    if limit == 10:
                        continue
                    if limit == 0:
                        videoid = vidid
                    limit += 1
                    details = stats.get(vidid)
                    title = (details["title"][:35]).title()
                    if vidid == "telegram":
                        msg += f"🎧 [Telegram Dosyaları](https://t.me/telegram) **{count} kez oynatıldı**\n\n"
                    else:
                        msg += f"🎵 [{title}](https://www.youtube.com/watch?v={vidid}) **{count} kez oynatıldı**\n\n"
                msg = _["ustats_2"].format(len(stats), tota, limit) + msg
                return videoid, msg

            try:
                videoid, msg = await loop.run_in_executor(None, get_stats)
            except Exception as e:
                print(e)
                return
            thumbnail = await YouTube.thumbnail(videoid, True)
            await m.delete()
            return await message.reply_photo(photo=thumbnail, caption=msg)
        # /sud start
        if name.startswith("sud"):
            await sudoers_list(client=client, message=message, _=_)
            if await is_on_off(config.LOG):
                return await app.send_message(
                    config.LOG_GROUP_ID,
                    f"{message.from_user.mention} az önce **SUDO LİSTESİNİ** kontrol etti.",
                )
            return
        # /lyr start
        if name.startswith("lyr"):
            query = (str(name)).replace("lyrics_", "", 1)
            lyrical = config.lyrical
            lyrics = lyrical.get(query)
            return await Telegram.send_split_text(
                message, lyrics or "Şarkı sözleri bulunamadı."
            )
        # /del start
        if name.startswith("del"):
            await del_plist_msg(client=client, message=message, _=_)
        # /inf start
        if name.startswith("inf"):
            m = await message.reply_text("🔎 Bilgi Alınıyor...")
            query = (str(name)).replace("info_", "", 1)
            query = f"https://www.youtube.com/watch?v={query}"
            results = VideosSearch(query, limit=1)
            for result in (await results.next())["result"]:
                title = result["title"]
                duration = result["duration"]
                views = result["viewCount"]["short"]
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
                channellink = result["channel"]["link"]
                channel = result["channel"]["name"]
                link = result["link"]
                published = result["publishedTime"]
            caption = f"""
🎬 **{title}**
⏳ Süre: {duration}
👀 Görüntüleme: {views}
🕒 Yayın: {published}
📺 Kanal: [{channel}]({channellink})
🔗 [YouTube'da İzle]({link})
"""
            key = InlineKeyboardMarkup(
                [[InlineKeyboardButton("🎥 İzle", url=link), InlineKeyboardButton("❌ Kapat", callback_data="close")]]
            )
            await m.delete()
            return await app.send_photo(
                message.chat.id, photo=thumbnail, caption=caption, reply_markup=key
            )

    # Normal /start paneli
    await loading.delete()
    try:
        await app.resolve_peer(OWNER_ID[0])
        OWNER = OWNER_ID[0]
    except:
        OWNER = None
    out = private_panel(_, app.username, OWNER)
    caption = f"✨ {config.MUSIC_BOT_NAME} seni karşıladı!\n\n🎶 Tüm müzik komutları için aşağıdaki paneli kullanabilirsin."
    if config.START_IMG_URL:
        try:
            await message.reply_photo(
                photo=config.START_IMG_URL,
                caption=caption,
                reply_markup=InlineKeyboardMarkup(out),
            )
        except:
            await message.reply_text(caption, reply_markup=InlineKeyboardMarkup(out))
    else:
        await message.reply_text(caption, reply_markup=InlineKeyboardMarkup(out))
    if await is_on_off(config.LOG):
        await app.send_message(
            config.LOG_GROUP_ID,
            f"{message.from_user.mention}, botu başlattı ve paneli görüntüledi.",
        )


# ===============================================================
# GRUPA EKLENİNCE HOŞGELDİN MESAJI
# ===============================================================

welcome_group = 2

@app.on_message(filters.new_chat_members, group=welcome_group)
async def welcome(client, message: Message):
    chat_id = message.chat.id
    if config.PRIVATE_BOT_MODE == str(True):
        if not await is_served_private_chat(message.chat.id):
            await message.reply_text(
                "**Özel Müzik Botu**\n\nYalnızca sahibinden yetkili sohbetlerde kullanılabilir."
            )
            return await app.leave_chat(message.chat.id)
    else:
        await add_served_chat(chat_id)
    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)
            if member.id == app.id:
                chat_type = message.chat.type
                if chat_type != ChatType.SUPERGROUP:
                    await message.reply_text(_["start_6"])
                    return await app.leave_chat(message.chat.id)
                if chat_id in await blacklisted_chats():
                    await message.reply_text(
                        _["start_7"].format(f"https://t.me/{app.username}?start=sudolist")
                    )
                    return await app.leave_chat(chat_id)
                userbot = await get_assistant(message.chat.id)
                out = start_pannel(_)
                video_url = "https://telegra.ph/file/acfb445238b05315f0013.mp4"
                video_caption = _["start_3"].format(
                    config.MUSIC_BOT_NAME, userbot.username, userbot.id
                )
                await app.send_video(
                    message.chat.id,
                    video_url,
                    caption=video_caption,
                    reply_markup=InlineKeyboardMarkup(out),
                )
            if member.id in config.OWNER_ID:
                return await message.reply_text(
                    _["start_4"].format(config.MUSIC_BOT_NAME, member.mention)
                )
            if member.id in SUDOERS:
                return await message.reply_text(
                    _["start_5"].format(config.MUSIC_BOT_NAME, member.mention)
                )
        except:
            return
