from pyrogram import filters
from pyrogram.types import Message
from config import BANNED_USERS
from ArchMusic import app

emoji_map = {
    "dice": "🎲",
    "dart": "🎯",
    "ball": "🏀",
    "goal": "⚽",
    "slot": "🎰",
    "bowling": "🎳"
}

@app.on_message(filters.command(list(emoji_map.keys())) & filters.group & ~BANNED_USERS)
async def play_game(client, message: Message):
    command = message.command[0].lower()
    emoji = emoji_map.get(command)

    if emoji:
        await message.reply_dice(emoji=emoji)
    else:
        await message.reply("⚠️ Bilinmeyen oyun komutu.")
