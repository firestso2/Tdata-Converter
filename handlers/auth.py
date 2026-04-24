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

from config import load_config, FOOTER, t
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


def _lang(user_id: int) -> str:
    return get_user_data(user_id, "lang", "ru")


@router.callback_query(lambda c: c.data == "start_auth")
async def cb_start_auth(callback: CallbackQuery, state: FSMContext) -> None:
    lang = _lang(callback.from_user.id)
    await state.set_state(AuthStates.waiting_phone)
    await callback.message.edit_text(
        t(lang, "ask_phone") + FOOTER,
        reply_markup=cancel_kb(lang),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "cancel_auth")
async def cb_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    lang = _lang(callback.from_user.id)
    await state.clear()
    await disconnect_client(callback.from_user.id)
    await callback.message.edit_text(
        t(lang, "cancelled") + FOOTER,
        reply_markup=main_menu_kb(lang),
        parse_mode="HTML",
    )
    await callback.answer()


# ─── phone ───────────────────────────────────────────────────────────────────

@router.message(AuthStates.waiting_phone)
async def handle_phone(message: Message, state: FSMContext) -> None:
    lang = _lang(message.from_user.id)
    phone = message.text.strip()
    if not phone.startswith("+"):
        await message.answer(t(lang, "phone_fmt") + FOOTER, parse_mode="HTML")
        return

    status = await message.answer(t(lang, "sending_code") + FOOTER, parse_mode="HTML")
    try:
        client = await get_or_create_client(
            message.from_user.id,
            config.api_id, config.api_hash,
            config.device_model, config.system_version,
            config.app_version, config.lang_code, config.system_lang_code,
        )
        result = await client.send_code_request(phone)
        store_user_data(message.from_user.id, "phone", phone)
        store_user_data(message.from_user.id, "phone_code_hash", result.phone_code_hash)
        await state.set_state(AuthStates.waiting_code)
        await status.edit_text(
            t(lang, "code_sent") + FOOTER,
            reply_markup=cancel_kb(lang),
            parse_mode="HTML",
        )
    except FloodWaitError as e:
        await state.clear()
        await disconnect_client(message.from_user.id)
        await status.edit_text(
            t(lang, "flood", sec=e.seconds) + FOOTER,
            reply_markup=main_menu_kb(lang),
            parse_mode="HTML",
        )
    except Exception as exc:
        logger.exception("send_code_request: %s", exc)
        await state.clear()
        await disconnect_client(message.from_user.id)
        await status.edit_text(
            f"❌ <code>{exc}</code>" + FOOTER,
            reply_markup=main_menu_kb(lang),
            parse_mode="HTML",
        )


# ─── code ────────────────────────────────────────────────────────────────────

@router.message(AuthStates.waiting_code)
async def handle_code(message: Message, state: FSMContext) -> None:
    lang = _lang(message.from_user.id)
    code = message.text.strip().replace("-", "").replace(" ", "")
    phone = get_user_data(message.from_user.id, "phone")
    phone_code_hash = get_user_data(message.from_user.id, "phone_code_hash")

    status = await message.answer(t(lang, "checking") + FOOTER, parse_mode="HTML")
    try:
        client = await get_or_create_client(
            message.from_user.id,
            config.api_id, config.api_hash,
            config.device_model, config.system_version,
            config.app_version, config.lang_code, config.system_lang_code,
        )
        await client.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash)
        await _on_success(message, state, status)

    except PhoneCodeInvalidError:
        await status.edit_text(
            t(lang, "wrong_code") + FOOTER,
            reply_markup=cancel_kb(lang),
            parse_mode="HTML",
        )
    except PhoneCodeExpiredError:
        await state.set_state(AuthStates.waiting_phone)
        await status.edit_text(
            t(lang, "code_expired") + FOOTER,
            reply_markup=cancel_kb(lang),
            parse_mode="HTML",
        )
    except SessionPasswordNeededError:
        await state.set_state(AuthStates.waiting_password)
        await status.edit_text(
            t(lang, "ask_2fa") + FOOTER,
            reply_markup=cancel_kb(lang),
            parse_mode="HTML",
        )
    except FloodWaitError as e:
        await state.clear()
        await disconnect_client(message.from_user.id)
        await status.edit_text(
            t(lang, "flood", sec=e.seconds) + FOOTER,
            reply_markup=main_menu_kb(lang),
            parse_mode="HTML",
        )
    except Exception as exc:
        logger.exception("sign_in code: %s", exc)
        await state.clear()
        await disconnect_client(message.from_user.id)
        await status.edit_text(
            f"❌ <code>{exc}</code>" + FOOTER,
            reply_markup=main_menu_kb(lang),
            parse_mode="HTML",
        )


# ─── 2FA password ────────────────────────────────────────────────────────────

@router.message(AuthStates.waiting_password)
async def handle_password(message: Message, state: FSMContext) -> None:
    lang = _lang(message.from_user.id)
    password = message.text.strip()
    try:
        await message.delete()
    except Exception:
        pass

    status = await message.answer(t(lang, "checking") + FOOTER, parse_mode="HTML")
    try:
        client = await get_or_create_client(
            message.from_user.id,
            config.api_id, config.api_hash,
            config.device_model, config.system_version,
            config.app_version, config.lang_code, config.system_lang_code,
        )
        await client.sign_in(password=password)
        await _on_success(message, state, status)

    except PasswordHashInvalidError:
        await status.edit_text(
            t(lang, "wrong_pass") + FOOTER,
            reply_markup=cancel_kb(lang),
            parse_mode="HTML",
        )
    except FloodWaitError as e:
        await state.clear()
        await disconnect_client(message.from_user.id)
        await status.edit_text(
            t(lang, "flood", sec=e.seconds) + FOOTER,
            reply_markup=main_menu_kb(lang),
            parse_mode="HTML",
        )
    except Exception as exc:
        logger.exception("sign_in password: %s", exc)
        await state.clear()
        await disconnect_client(message.from_user.id)
        await status.edit_text(
            f"❌ <code>{exc}</code>" + FOOTER,
            reply_markup=main_menu_kb(lang),
            parse_mode="HTML",
        )


# ─── success ─────────────────────────────────────────────────────────────────

async def _on_success(message: Message, state: FSMContext, status_msg) -> None:
    await state.set_state(AuthStates.authenticated)
    lang = _lang(message.from_user.id)
    me_str = ""
    try:
        from utils.client_manager import _clients
        client = _clients.get(message.from_user.id)
        if client:
            me = await client.get_me()
            name = f"{me.first_name or ''} {me.last_name or ''}".strip()
            username = f"@{me.username}" if me.username else "—"
            phone = f"+{me.phone}" if me.phone else "—"
            # save phone with + for filenames
            store_user_data(message.from_user.id, "phone", phone)
            me_str = t(lang, "logged_as", name=name, username=username, phone=phone)
    except Exception:
        pass

    await status_msg.edit_text(
        t(lang, "success", me=me_str) + FOOTER,
        reply_markup=download_kb(lang),
        parse_mode="HTML",
    )
