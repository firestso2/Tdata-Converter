import asyncio
import logging

from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from telethon.errors import (
    FloodWaitError,
    PhoneCodeInvalidError,
    PhoneCodeExpiredError,
    SessionPasswordNeededError,
    PasswordHashInvalidError,
)

from config import load_config, FOOTER
from keyboards import cancel_kb, download_kb, main_menu_kb
from states.auth import AuthStates
from utils.client_manager import (
    get_or_create_client,
    store_user_data,
    get_user_data,
    disconnect_client,
)

logger = logging.getLogger(__name__)
router = Router()
config = load_config()


# ──────────────────────────── helpers ───────────────────────────────────────

def _fmt(text: str) -> str:
    return text + FOOTER


# ──────────────────────────── entry point ───────────────────────────────────

@router.callback_query(lambda c: c.data == "start_auth")
async def cb_start_auth(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AuthStates.waiting_phone)
    await callback.message.edit_text(
        _fmt(
            "📱 <b>Step 1 / 3 — Phone number</b>\n\n"
            "Send your phone number in international format:\n"
            "<code>+1234567890</code>"
        ),
        reply_markup=cancel_kb(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "cancel_auth")
async def cb_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await disconnect_client(callback.from_user.id)
    await callback.message.edit_text(
        _fmt("❌ <b>Authorization cancelled.</b>\n\nPress /start to begin again."),
        reply_markup=main_menu_kb(),
        parse_mode="HTML",
    )
    await callback.answer()


# ──────────────────────────── phone ─────────────────────────────────────────

@router.message(AuthStates.waiting_phone)
async def handle_phone(message: Message, state: FSMContext) -> None:
    phone = message.text.strip()
    if not phone.startswith("+"):
        await message.answer(
            _fmt("⚠️ Please include the country code, e.g. <code>+1234567890</code>."),
            parse_mode="HTML",
        )
        return

    status_msg = await message.answer(
        _fmt("⏳ Sending login code…"),
        parse_mode="HTML",
    )

    try:
        client = await get_or_create_client(
            message.from_user.id,
            config.api_id, config.api_hash,
            config.device_model, config.system_version,
            config.app_version, config.lang_code,
            config.system_lang_code,
        )
        result = await client.send_code_request(phone)
        store_user_data(message.from_user.id, "phone", phone)
        store_user_data(message.from_user.id, "phone_code_hash", result.phone_code_hash)
        await state.set_state(AuthStates.waiting_code)

        await status_msg.edit_text(
            _fmt(
                "✅ Code sent!\n\n"
                "📟 <b>Step 2 / 3 — Verification code</b>\n\n"
                "Enter the code Telegram sent you (digits only).\n"
                "If you received <code>1-2345</code>, send <code>12345</code>."
            ),
            reply_markup=cancel_kb(),
            parse_mode="HTML",
        )

    except FloodWaitError as e:
        await state.clear()
        await disconnect_client(message.from_user.id)
        await status_msg.edit_text(
            _fmt(
                f"🚫 <b>FloodWait</b>: Telegram requires a cooldown of "
                f"<b>{e.seconds}s</b>.\n\nPlease try again later."
            ),
            reply_markup=main_menu_kb(),
            parse_mode="HTML",
        )
    except Exception as exc:
        logger.exception("send_code_request failed: %s", exc)
        await state.clear()
        await disconnect_client(message.from_user.id)
        await status_msg.edit_text(
            _fmt(f"❌ Error: <code>{exc}</code>\n\nPlease try again via /start."),
            reply_markup=main_menu_kb(),
            parse_mode="HTML",
        )


# ──────────────────────────── code ──────────────────────────────────────────

@router.message(AuthStates.waiting_code)
async def handle_code(message: Message, state: FSMContext) -> None:
    code = message.text.strip().replace("-", "").replace(" ", "")
    phone = get_user_data(message.from_user.id, "phone")
    phone_code_hash = get_user_data(message.from_user.id, "phone_code_hash")

    status_msg = await message.answer(
        _fmt("⏳ Verifying code…"), parse_mode="HTML"
    )

    try:
        client = await get_or_create_client(
            message.from_user.id,
            config.api_id, config.api_hash,
            config.device_model, config.system_version,
            config.app_version, config.lang_code,
            config.system_lang_code,
        )
        await client.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash)
        # ─── success ───
        await _on_auth_success(message, state, status_msg)

    except PhoneCodeInvalidError:
        await status_msg.edit_text(
            _fmt(
                "❌ <b>Invalid code.</b> Please check and try again.\n\n"
                "📟 <b>Step 2 / 3 — Verification code</b>"
            ),
            reply_markup=cancel_kb(),
            parse_mode="HTML",
        )
        # Stay in waiting_code state — user can re-enter

    except PhoneCodeExpiredError:
        await state.set_state(AuthStates.waiting_phone)
        await status_msg.edit_text(
            _fmt("⏰ <b>Code expired.</b> Please send your phone number again."),
            reply_markup=cancel_kb(),
            parse_mode="HTML",
        )

    except SessionPasswordNeededError:
        await state.set_state(AuthStates.waiting_password)
        await status_msg.edit_text(
            _fmt(
                "🔒 <b>Step 3 / 3 — Two-Factor Authentication</b>\n\n"
                "Your account has a cloud password enabled.\n"
                "Please enter your <b>2FA password</b>:"
            ),
            reply_markup=cancel_kb(),
            parse_mode="HTML",
        )

    except FloodWaitError as e:
        await state.clear()
        await disconnect_client(message.from_user.id)
        await status_msg.edit_text(
            _fmt(
                f"🚫 <b>FloodWait</b>: Cooldown of <b>{e.seconds}s</b>.\n\n"
                "Please try again later."
            ),
            reply_markup=main_menu_kb(),
            parse_mode="HTML",
        )
    except Exception as exc:
        logger.exception("sign_in (code) failed: %s", exc)
        await state.clear()
        await disconnect_client(message.from_user.id)
        await status_msg.edit_text(
            _fmt(f"❌ Unexpected error: <code>{exc}</code>"),
            reply_markup=main_menu_kb(),
            parse_mode="HTML",
        )


