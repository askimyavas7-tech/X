from datetime import datetime

from pyrogram import filters
from pyrogram.types import Message

from config import BANNED_USERS, MUSIC_BOT_NAME
from strings import get_command
from ArchMusic import app
from ArchMusic.core.call import ArchMusic
from ArchMusic.utils import bot_sys_stats
from ArchMusic.utils.decorators.language import language

### Commands
PING_COMMAND = get_command("PING_COMMAND")


@app.on_message(
    filters.command(PING_COMMAND)
    & filters.group
    & ~BANNED_USERS
)
@language
async def ping_com(client, message: Message, _):
    # İlk mesaj, ping hesaplanıyor bilgisi
    response = await message.reply_text(
        _["ping_1"]
    )

    start = datetime.now()
    
    # Bot ve Telegram ping değerleri
    pytgping = await ArchMusic.ping()
    
    # Sistem istatistikleri
    UP, CPU, RAM, DISK = await bot_sys_stats()
    
    # Geçen süreyi hesapla (ms)
    resp = (datetime.now() - start).microseconds / 1000

    # Mesajı düzenle ve ekstra emoji ile bilgileri göster
    await response.edit_text(
        _["ping_2"].format(
            MUSIC_BOT_NAME,
            resp,
            UP,
            DISK,
            CPU,
            RAM,
            pytgping
        ) + "\n\n⚡ Hızlı Ping | 📊 Sistem Durumu ✅"
    )
    
