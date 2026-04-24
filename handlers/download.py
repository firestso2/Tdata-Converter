import logging

from aiogram import Router
from aiogram.types import CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext

from config import load_config, FOOTER, t
from keyboards import download_kb
from states.auth import AuthStates
from utils.client_manager import _clients, get_user_data
from utils.session_export import export_session_string, export_session_file, export_json
from utils.tdata_export import build_tdata_zip

logger = logging.getLogger(__name__)
router  = Router()
config  = load_config()


def _lang(user_id: int) -> str:
    return get_user_data(user_id, "lang", "ru")


def _phone(user_id: int) -> str:
    return get_user_data(user_id, "phone", "session")


def _safe(phone: str) -> str:
    """'+79991234567' → '79991234567'"""
    return phone.replace("+", "").replace(" ", "")


async def _get_client(user_id: int):
    client = _clients.get(user_id)
    if client is None or not client.is_connected():
        return None
    return client


# ─── .session file ───────────────────────────────────────────────────────────

@router.callback_query(AuthStates.authenticated, lambda c: c.data == "dl_session")
async def cb_dl_session(callback: CallbackQuery, state: FSMContext) -> None:
    lang = _lang(callback.from_user.id)
    await callback.answer()
    client = await _get_client(callback.from_user.id)
    if not client:
        await callback.message.answer(t(lang, "expired") + FOOTER, parse_mode="HTML")
        return

    msg = await callback.message.answer(t(lang, "building") + FOOTER, parse_mode="HTML")
    try:
        buf      = await export_session_file(client)
        filename = f"{_safe(_phone(callback.from_user.id))}.session"
        await msg.delete()
        await callback.message.answer_document(
            BufferedInputFile(buf.read(), filename=filename),
            caption=t(lang, "session_caption") + FOOTER,
            parse_mode="HTML",
        )
    except Exception as exc:
        logger.exception("export_session_file: %s", exc)
        await msg.edit_text(f"❌ <code>{exc}</code>" + FOOTER, parse_mode="HTML")


# ─── session string ──────────────────────────────────────────────────────────

@router.callback_query(AuthStates.authenticated, lambda c: c.data == "dl_session_str")
async def cb_dl_session_str(callback: CallbackQuery, state: FSMContext) -> None:
    lang = _lang(callback.from_user.id)
    await callback.answer()
    client = await _get_client(callback.from_user.id)
    if not client:
        await callback.message.answer(t(lang, "expired") + FOOTER, parse_mode="HTML")
        return

    msg = await callback.message.answer(t(lang, "building") + FOOTER, parse_mode="HTML")
    try:
        session_str = await export_session_string(client)
        filename    = f"{_safe(_phone(callback.from_user.id))}_session.txt"
        content     = f"# Telethon StringSession\n{session_str}\n"
        await msg.delete()
        await callback.message.answer_document(
            BufferedInputFile(content.encode(), filename=filename),
            caption=t(lang, "str_caption") + FOOTER,
            parse_mode="HTML",
        )
    except Exception as exc:
        logger.exception("export_session_string: %s", exc)
        await msg.edit_text(f"❌ <code>{exc}</code>" + FOOTER, parse_mode="HTML")


# ─── tdata ZIP ───────────────────────────────────────────────────────────────

@router.callback_query(AuthStates.authenticated, lambda c: c.data == "dl_tdata")
async def cb_dl_tdata(callback: CallbackQuery, state: FSMContext) -> None:
    lang  = _lang(callback.from_user.id)
    phone = _phone(callback.from_user.id)
    await callback.answer()
    client = await _get_client(callback.from_user.id)
    if not client:
        await callback.message.answer(t(lang, "expired") + FOOTER, parse_mode="HTML")
        return

    msg = await callback.message.answer(t(lang, "building") + FOOTER, parse_mode="HTML")
    try:
        session_str = await export_session_string(client)
        buf         = build_tdata_zip(session_str, phone=phone)
        filename    = f"{_safe(phone)}_tdata.zip"
        await msg.delete()
        await callback.message.answer_document(
            BufferedInputFile(buf.read(), filename=filename),
            caption=t(lang, "tdata_caption") + t(lang, "tdata_howto") + FOOTER,
            parse_mode="HTML",
        )
    except Exception as exc:
        logger.exception("build_tdata_zip: %s", exc)
        await msg.edit_text(f"❌ <code>{exc}</code>" + FOOTER, parse_mode="HTML")


# ─── JSON ────────────────────────────────────────────────────────────────────

@router.callback_query(AuthStates.authenticated, lambda c: c.data == "dl_json")
async def cb_dl_json(callback: CallbackQuery, state: FSMContext) -> None:
    lang  = _lang(callback.from_user.id)
    phone = _phone(callback.from_user.id)
    await callback.answer()
    client = await _get_client(callback.from_user.id)
    if not client:
        await callback.message.answer(t(lang, "expired") + FOOTER, parse_mode="HTML")
        return

    msg = await callback.message.answer(t(lang, "building") + FOOTER, parse_mode="HTML")
    try:
        buf      = await export_json(
            client,
            api_id=config.api_id,
            api_hash=config.api_hash,
            device_model=config.device_model,
            system_version=config.system_version,
            app_version=config.app_version,
        )
        filename = f"{_safe(phone)}_session.json"
        await msg.delete()
        await callback.message.answer_document(
            BufferedInputFile(buf.read(), filename=filename),
            caption=t(lang, "json_caption") + FOOTER,
            parse_mode="HTML",
        )
    except Exception as exc:
        logger.exception("export_json: %s", exc)
        await msg.edit_text(f"❌ <code>{exc}</code>" + FOOTER, parse_mode="HTML")
