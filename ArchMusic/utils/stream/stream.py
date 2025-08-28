import os
from random import randint
from typing import Union

from pyrogram.types import InlineKeyboardMarkup

import config
from ArchMusic import Carbon, YouTube, app
from ArchMusic.core.call import ArchMusic
from ArchMusic.misc import db
from ArchMusic.utils.database import (
    add_active_chat,
    add_active_video_chat,
    is_active_chat,
    is_video_allowed,
    music_on,
)
from ArchMusic.utils.exceptions import AssistantErr
from ArchMusic.utils.inline.play import stream_markup, telegram_markup
from ArchMusic.utils.inline.playlist import close_markup
from ArchMusic.utils.pastebin import ArchMusicbin
from ArchMusic.utils.stream.queue import put_queue, put_queue_index


async def send_stream_message(_, chat_id, text):
    """Mesaj gönderme yardımcı fonksiyonu."""
    return await app.send_message(chat_id=chat_id, text=text)


async def handle_stream_entry(
    _,
    chat_id,
    original_chat_id,
    user_name,
    file_path,
    title,
    duration_min,
    user_id,
    source,
    video=None,
    vidid=None,
    forceplay=None,
):
    """Kuyruğa ekleme ve mesaj gönderme fonksiyonu."""
    status = True if video else None
    is_active = await is_active_chat(chat_id)

    if is_active:
        await put_queue(
            chat_id,
            original_chat_id,
            file_path if vidid is None else f"vid_{vidid}",
            title,
            duration_min,
            user_name,
            vidid or source,
            user_id,
            "video" if video else "audio",
        )
        position = len(db.get(chat_id, [])) - 1
        await send_stream_message(
            _, chat_id=original_chat_id,
            text=_["queue_4"].format(position, title, duration_min, user_name)
        )
    else:
        if not forceplay:
            db[chat_id] = []
        await ArchMusic.join_call(chat_id, original_chat_id, file_path, video=status)
        await put_queue(
            chat_id,
            original_chat_id,
            file_path if vidid is None else f"vid_{vidid}",
            title,
            duration_min,
            user_name,
            vidid or source,
            user_id,
            "video" if video else "audio",
            forceplay=forceplay,
        )

        if source == "telegram" and video:
            await add_active_video_chat(chat_id)

        info_link = f"https://t.me/{app.username}?start=info_{vidid}" if vidid else ""
        if source in ["youtube", "live", "playlist"]:
            message_text = _["stream_1"].format(title, info_link, duration_min, user_name)
        elif source == "soundcloud":
            message_text = _["stream_3"].format(title, duration_min, user_name)
        else:
            message_text = _["stream_4"].format(title, info_link or file_path, duration_min, user_name)

        run = await send_stream_message(_, chat_id=original_chat_id, text=message_text)
        db[chat_id][0]["mystic"] = run
        db[chat_id][0]["markup"] = "tg" if source in ["soundcloud", "telegram", "live", "index"] else "stream"


async def stream(
    _,
    mystic,
    user_id,
    result,
    chat_id,
    user_name,
    original_chat_id,
    video: Union[bool, str] = None,
    streamtype: Union[bool, str] = None,
    spotify: Union[bool, str] = None,
    forceplay: Union[bool, str] = None,
):
    if not result:
        return

    if video and not await is_video_allowed(chat_id):
        raise AssistantErr(_["play_7"])

    if forceplay:
        await ArchMusic.force_stop_stream(chat_id)

    def get_position(chat):
        return len(db.get(chat, [])) - 1

    # ---------------- PLAYLIST ----------------
    if streamtype == "playlist":
        msg = f"{_['playlist_16']}\n\n"
        count = 0
        for search in result:
            if count >= config.PLAYLIST_FETCH_LIMIT:
                break
            try:
                title, duration_min, duration_sec, thumbnail, vidid = await YouTube.details(
                    search, False if spotify else True
                )
            except Exception:
                continue

            if duration_min is None or duration_sec > config.DURATION_LIMIT:
                continue

            file_path, direct = None, False
            if not await is_active_chat(chat_id):
                try:
                    file_path, direct = await YouTube.download(
                        vidid, mystic, video=True if video else None, videoid=True
                    )
                except Exception:
                    continue

            await handle_stream_entry(
                _, chat_id, original_chat_id, user_name,
                file_path if file_path else f"vid_{vidid}",
                title,
                duration_min,
                user_id,
                source="playlist",
                video=video,
                vidid=vidid,
                forceplay=forceplay,
            )

            count += 1
            msg += f"{count}- {title[:70]}\n"
            msg += f"{_['playlist_17']} {get_position(chat_id)}\n\n"

        if count == 0:
            return
        link = await ArchMusicbin(msg)
        car = os.linesep.join(msg.split(os.linesep)[:17]) if msg.count("\n") >= 17 else msg
        await Carbon.generate(car, randint(100, 10000000))
        upl = close_markup(_)
        await send_stream_message(
            _, chat_id=original_chat_id,
            text=_["playlist_18"].format(link, get_position(chat_id)),
        )
        return

    # ---------------- YOUTUBE, SOUNDCLOUD, TELEGRAM, LIVE, INDEX ----------------
    if streamtype in ["youtube", "soundcloud", "telegram", "live", "index"]:
        if streamtype == "youtube":
            vidid = result.get("vidid")
            title = (result.get("title") or "").title()
            duration_min = result.get("duration_min")
            try:
                file_path, direct = await YouTube.download(vidid, mystic, videoid=True, video=video)
            except Exception:
                raise AssistantErr(_["play_16"])
            await handle_stream_entry(
                _, chat_id, original_chat_id, user_name,
                file_path, title, duration_min, user_id,
                source="youtube", video=video, vidid=vidid, forceplay=forceplay
            )

        elif streamtype == "soundcloud":
            file_path = result.get("filepath")
            title = result.get("title")
            duration_min = result.get("duration_min")
            await handle_stream_entry(
                _, chat_id, original_chat_id, user_name,
                file_path, title, duration_min, user_id,
                source="soundcloud", video=None, forceplay=forceplay
            )

        elif streamtype == "telegram":
            file_path = result.get("path")
            title = (result.get("title") or "").title()
            duration_min = result.get("dur")
            await handle_stream_entry(
                _, chat_id, original_chat_id, user_name,
                file_path, title, duration_min, user_id,
                source="telegram", video=video, forceplay=forceplay
            )

        elif streamtype == "live":
            link = result.get("link")
            vidid = result.get("vidid")
            title = (result.get("title") or "").title()
            duration_min = "Live Track"
            n, file_path = await YouTube.video(link)
            if n == 0:
                raise AssistantErr(_["str_3"])
            await handle_stream_entry(
                _, chat_id, original_chat_id, user_name,
                file_path, title, duration_min, user_id,
                source="live", video=video, vidid=vidid, forceplay=forceplay
            )

        elif streamtype == "index":
            link = result
            title = "Index or M3u8 Link"
            duration_min = "URL stream"
            await handle_stream_entry(
                _, chat_id, original_chat_id, user_name,
                link, title, duration_min, user_id,
                source="index", video=video, forceplay=forceplay
            )
            if mystic:
                await mystic.delete()
