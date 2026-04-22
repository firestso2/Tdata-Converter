import logging

from aiogram import Router
from aiogram.types import CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext

from config import load_config, FOOTER
from keyboards import download_kb
from states.auth import AuthStates
from utils.client_manager import _clients, get_user_data
from utils.session_export import export_session_string, export_session_file, export_json
from utils.tdata_export import build_tdata_zip

logger = logging.getLogger(__name__)
router = Router()
config = load_config()


def _footer_caption(title: str, extra: str = "") -> str:
    return f"<b>{title}</b>{extra}{FOOTER}"


async def _get_client(user_id: int):
    client = _clients.get(user_id)
    if client is None or not client.is_connected():
        return None
    return client


# ──────────────────────────── .session file ─────────────────────────────────

@router.callback_query(AuthStates.authenticated, lambda c: c.data == "dl_session")
async def cb_dl_session(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer("⏳ Building .session file…")
    client = await _get_client(callback.from_user.id)
    if not client:
        await callback.message.answer("⚠️ Session expired. Please /start again.")
        return

    try:
        buf = await export_session_file(client)
        phone = get_user_data(callback.from_user.id, "phone", "session")
        safe_phone = phone.replace("+", "").replace(" ", "_")
        filename = f"{safe_phone}.session"

        await callback.message.answer_document(
            BufferedInputFile(buf.read(), filename=filename),
            caption=_footer_caption(
                "📄 Telethon <code>.session</code> file",
                "\n\nImport with: <code>TelegramClient('name', api_id, api_hash)</code>",
            ),
            parse_mode="HTML",
        )
    except Exception as exc:
        logger.exception("export_session_file error: %s", exc)
        await callback.message.answer(f"❌ Error generating .session: <code>{exc}</code>",
                                      parse_mode="HTML")


# ──────────────────────────── session string ────────────────────────────────

@router.callback_query(AuthStates.authenticated, lambda c: c.data == "dl_session_str")
async def cb_dl_session_str(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer("⏳ Fetching session string…")
    client = await _get_client(callback.from_user.id)
    if not client:
        await callback.message.answer("⚠️ Session expired. Please /start again.")
        return

    try:
        session_str = await export_session_string(client)
        # Send as a file so it isn't truncated in the chat bubble
        content = f"# Telethon StringSession\n{session_str}\n"
        await callback.message.answer_document(
            BufferedInputFile(content.encode(), filename="session_string.txt"),
            caption=_footer_caption(
                "🔑 Telethon StringSession",
                "\n\nUse with: <code>TelegramClient(StringSession('…'), …)</code>",
            ),
            parse_mode="HTML",
        )
    except Exception as exc:
        logger.exception("export_session_string error: %s", exc)
        await callback.message.answer(f"❌ Error: <code>{exc}</code>", parse_mode="HTML")


# ──────────────────────────── tdata ZIP ─────────────────────────────────────

@router.callback_query(AuthStates.authenticated, lambda c: c.data == "dl_tdata")
async def cb_dl_tdata(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer("⏳ Building tdata archive…")
    client = await _get_client(callback.from_user.id)
    if not client:
        await callback.message.answer("⚠️ Session expired. Please /start again.")
        return

    try:
        session_str = await export_session_string(client)
        buf = build_tdata_zip(session_str)

        await callback.message.answer_document(
            BufferedInputFile(buf.read(), filename="tdata.zip"),
            caption=_footer_caption(
                "🗂 Telegram Desktop <code>tdata</code> archive",
                (
                    "\n\n<b>How to use:</b>\n"
                    "1. Extract the ZIP — you'll get a <code>tdata/</code> folder.\n"
                    "2. Place it next to your <code>Telegram.exe</code> / app binary.\n"
                    "3. Launch Telegram Desktop — it will pick up the session automatically."
                ),
            ),
            parse_mode="HTML",
        )
    except Exception as exc:
        logger.exception("build_tdata_zip error: %s", exc)
        await callback.message.answer(f"❌ Error building tdata: <code>{exc}</code>",
                                      parse_mode="HTML")


# ──────────────────────────── JSON metadata ─────────────────────────────────

@router.callback_query(AuthStates.authenticated, lambda c: c.data == "dl_json")
async def cb_dl_json(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer("⏳ Building JSON metadata…")
    client = await _get_client(callback.from_user.id)
    if not client:
        await callback.message.answer("⚠️ Session expired. Please /start again.")
        return

    try:
        buf = await export_json(
            client,
            api_id=config.api_id,
            api_hash=config.api_hash,
            device_model=config.device_model,
            system_version=config.system_version,
            app_version=config.app_version,
        )
        await callback.message.answer_document(
            BufferedInputFile(buf.read(), filename="session.json"),
            caption=_footer_caption(
                "📋 Session metadata JSON",
                "\n\nContains: API credentials, DC info, account details, session string.",
            ),
            parse_mode="HTML",
        )
    except Exception as exc:
        logger.exception("export_json error: %s", exc)
        await callback.message.answer(f"❌ Error: <code>{exc}</code>", parse_mode="HTML")
