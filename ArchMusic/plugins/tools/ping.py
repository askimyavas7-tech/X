from datetime import datetime

from pyrogram import filters
from pyrogram.types import Message

from config import BANNED_USERS, MUSIC_BOT_NAME
from strings import get_command
from ArchMusic import app
from ArchMusic.core.call import ArchMusic
from ArchMusic.utils.decorators.language import language

import psutil  # Sistem istatistikleri için

### Commands
PING_COMMAND = get_command("PING_COMMAND")


# Güvenli sistem istatistik fonksiyonu
async def bot_sys_stats():
    try:
        disk_io = psutil.disk_io_counters()
        if disk_io is None:
            disk_read = 0
            disk_write = 0
        else:
            disk_read = disk_io.read_bytes
            disk_write = disk_io.write_bytes
    except Exception:
        disk_read = disk_write = 0

    try:
        cpu = psutil.cpu_percent()
    except Exception:
        cpu = 0

    try:
        ram = psutil.virtual_memory().percent
    except Exception:
        ram = 0

    # Bot uptime (örnek)
    uptime = "1 gün"

    return uptime, cpu, ram, f"Read:{disk_read} Write:{disk_write}"


@app.on_message(
    filters.command(PING_COMMAND)
    & filters.group
    & ~BANNED_USERS
)
@language
async def ping_com(client, message: Message, _):
    # İlk mesaj: ping hesaplanıyor
    response = await message.reply_text(
        _["ping_1"]
    )

    start = datetime.now()

    # Bot ve Telegram ping değerleri
    pytgping = await ArchMusic.ping()

    # Sistem istatistikleri (güvenli)
    UP, CPU, RAM, DISK = await bot_sys_stats()

    # Geçen süreyi hesapla (ms)
    resp = (datetime.now() - start).microseconds / 1000

    # Mesajı düzenle ve emoji ile göster
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
   
