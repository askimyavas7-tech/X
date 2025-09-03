from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import logging

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

# Basit log ayarı
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

def PlayWrapper(command):
    async def wrapper(client, message):
        logging.info(f"Komut alındı: {message.text} | Kullanıcı: {message.from_user.id}")

        # Bakım modu kontrolü
        if await is_maintenance() is False:
            if message.from_user.id not in SUDOERS:
                logging.warning(f"Kullanıcı {message.from_user.id} bakım modunda komut gönderdi")
                return await message.reply_text(
                    "Bot bakımda. Lütfen bir süre bekleyin..."
                )

        # Özel bot modu kontrolü
        if PRIVATE_BOT_MODE == str(True):
            if not await is_served_private_chat(message.chat.id):
                logging.info(f"Özel bot modu: Kullanıcı {message.from_user.id} yetkisiz chat")
                await message.reply_text(
                    "**Özel Müzik Botu**\n\nYalnızca sahibinden gelen yetkili sohbetler için. "
                    "Önce sahibimden sohbetinize izin vermesini isteyin."
                )
                return await app.leave_chat(message.chat.id)

        # Komut silme özelliği
        if await is_commanddelete_on(message.chat.id):
            try:
                await message.delete()
                logging.info("Komut silindi")
            except Exception as e:
                logging.warning(f"Komut silinirken hata oluştu: {e}")

        # Dil ayarı
        language = await get_lang(message.chat.id)
        _ = get_string(language)
        logging.info(f"Dil ayarı: {language}")

        # Telegram mesajlarından ses ve video tespiti
        audio_telegram = (
            message.reply_to_message.audio
            or message.reply_to_message.voice
        ) if message.reply_to_message else None

        video_telegram = (
            message.reply_to_message.video
            or message.reply_to_message.document
        ) if message.reply_to_message else None

        url = await YouTube.url(message)
        logging.info(f"URL: {url}, Audio: {bool(audio_telegram)}, Video: {bool(video_telegram)}")

        # Hiçbir medya veya URL yoksa
        if audio_telegram is None and video_telegram is None and url is None:
            if len(message.command) < 2:
                if "stream" in message.command:
                    logging.info("Stream komutu ama input yok")
                    return await message.reply_text(_["str_1"])
                buttons = botplaylist_markup(_)
                logging.info("Playlist gösteriliyor")
                return await message.reply_photo(
                    photo=PLAYLIST_IMG_URL,
                    caption=_["playlist_1"],
                    reply_markup=InlineKeyboardMarkup(buttons),
                )

        # Kanal üzerinden anonim gönderim kontrolü
        if message.sender_chat:
            upl = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Bunu Nasıl Düzeltirim?", 
                            callback_data="AnonymousAdmin",
                        ),
                    ]
                ]
            )
            logging.info("Anonim admin kontrolü tetiklendi")
            return await message.reply_text(
                _["general_4"], reply_markup=upl
            )

        # Chat modu
        if message.command[0][0] == "c":
            chat_id = await get_cmode(message.chat.id)
            if chat_id is None:
                logging.info("Chat modu aktif ama chat bulunamadı")
                return await message.reply_text(_["setting_12"])
            try:
                chat = await app.get_chat(chat_id)
                logging.info(f"Chat bulundu: {chat.title}")
            except Exception as e:
                logging.warning(f"Chat alınamadı: {e}")
                return await message.reply_text(_["cplay_4"])
            channel = chat.title
        else:
            chat_id = message.chat.id
            channel = None
            logging.info(f"Normal chat modu: {chat_id}")

        # Oynatma modu ve tipi
        playmode = await get_playmode(message.chat.id)
        playty = await get_playtype(message.chat.id)
        logging.info(f"Play mode: {playmode}, Play type: {playty}")

        # Yetki kontrolü
        if playty != "Everyone":
            if message.from_user.id not in SUDOERS:
                admins = adminlist.get(message.chat.id)
                if not admins:
                    logging.warning("Yönetici listesi boş")
                    return await message.reply_text(_["admin_18"])
                elif message.from_user.id not in admins:
                    logging.info(f"Kullanıcı {message.from_user.id} yetkisiz")
                    return await message.reply_text(_["play_4"])

        # Video kontrolü
        if message.command[0][0] == "v":
            video = True
        else:
            if "-v" in message.text:
                video = True
            else:
                video = True if message.command[0][1] == "v" else None
        logging.info(f"Video modu: {video}")

        # Fplay kontrolü
        if message.command[0][-1] == "e":
            if not await is_active_chat(chat_id):
                logging.info("Fplay: Aktif chat değil")
                return await message.reply_text(_["play_18"])
            fplay = True
        else:
            fplay = None

        logging.info("Asıl komut çağrılıyor")
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
        )

    return wrapper
