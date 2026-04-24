from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import t


def lang_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
        ]
    ])


def main_menu_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "btn_login"), callback_data="start_auth")],
    ])


def download_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t(lang, "btn_session"), callback_data="dl_session"),
            InlineKeyboardButton(text=t(lang, "btn_str"),     callback_data="dl_session_str"),
        ],
        [
            InlineKeyboardButton(text=t(lang, "btn_tdata"),   callback_data="dl_tdata"),
            InlineKeyboardButton(text=t(lang, "btn_json"),    callback_data="dl_json"),
        ],
        [InlineKeyboardButton(text=t(lang, "btn_back"),       callback_data="back_menu")],
    ])


def cancel_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "btn_cancel"), callback_data="cancel_auth")],
    ])
