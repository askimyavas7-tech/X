import asyncio
import random
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait

from config import BANNED_USERS
from ArchMusic import app

etag_sessions = {}

EMOJIS = [
    "😂", "🤣", "😍", "🤩", "😎", "🥶", "🤑", "👑", "🤖", "🐸", "👻", "🐼", "🐶",
    "🐱", "🐯", "🐷", "🦄", "🐵", "🦁", "🐣", "🦋", "🍕", "🍔", "🍟", "🌮",
    "⚽", "🏀", "🏓", "🎮", "🎲", "🎧", "🎤", "📸", "📱", "💻", "🚀", "✈️",
]

@app.on_message(filters.command("etag") & filters.group & ~BANNED_USERS)
async def etag_command(client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    args = message.text.split(maxsplit=1)
    custom_msg = args[1] if len(args) > 1 else "Selam millet! 👋"

    members = []
    async for member in client.get_chat_members(chat_id):
        if member.user.is_bot:
            continue
        members.append(member.user)

    if not members:
        return await message.reply_text("Etiketlenecek kullanıcı bulunamadı.")

    etag_sessions[chat_id] = {
        "active": True,
        "last": None,
        "members": members,
        "msg": custom_msg,
        "from": user_id,
    }

    await message.reply(
        f"🎉 **Emojili Etiketleme Başlatılsın mı?**\n\n"
        f"👤 Başlatan: [{message.from_user.first_name}](tg://user?id={user_id})\n"
        f"📦 Kişi sayısı: {len(members)}\n"
        f"💬 Mesaj: {custom_msg}",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Başla", callback_data=f"start_etag:{user_id}"),
                InlineKeyboardButton("🛑 İptal", callback_data=f"cancel_etag:{user_id}")
            ]
        ])
    )


@app.on_callback_query(filters.regex(r"start_etag:(\d+)"))
async def start_etag(client, cq: CallbackQuery):
    uid = int(cq.matches[0].group(1))
    chat_id = cq.message.chat.id

    if cq.from_user.id != uid:
        return await cq.answer("Bu işlem sadece başlatan kişiye ait.", show_alert=True)

    session = etag_sessions.get(chat_id)
    if not session:
        return await cq.answer("Etiket oturumu bulunamadı.", show_alert=True)

    await cq.message.edit_text("🚀 Emojili etiketleme başlatıldı. Durdurmak için: `/cancel_etag`")

    tagged, failed = 0, 0
    delay = 1.3
    chunk = 5
    members = session["members"]
    chunks = [members[i:i + chunk] for i in range(0, len(members), chunk)]

    for group in chunks:
        if not etag_sessions.get(chat_id, {}).get("active"):
            break
        try:
            tags = "\n".join(
                f"{random.choice(EMOJIS)} [{u.first_name}](tg://user?id={u.id})"
                for u in group
            )
            await cq.message.reply(f"{tags}\n\n{session['msg']}")
            await asyncio.sleep(delay)
            session["last"] = group[-1]
            tagged += len(group)
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except:
            failed += len(group)

    last_user = session.get("last")
    name = f"[{last_user.first_name}](tg://user?id={last_user.id})" if last_user else "Yok"
    etag_sessions.pop(chat_id, None)

    await cq.message.reply(
        f"✅ Emojili etiketleme tamamlandı.\n"
        f"📌 Etiketlenen: {tagged}\n"
        f"❌ Başarısız: {failed}\n"
        f"🔚 Son etiketlenen: {name}"
    )


@app.on_callback_query(filters.regex(r"cancel_etag:(\d+)"))
async def cancel_etag(client, cq: CallbackQuery):
    uid = int(cq.matches[0].group(1))
    if cq.from_user.id != uid:
        return await cq.answer("Sadece başlatan iptal edebilir.", show_alert=True)

    chat_id = cq.message.chat.id
    etag_sessions.pop(chat_id, None)
    await cq.message.edit_text("🛑 Emojili etiketleme iptal edildi.")


@app.on_message(filters.command("cancel_etag") & filters.group & ~BANNED_USERS)
async def cancel_etag_cmd(client, message: Message):
    chat_id = message.chat.id
    session = etag_sessions.get(chat_id)

    if not session:
        return await message.reply_text("🔍 Aktif bir etiketleme oturumu yok.")

    if message.from_user.id != session["from"]:
        return await message.reply_text("⛔ Sadece başlatan kullanıcı durdurabilir.")

    etag_sessions[chat_id]["active"] = False
    last_user = session.get("last")
    name = f"[{last_user.first_name}](tg://user?id={last_user.id})" if last_user else "Yok"
    await message.reply(
        f"🛑 Etiketleme durduruldu.\n"
        f"🔚 Son etiketlenen: {name}"
    )
