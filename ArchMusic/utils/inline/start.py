# panel_buttons.py

from typing import Union
from pyrogram.types import InlineKeyboardButton
from config import GITHUB_REPO, SUPPORT_CHANNEL, SUPPORT_GROUP
from ArchMusic import app


def start_pannel(_):
    buttons = [
        [
            InlineKeyboardButton(text=_["S_B_1"], url=f"https://t.me/{app.username}?start=help"),
            InlineKeyboardButton(text=_["S_B_2"], callback_data="settings_helper"),
        ]
    ]

    support_buttons = _get_support_buttons(_)
    if support_buttons:
        buttons.append(support_buttons)

    return buttons


def private_panel(_, BOT_USERNAME, OWNER: Union[bool, int] = None):
    buttons = [
        [InlineKeyboardButton(text=_["S_B_8"], callback_data="settings_back_helper")]
    ]

    support_buttons = _get_support_buttons(_)
    if support_buttons:
        buttons.append(support_buttons)

    buttons.append([
        InlineKeyboardButton(
            text=_["S_B_5"],
            url=f"https://t.me/{BOT_USERNAME}?startgroup=true"
        )
    ])

    # Ek seçenekler: GitHub ve OWNER
    final_row = []
    if GITHUB_REPO:
        final_row.append(
            InlineKeyboardButton(text=_["S_B_6"], url="https://github.com/ArchBots/ArchMusic")
        )
    if OWNER:
        final_row.append(
            InlineKeyboardButton(text=_["S_B_7"], user_id=OWNER)
        )
    if final_row:
        buttons.append(final_row)

    return buttons


def _get_support_buttons(_):
    """Yardım ve destek butonlarını oluşturur."""
    buttons = []
    if SUPPORT_CHANNEL:
        buttons.append(InlineKeyboardButton(text=_["S_B_4"], url=SUPPORT_CHANNEL))
    if SUPPORT_GROUP:
        buttons.append(InlineKeyboardButton(text=_["S_B_3"], url=SUPPORT_GROUP))
    return buttons if buttons else None
 
