from pyrogram import Client, filters
from pyrogram.types import Message, ChatMemberUpdated, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatMemberStatus
from config import LOG_GROUP_ID
from ArchMusic import app  # Veya senin bot uygulamanın adı neyse

# ✅ Log fonksiyonu
async def send_log(text: str, reply_markup=None):
    try:
        await app.send_message(chat_id=LOG_GROUP_ID, text=text, reply_markup=reply_markup)
    except Exception as e:
        print(f"[HATA] Log mesajı gönderilemedi:\n{e}\nMesaj: {text}")

# ✅ Yeni kullanıcı veya bot eklendiğinde
@app.on_message(filters.new_chat_members)
async def on_new_member(client, message: Message):
    bot_id = (await client.get_me()).id
    chat = message.chat
    chat_link = f"@{chat.username}" if chat.username else "Yok"
    ad = message.from_user.first_name if message.from_user else "Bilinmiyor"

    for user in message.new_chat_members:
        if user.id == bot_id:
            text = (
                f"<u>#✅ **Bot Gruba Eklendi**</u>\n\n"
                f"**Grup:** {chat.title}\n"
                f"**ID:** `{chat.id}`\n"
                f"**Link:** {chat_link}\n"
                f"**Ekleyen:** {ad}"
            )
        else:
            text = (
                f"<u>#👤 **Kullanıcı Eklendi**</u>\n\n"
                f"**Adı:** {user.mention}\n"
                f"**ID:** `{user.id}`\n"
                f"**Grup:** {chat.title}\n"
                f"**Link:** {chat_link}\n"
                f"**Ekleyen:** {ad}"
            )

        markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(ad, user_id=message.from_user.id)]] if message.from_user else []
        )

        await send_log(text, markup)

# ✅ Bot veya kullanıcı gruptan çıkarıldığında
@app.on_message(filters.left_chat_member)
async def on_left_member(client, message: Message):
    bot_id = (await client.get_me()).id
    user = message.left_chat_member
    chat = message.chat
    ad = message.from_user.first_name if message.from_user else "Bilinmiyor"
    chat_link = f"@{chat.username}" if chat.username else "Yok"

    if user.id == bot_id:
        text = (
            f"<u>#🚫 **Bot Gruptan Atıldı**</u>\n\n"
            f"**Grup:** {chat.title}\n"
            f"**ID:** `{chat.id}`\n"
            f"**Link:** {chat_link}\n"
            f"**Atan:** {ad}"
        )
    else:
        text = (
            f"<u>#🚷 **Kullanıcı Çıkarıldı**</u>\n\n"
            f"**Adı:** {user.mention}\n"
            f"**ID:** `{user.id}`\n"
            f"**Grup:** {chat.title}\n"
            f"**Link:** {chat_link}\n"
            f"**Çıkaran:** {ad}"
        )

    markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton(ad, user_id=message.from_user.id)]] if message.from_user else []
    )

    await send_log(text, markup)

# ✅ Yönetici işlemleri, ban, üyelik değişiklikleri
@app.on_chat_member_updated()
async def on_chat_member_update(client: Client, update: ChatMemberUpdated):
    old = update.old_chat_member
    new = update.new_chat_member
    user = new.user
    chat = update.chat
    executor = update.from_user
    grup_link = f"@{chat.username}" if chat.username else "Yok"
    yapan = executor.first_name if executor else "Bilinmiyor"

    if old.status != new.status:
        if new.status == ChatMemberStatus.ADMINISTRATOR:
            text = (
                f"<u>#🛡️ **Yönetici Yapıldı**</u>\n\n"
                f"**Kullanıcı:** {user.mention}\n"
                f"**ID:** `{user.id}`\n"
                f"**Grup:** {chat.title}\n"
                f"**ID:** `{chat.id}`\n"
                f"**Link:** {grup_link}\n"
                f"**Yapan:** {yapan}"
            )
        elif old.status == ChatMemberStatus.ADMINISTRATOR and new.status == ChatMemberStatus.MEMBER:
            text = (
                f"<u>#⚠️ **Yönetici Alındı**</u>\n\n"
                f"**Kullanıcı:** {user.mention}\n"
                f"**ID:** `{user.id}`\n"
                f"**Grup:** {chat.title}\n"
                f"**ID:** `{chat.id}`\n"
                f"**Link:** {grup_link}\n"
                f"**Yapan:** {yapan}"
            )
        elif new.status == ChatMemberStatus.BANNED:
            text = (
                f"<u>#⛔️ **Kullanıcı Banlandı**</u>\n\n"
                f"**Kullanıcı:** {user.mention}\n"
                f"**ID:** `{user.id}`\n"
                f"**Grup:** {chat.title}\n"
                f"**ID:** `{chat.id}`\n"
                f"**Link:** {grup_link}\n"
                f"**Yapan:** {yapan}"
            )
        elif old.status == ChatMemberStatus.BANNED and new.status == ChatMemberStatus.MEMBER:
            text = (
                f"<u>#🔓 **Ban Kaldırıldı**</u>\n\n"
                f"**Kullanıcı:** {user.mention}\n"
                f"**ID:** `{user.id}`\n"
                f"**Grup:** {chat.title}\n"
                f"**ID:** `{chat.id}`\n"
                f"**Link:** {grup_link}\n"
                f"**Yapan:** {yapan}"
            )
        elif new.status == ChatMemberStatus.LEFT:
            text = (
                f"<u>#🚷 **Kullanıcı Ayrıldı veya Atıldı**</u>\n\n"
                f"**Kullanıcı:** {user.mention}\n"
                f"**ID:** `{user.id}`\n"
                f"**Grup:** {chat.title}\n"
                f"**ID:** `{chat.id}`\n"
                f"**Link:** {grup_link}\n"
                f"**Yapan:** {yapan}"
            )
        else:
            return

        markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(yapan, user_id=executor.id)]] if executor else []
        )

        await send_log(text, markup)
