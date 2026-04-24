import os
from dataclasses import dataclass

FOOTER = "\n\n✍️ <i>Author: @vorache777</i>"

# ─── Localisation strings ────────────────────────────────────────────────────

TEXTS = {
    "ru": {
        "choose_lang":    "🌐 Выберите язык / Choose language:",
        "welcome":        (
            "👋 <b>Добро пожаловать в Session Exporter Bot</b>\n\n"
            "Этот бот позволяет экспортировать ваш аккаунт Telegram в:\n"
            "  • <code>.session</code> — файл сессии Telethon\n"
            "  • <code>TData ZIP</code>  — папка tdata для Telegram Desktop\n"
            "  • <code>JSON</code>       — метаданные аккаунта\n\n"
            "<b>Нажмите кнопку ниже чтобы начать.</b>"
        ),
        "btn_login":      "🔐 Войти по номеру телефона",
        "btn_back":       "🏠 Главное меню",
        "btn_cancel":     "❌ Отмена",
        "ask_phone":      "📱 <b>Шаг 1 / 3 — Номер телефона</b>\n\nОтправьте номер в международном формате:\n<code>+79991234567</code>",
        "sending_code":   "⏳ Отправляем код…",
        "code_sent":      "✅ Код отправлен!\n\n📟 <b>Шаг 2 / 3 — Код подтверждения</b>\n\nВведите код из Telegram (только цифры).\nЕсли получили <code>1-2345</code>, отправьте <code>12345</code>.",
        "ask_2fa":        "🔒 <b>Шаг 3 / 3 — Двухфакторная аутентификация</b>\n\nВведите ваш облачный пароль:",
        "checking":       "⏳ Проверяем…",
        "wrong_code":     "❌ <b>Неверный код.</b> Попробуйте ещё раз.\n\n📟 <b>Шаг 2 / 3 — Код подтверждения</b>",
        "code_expired":   "⏰ <b>Код устарел.</b> Введите номер телефона заново.",
        "wrong_pass":     "❌ <b>Неверный пароль.</b> Попробуйте ещё раз.\n\n🔒 <b>Шаг 3 / 3 — Двухфакторная аутентификация</b>",
        "flood":          "🚫 <b>FloodWait:</b> подождите <b>{sec}с</b> и попробуйте снова.",
        "cancelled":      "❌ <b>Авторизация отменена.</b>\n\nНажмите /start чтобы начать заново.",
        "success":        "✅ <b>Авторизация успешна!</b>{me}\n\nВыберите формат для скачивания:",
        "logged_as":      "\n👤 <b>Аккаунт:</b> {name} ({username})\n📱 <b>Телефон:</b> <code>{phone}</code>",
        "building":       "⏳ Генерируем файл…",
        "session_caption":"📄 Файл <code>.session</code> для Telethon",
        "str_caption":    "🔑 Telethon StringSession",
        "tdata_caption":  "🗂 Архив <code>tdata</code> для Telegram Desktop",
        "tdata_howto":    "\n\n<b>Как использовать:</b>\n1. Распакуй архив — получишь папку <code>tdata/</code>\n2. Положи её рядом с <code>Telegram.exe</code>\n3. Запусти Telegram Desktop — сессия подхватится автоматически.",
        "json_caption":   "📋 Метаданные сессии (JSON)",
        "expired":        "⚠️ Сессия истекла. Нажмите /start заново.",
        "phone_fmt":      "⚠️ Укажите код страны, например <code>+79991234567</code>.",
        "btn_session":    "📄 .session файл",
        "btn_str":        "🔑 Session string",
        "btn_tdata":      "🗂 TData ZIP",
        "btn_json":       "📋 JSON",
    },
    "en": {
        "choose_lang":    "🌐 Выберите язык / Choose language:",
        "welcome":        (
            "👋 <b>Welcome to Session Exporter Bot</b>\n\n"
            "This bot exports your Telegram account into:\n"
            "  • <code>.session</code> — Telethon session file\n"
            "  • <code>TData ZIP</code>  — Telegram Desktop tdata folder\n"
            "  • <code>JSON</code>       — Account metadata\n\n"
            "<b>Press the button below to start.</b>"
        ),
        "btn_login":      "🔐 Login with phone number",
        "btn_back":       "🏠 Main menu",
        "btn_cancel":     "❌ Cancel",
        "ask_phone":      "📱 <b>Step 1 / 3 — Phone number</b>\n\nSend your number in international format:\n<code>+12345678901</code>",
        "sending_code":   "⏳ Sending code…",
        "code_sent":      "✅ Code sent!\n\n📟 <b>Step 2 / 3 — Verification code</b>\n\nEnter the code from Telegram (digits only).\nIf you got <code>1-2345</code>, send <code>12345</code>.",
        "ask_2fa":        "🔒 <b>Step 3 / 3 — Two-Factor Authentication</b>\n\nEnter your cloud password:",
        "checking":       "⏳ Checking…",
        "wrong_code":     "❌ <b>Invalid code.</b> Please try again.\n\n📟 <b>Step 2 / 3 — Verification code</b>",
        "code_expired":   "⏰ <b>Code expired.</b> Please send your phone number again.",
        "wrong_pass":     "❌ <b>Wrong password.</b> Please try again.\n\n🔒 <b>Step 3 / 3 — Two-Factor Authentication</b>",
        "flood":          "🚫 <b>FloodWait:</b> please wait <b>{sec}s</b> and try again.",
        "cancelled":      "❌ <b>Authorization cancelled.</b>\n\nPress /start to begin again.",
        "success":        "✅ <b>Successfully authenticated!</b>{me}\n\nChoose the format to download:",
        "logged_as":      "\n👤 <b>Logged in as:</b> {name} ({username})\n📱 <b>Phone:</b> <code>{phone}</code>",
        "building":       "⏳ Building file…",
        "session_caption":"📄 Telethon <code>.session</code> file",
        "str_caption":    "🔑 Telethon StringSession",
        "tdata_caption":  "🗂 Telegram Desktop <code>tdata</code> archive",
        "tdata_howto":    "\n\n<b>How to use:</b>\n1. Extract the ZIP — you get a <code>tdata/</code> folder.\n2. Place it next to your <code>Telegram.exe</code>.\n3. Launch Telegram Desktop — it picks up the session automatically.",
        "json_caption":   "📋 Session metadata (JSON)",
        "expired":        "⚠️ Session expired. Press /start again.",
        "phone_fmt":      "⚠️ Please include the country code, e.g. <code>+12345678901</code>.",
        "btn_session":    "📄 .session file",
        "btn_str":        "🔑 Session string",
        "btn_tdata":      "🗂 TData ZIP",
        "btn_json":       "📋 JSON",
    },
}


def t(lang: str, key: str, **kwargs) -> str:
    """Get translated string for lang (fallback to en)."""
    text = TEXTS.get(lang, TEXTS["en"]).get(key, TEXTS["en"].get(key, key))
    return text.format(**kwargs) if kwargs else text


@dataclass
class Config:
    bot_token: str
    api_id: int
    api_hash: str
    device_model: str = "Samsung Galaxy S23"
    system_version: str = "Android 13"
    app_version: str = "10.3.2"
    lang_code: str = "en"
    system_lang_code: str = "en-US"


def load_config() -> Config:
    return Config(
        bot_token=os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN"),
        api_id=int(os.getenv("API_ID", "2040")),
        api_hash=os.getenv("API_HASH", "b18441a1ff607e10a989891a5462e627"),
    )
