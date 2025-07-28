# group_events.py

from pyrogram import Client, filters
from pyrogram.types import Message, ChatMemberUpdated, InlineKeyboardMarkup, InlineKeyboardButton
from config import LOG_GROUP_ID
from ArchMusic import app


async def new_message(chat_id: int, message: str, reply_markup=None):
    await app.send_message(chat_id=chat_id, text=message, reply_markup=reply_markup)


# 1. Bot gruba eklendi
@app.on_message(filters.new_chat_members)
async def on_new_member(client: Client, message: Message):
    bot_id = (await client.get_me()).id
    for user in message.new_chat_members:
        added_by = message.from_user.first_name if message.from_user else "Bilinmiyor"
        chat_id = message.chat.id
        title = message.chat.title
        chat_link = f"@{message.chat.username}" if message.chat.username else "Yok"

        if user.id == bot_id:
            # Bot eklendi
            text = (
                f"<u>#**Bot Gruba Eklendi**</u>\n\n"
                f"**Grup Adı:** {title}\n"
                f"**Grup ID:** `{chat_id}`\n"
                f"**Grup Linki:** {chat_link}\n"
                f"**Ekleyen:** {added_by}"
            )
        else:
            # Normal kullanıcı eklendi
            text = (
                f"<u>#**Kullanıcı Eklendi**</u>\n\n"
                f"**Adı:** {user.mention}\n"
                f"**ID:** `{user.id}`\n"
                f"**Grup:** {title}\n"
                f"**Ekleyen:** {added_by}"
            )

        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(added_by, user_id=message.from_user.id)]] if message.from_user else []
        )

        await new_message(LOG_GROUP_ID, text, reply_markup)


# 2. Bot veya kullanıcı gruptan çıkarıldı
@app.on_message(filters.left_chat_member)
async def on_left_member(client: Client, message: Message):
    bot_id = (await client.get_me()).id
    user = message.left_chat_member
    remover = message.from_user.first_name if message.from_user else "Bilinmiyor"
    title = message.chat.title
    chat_id = message.chat.id

    if user.id == bot_id:
        text = (
            f"<u>#**Bot Gruptan Atıldı**</u>\n\n"
            f"**Grup Adı:** {title}\n"
            f"**Grup ID:** `{chat_id}`\n"
            f"**Atan Kişi:** {remover}"
        )
    else:
        text = (
            f"<u>#**Kullanıcı Çıkarıldı**</u>\n\n"
            f"**Adı:** {user.mention}\n"
            f"**ID:** `{user.id}`\n"
            f"**Grup:** {title}\n"
            f"**Çıkaran:** {remover}"
        )

    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton(remover, user_id=message.from_user.id)]] if message.from_user else []
    )

    await new_message(LOG_GROUP_ID, text, reply_markup)


# 3. Ban / Unban / Leave gibi değişiklikleri algıla
@app.on_chat_member_updated()
async def on_chat_member_update(client: Client, update: ChatMemberUpdated):
    old_status = update.old_chat_member.status
    new_status = update.new_chat_member.status
    user = update.new_chat_member.user
    chat = update.chat
    actor = update.from_user.first_name if update.from_user else "Bilinmiyor"
    actor_id = update.from_user.id if update.from_user else None

    if user.is_self:
        # Bot ile ilgili işlem
        if new_status == "kicked":
            action = "Bot gruptan banlandı"
        elif old_status == "kicked" and new_status == "member":
            action = "Bot gruba geri alındı"
        else:
            return
    else:
        # Kullanıcı işlemi
        if new_status == "kicked":
            action = f"{user.mention} gruptan **banlandı**"
        elif old_status == "kicked" and new_status == "member":
            action = f"{user.mention} gruba **geri alındı (ban kaldırıldı)**"
        else:
            return

    text = (
        f"<u>#**Grup Üyelik Güncellemesi**</u>\n\n"
        f"**Grup:** {chat.title}\n"
        f"**Kullanıcı:** {user.mention} (`{user.id}`)\n"
        f"**İşlem:** {action}\n"
        f"**İşlemi Yapan:** {actor}"
    )

    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton(actor, user_id=actor_id)]] if actor_id else []
    )

    await new_message(LOG_GROUP_ID, text, reply_markup)