# ──────────────────────────── 2FA password ──────────────────────────────────

@router.message(AuthStates.waiting_password)
async def handle_password(message: Message, state: FSMContext) -> None:
    password = message.text.strip()

    # Delete the message so the password isn't visible in chat
    try:
        await message.delete()
    except Exception:
        pass

    status_msg = await message.answer(
        _fmt("⏳ Checking password…"), parse_mode="HTML"
    )

    try:
        client = await get_or_create_client(
            message.from_user.id,
            config.api_id, config.api_hash,
            config.device_model, config.system_version,
            config.app_version, config.lang_code,
            config.system_lang_code,
        )
        await client.sign_in(password=password)
        await _on_auth_success(message, state, status_msg)

    except PasswordHashInvalidError:
        await status_msg.edit_text(
            _fmt(
                "❌ <b>Incorrect password.</b> Please try again.\n\n"
                "🔒 <b>Step 3 / 3 — Two-Factor Authentication</b>"
            ),
            reply_markup=cancel_kb(),
            parse_mode="HTML",
        )
        # Stay in waiting_password state — user can re-enter

    except FloodWaitError as e:
        await state.clear()
        await disconnect_client(message.from_user.id)
        await status_msg.edit_text(
            _fmt(f"🚫 <b>FloodWait</b>: Cooldown of <b>{e.seconds}s</b>."),
            reply_markup=main_menu_kb(),
            parse_mode="HTML",
        )
    except Exception as exc:
        logger.exception("sign_in (password) failed: %s", exc)
        await state.clear()
        await disconnect_client(message.from_user.id)
        await status_msg.edit_text(
            _fmt(f"❌ Unexpected error: <code>{exc}</code>"),
            reply_markup=main_menu_kb(),
            parse_mode="HTML",
        )


# ──────────────────────────── success ───────────────────────────────────────

async def _on_auth_success(message: Message, state: FSMContext, status_msg) -> None:
    """Called after a successful sign-in — set state and show download menu."""
    await state.set_state(AuthStates.authenticated)
    me_info = ""
    try:
        from utils.client_manager import _clients
        client = _clients.get(message.from_user.id)
        if client:
            me = await client.get_me()
            name = f"{me.first_name or ''} {me.last_name or ''}".strip()
            username = f"@{me.username}" if me.username else "no username"
            me_info = (
                f"\n👤 <b>Logged in as:</b> {name} ({username})\n"
                f"📱 <b>Phone:</b> <code>+{me.phone}</code>"
            )
    except Exception:
        pass

    await status_msg.edit_text(
        _fmt(
            f"✅ <b>Successfully authenticated!</b>{me_info}\n\n"
            "Choose the format you want to download:"
        ),
        reply_markup=download_kb(),
        parse_mode="HTML",
    )
