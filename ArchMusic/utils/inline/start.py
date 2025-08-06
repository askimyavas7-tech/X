from pyrogram import Client, filters
from pyrogram.types import Message

# Doğru importlar (start_panel ile)
from ArchMusic.utils.inline import (
    help_pannel,
    private_panel,
    start_panel
)

BOT_USERNAME = "YourBotUsername"  # Bot kullanıcı adını buraya yaz

@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    # Örnek dil sözlüğü (gerçek projede burayı kendi i18n yapınıza göre değiştirin)
    _ = {
        "S_B_1": "Yardım",
        "S_B_2": "Ayarlar",
        "S_B_3": "Destek Grubu",
        "S_B_4": "Destek Kanalı",
        "S_B_5": "Gruba Ekle",
        "S_B_6": "GitHub",
        "S_B_7": "Sahip",
        "S_B_8": "Geri"
    }

    buttons = start_panel(_)

    await message.reply_text(
        "Hoşgeldin! Yardım almak için aşağıdaki butonları kullanabilirsin.",
        reply_markup=buttons
    )
