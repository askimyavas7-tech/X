from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import LOG_GROUP_ID
from ArchMusic import app

# Yardımcı: log mesajını oluşturur
async def create_log_message(event_type: str, chat, user):
    emoji = "✅" if event_type == "joined" else "🚫"
    title = "**Bot Gruba Eklendi**" if event_type == "joined" else "**Bot Gruptan Çıkarıldı**"
    action_by = user.mention if user else "Bilinmeyen"
    members_count = await app.get_chat_members_count(chat.id)

    message = (
        f"{emoji} {title}\n\n"
        f"📌 **Grup:** `{chat.title}`\n"
        f"🆔 **Grup ID:** `{chat.id}`\n"
        f"👥 **Üye Sayısı:** `{members_count}`\n"
        f"👤 **İşlemi Yapan:** {action_by}\n"
    )

    if chat.username:
        message += f"🔗 [@{chat.username}](https://t.me/{chat.username})"

    return message

# Bot gruba eklendiğinde
@app.on_message(filters.new_chat_members)
async def bot_added_handler(client: Client, message: Message):
    for member in message.new_chat_members:
        if member.id == (await app.get_me()).id:
            log_text = await create_log_message("joined", message.chat, message.from_user)
            chat_id = message.chat.id

            # Grup linki oluştur
            if message.chat.username:
                url = f"https://t.me/{message.chat.username}"
            else:
                url = f"https://t.me/c/{str(chat_id)[4:]}/1"

            buttons = InlineKeyboardMarkup([
                [InlineKeyboardButton("📂 Gruba Git", url=url)]
            ])

            await app.send_message(LOG_GROUP_ID, log_text, reply_markup=buttons)
            break

# Bot gruptan çıkarıldığında
@app.on_message(filters.left_chat_member)
async def bot_removed_handler(client: Client, message: Message):
    if message.left_chat_member.id == (await app.get_me()).id:
        log_text = await create_log_message("left", message.chat, message.from_user)
        chat_id = message.chat.id

        if message.chat.username:
            url = f"https://t.me/{message.chat.username}"
        else:
            url = f"https://t.me/c/{str(chat_id)[4:]}/1"

        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📁 Grup Bilgisi", url=url)]
        ])

        await app.send_message(LOG_GROUP_ID, log_text, reply_markup=buttons)
