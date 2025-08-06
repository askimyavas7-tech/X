# app/ArchMusic/utils/inline/start.py

from typing import Union, Optional, List
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from config import GITHUB_REPO, SUPPORT_CHANNEL, SUPPORT_GROUP
from ArchMusic import app


def _support_row(_: dict) -> Optional[List[InlineKeyboardButton]]:
    """
    Destek butonlarını tek bir satır halinde döndürür (ya 0, ya 1, ya 2 buton).
    Hiç buton yoksa None döner.
    """
    row: List[InlineKeyboardButton] = []
    if SUPPORT_GROUP:
        row.append(InlineKeyboardButton(text=f"🟩 {_['S_B_3']}", url=SUPPORT_GROUP))
    if SUPPORT_CHANNEL:
        row.append(InlineKeyboardButton(text=f"🟦 {_['S_B_4']}", url=SUPPORT_CHANNEL))
    return row if row else None


def start_panel(_: dict) -> InlineKeyboardMarkup:
    """
    Başlangıç paneli — start mesajı için kullanılabilir.
    Döndürülen değer doğrudan reply_markup parametresine verilebilir.
    """
    buttons: List[List[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(text=f"🟦 {_['S_B_1']}", url=f"https://t.me/{app.username}?start=help"),
            InlineKeyboardButton(text=f"🟨 {_['S_B_2']}", callback_data="settings_helper"),
        ]
    ]

    support = _support_row(_)
    if support:
        buttons.append(support)

    return InlineKeyboardMarkup(buttons)


def private_panel(
    _: dict,
    BOT_USERNAME: str,
    OWNER: Union[bool, int] = None,
    header_text: Optional[str] = "📌 Menuden istediğin işlemi seç"
) -> InlineKeyboardMarkup:
    """
    Özel (private) panel:
      - header_text: Eğer None verilirse klavyede başlık olmaz. Aksi halde tıklanabilir bir başlık butonu ekler (callback_data='header').
      - OWNER: kullanıcının user_id'si ya da False/None
    Döndürdüğü InlineKeyboardMarkup doğrudan reply_markup olarak kullanılır.
    """
    buttons: List[List[InlineKeyboardButton]] = []

    # Opsiyonel başlık (klavyede tıklanabilir buton olarak)
    if header_text:
        buttons.append([InlineKeyboardButton(text=header_text, callback_data="header")])

    # Geri butonu (tek ortalı satır)
    buttons.append([InlineKeyboardButton(text=f"🔙 {_['S_B_8']}", callback_data="settings_back_helper")])

    # Destek satırı (varsa)
    support = _support_row(_)
    if support:
        buttons.append(support)

    # Grup ekleme (tek ortalı satır)
    buttons.append([
        InlineKeyboardButton(
            text=f"🟢 {_['S_B_5']}",
            url=f"https://t.me/{BOT_USERNAME}?startgroup=true"
        )
    ])

    # GitHub & Owner satırı (iki sütun olacak şekilde)
    final_row: List[InlineKeyboardButton] = []
    if GITHUB_REPO:
        final_row.append(InlineKeyboardButton(text=f"🟣 {_['S_B_6']}", url=GITHUB_REPO))
    if OWNER:
        final_row.append(InlineKeyboardButton(text=f"🔴 {_['S_B_7']}", user_id=OWNER))
    if final_row:
        buttons.append(final_row)

    return InlineKeyboardMarkup(buttons)


# --- Kullanım örnekleri ---
# reply_markup = start_panel(your_locale_dict)
# reply_markup = private_panel(your_locale_dict, BOT_USERNAME="YourBot", OWNER=123456789)
#
# Öneri: Eğer başlığı tıklanmaz (pasif) görmek istersen header_text=None verip
# mesaj metnine başlık yaz:
# await app.send_message(chat_id, "📌 Menuden istediğin işlemi seç", reply_markup=private_panel(..., header_text=None))
