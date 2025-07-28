import random
import asyncio
from pyrogram import filters
from pyrogram.types import Message
from config import BANNED_USERS
from ArchMusic import app
from pyrogram.enums import ChatMemberStatus

# ✅ Pyrogram client (örneğin: app.bot, app.client olabilir)
real_client = app.bot  # eğer hata alırsan bunu 'app' olarak değiştir

# ✅ Kullanıcının iptal talebini takip etmek için
cancel_users = {}

# ✅ Söz listesi
SOZLER = [
    "Hayal gücü bilgiden daha önemlidir. – Einstein",
    "İmkansız, sadece tembellerin bahanesidir.",
    "Yavaş git ama asla durma.",
    "Her şey seninle başlar.",
    "İnsan en çok kendiyle savaşıyor.",
    "İyi şeyler zaman alır.",
    "Mutluluk bir varış noktası değil, yolculuktur.",
    "Gerçek özgürlük kendin olabilmektir.",
    "Fark yaratmak cesaret ister.",
    "Bugün yapmadığın şey, yarın pişmanlığın olabilir.",
]

# ✅ /cancel komutu
@app.on_message(filters.command("cancel") & filters.group & ~BANNED_USERS)
async def cancel_soz(client, message: Message):
    cancel_users[message.from_user.id] = True
    await message.reply("❌ Etiketleme işlemi iptal edildi.")

# ✅ /soz komutu
@app.on_message(filters.command("soz") & filters.group & ~BANNED_USERS)
async def soz_gonder(client, message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    cancel_users[user_id] = False

    await message.reply("📨 Üyeler etiketleniyor. Durdurmak için /cancel yaz.")

    etiketlenen = 0
    atilamayan = 0

    try:
        async for member in real_client.iter_chat_members(chat_id):
            if cancel_users.get(user_id):
                await message.reply("🛑 Etiketleme işlemi iptal edildi.")
                return

            if member.user.is_bot:
                continue

            # Söz seç
            soz = random.choice(SOZLER)

            try:
                await message.reply(
                    f"👤 [{member.user.first_name}](tg://user?id={member.user.id})\n\n📝 _{soz}_",
                    quote=False
                )
                etiketlenen += 1
            except Exception:
                atilamayan += 1

            await asyncio.sleep(1.5)

    except Exception as e:
        return await message.reply(f"⚠️ Üye listesi alınamadı:\n`{e}`")

    await message.reply(
        f"✅ **Etiketleme Tamamlandı**\n"
        f"👥 Etiketlenen: {etiketlenen}\n"
        f"❌ Atılamayan: {atilamayan}\n"
        f"🎯 Toplam: {etiketlenen + atilamayan}"
    )
