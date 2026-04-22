from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔐 Login with phone", callback_data="start_auth")],
    ])


def download_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📄 .session file",  callback_data="dl_session"),
            InlineKeyboardButton(text="🔑 Session string", callback_data="dl_session_str"),
        ],
        [
            InlineKeyboardButton(text="🗂 TData ZIP",       callback_data="dl_tdata"),
            InlineKeyboardButton(text="📋 JSON metadata",   callback_data="dl_json"),
        ],
        [InlineKeyboardButton(text="🏠 Back to menu",      callback_data="back_menu")],
    ])


def cancel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_auth")],
    ])
