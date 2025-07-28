import random
import asyncio
from collections import defaultdict
from pyrogram import filters
from pyrogram.types import Message
from config import BANNED_USERS
from ArchMusic import app

# Her kullanıcıya özel iptal listesi
cancel_users = defaultdict(set)

# 50 Güzel söz
SOZ_LISTESI = [
    "Sen gülümsedikçe dünya güzelleşiyor 🌸",
    "Senin varlığın bu gruba renk katıyor 🎨",
    "İyi ki varsın, her şey seninle daha anlamlı 🌟",
    "Pozitif enerjin burayı aydınlatıyor ☀️",
    "Senin gibi biriyle aynı grupta olmak harika! 💖",
    "Gülüşün bile mesaj gibi ✨",
    "Senin gibi insanlar sayesinde burası özel 😊",
    "Sen özelsin, unutma 💫",
    "Dünyaya neşe saçıyorsun 🎉",
    "Sen bu grubun neşesisin 🎈",
    "Kalbinle güzelsin ❤️",
    "Senin enerjin bulaşıcı ⚡",
    "Sen umut gibisin 🌈",
    "Işığın karanlıkta parlıyor 🔥",
    "Sen bu sohbetin kalbisin 💌",
    "Seninle burası bir başka güzel 🏞️",
    "Senin gülüşün moral kaynağı 😊",
    "Senin dostluğun paha biçilemez 💎",
    "Sen varsan burada sıcaklık var 🔆",
    "Seninle konuşmak terapi gibi 🧘",
    "Senin adın huzurla anılıyor ☁️",
    "Senin bakışlarında sevgi var 🥰",
    "Seninle olmak en güzel anı 📸",
    "Senin söylediklerin ilham verici 🧠",
    "Sen bu grubun yıldızısın 🌟",
    "Seninle zaman akıp gidiyor ⏳",
    "Senin gülüşün dertleri unutturur 😄",
    "Senin kalbin sevgiyle dolu 💓",
    "Sen anlatılmaz, yaşanırsın 💬",
    "Sen özel değil, eşsizsin 🔮",
    "Seninle dünya daha güzel 🌍",
    "Senin güzelliğin içinden geliyor ✨",
    "Senin varlığın bir armağan 🎁",
    "Senin yanında olmak huzur veriyor 🕊️",
    "Sen iyi ki varsın dediklerimdensin 🙏",
    "Senin enerjin içimizi ısıtıyor 🔥",
    "Sen bu sohbetin ruhusun 👼",
    "Seninle her şey daha kolay 💪",
    "Senin sözlerin kalbimize dokunuyor 🎵",
    "Seninle yol almak ayrı bir güzellik 🚶‍♀️",
    "Sen gelsen, çiçekler açar 🌺",
    "Senin tebessümün güneş gibi ☀️",
    "Senin sevgine doyamıyoruz 💖",
    "Sen burada olduğun için bu grup özel ✨",
    "Senin düşüncelerin kıymetli 🧠",
    "Senin desteğin hep hissediliyor 🫶",
    "Senin gibi biriyle sohbet etmek ayrıcalık 🎙️",
    "Senin samimiyetin içimizi ısıtıyor 🔥",
    "Seninle olmak bir şans 🍀",
    "Sen kelimelere sığmazsın 📝"
]

# /cancel komutu
@app.on_message(filters.command("cancel") & filters.group & ~BANNED_USERS)
async def cancel_ptag(client, message: Message):
    cancel_users[message.chat.id].add(message.from_user.id)
    await message.reply("❌ Etiketleme işlemi iptal edildi.")

# /ptag komutu
@app.on_message(filters.command("ptag") & filters.group & ~BANNED_USERS)
async def ptag_command(client, message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    if user_id in cancel_users[chat_id]:
        cancel_users[chat_id].remove(user_id)
        return await message.reply("⛔ İşlem zaten iptal edilmişti.")

    await message.reply("📢 Etiketlemeye başlıyorum... /cancel yazarsan durur.")

    etiketlenen = 0
    atilamayan = 0

    try:
        async for member in app.get_chat_members(chat_id):
            if member.user.is_bot:
                continue

            if user_id in cancel_users[chat_id]:
                cancel_users[chat_id].remove(user_id)
                return await message.reply("🛑 İşlem iptal edildi.")

            soz = random.choice(SOZ_LISTESI)
            try:
                await message.reply(
                    f"👤 [{member.user.first_name}](tg://user?id={member.user.id})\n\n📝 _{soz}_",
                    quote=False
                )
                etiketlenen += 1
            except:
                atilamayan += 1

            await asyncio.sleep(1.5)  # spam koruması

    except Exception as e:
        return await message.reply(f"⚠️ Üye listesi alınamadı:\n`{e}`")

    await message.reply(
        f"✅ **Etiketleme Tamamlandı**\n"
        f"👥 Etiketlenen: {etiketlenen}\n"
        f"❌ Atılamayan: {atilamayan}\n"
        f"📊 Toplam: {etiketlenen + atilamayan}"
    )
