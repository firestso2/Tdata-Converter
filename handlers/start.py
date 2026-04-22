from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import FOOTER
from keyboards import main_menu_kb
from utils.client_manager import disconnect_client

router = Router()

WELCOME = (
    "👋 <b>Welcome to Session Exporter Bot</b>\n\n"
    "This bot lets you export your Telegram account into:\n"
    "  • <code>.session</code> — Telethon session file\n"
    "  • <code>TData ZIP</code>  — Telegram Desktop tdata folder\n"
    "  • <code>JSON</code>       — App ID / hash + account metadata\n\n"
    "<b>Press the button below to start.</b>"
    "{footer}"
)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await disconnect_client(message.from_user.id)
    await message.answer(
        WELCOME.format(footer=FOOTER),
        reply_markup=main_menu_kb(),
        parse_mode="HTML",
    )


@router.callback_query(lambda c: c.data == "back_menu")
async def cb_back(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await disconnect_client(callback.from_user.id)
    await callback.message.edit_text(
        WELCOME.format(footer=FOOTER),
        reply_markup=main_menu_kb(),
        parse_mode="HTML",
    )
    await callback.answer()
