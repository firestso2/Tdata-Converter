from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import FOOTER, t
from keyboards import lang_kb, main_menu_kb
from states.auth import AuthStates
from utils.client_manager import disconnect_client, store_user_data, get_user_data

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await disconnect_client(message.from_user.id)
    await state.set_state(AuthStates.choosing_lang)
    await message.answer(
        "🌐 Выберите язык / Choose language:" + FOOTER,
        reply_markup=lang_kb(),
        parse_mode="HTML",
    )


@router.callback_query(lambda c: c.data in ("lang_ru", "lang_en"))
async def cb_choose_lang(callback: CallbackQuery, state: FSMContext) -> None:
    lang = callback.data.split("_")[1]   # "ru" or "en"
    store_user_data(callback.from_user.id, "lang", lang)
    await state.clear()
    await callback.message.edit_text(
        t(lang, "welcome") + FOOTER,
        reply_markup=main_menu_kb(lang),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "back_menu")
async def cb_back(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await disconnect_client(callback.from_user.id)
    lang = get_user_data(callback.from_user.id, "lang", "ru")
    await callback.message.edit_text(
        t(lang, "welcome") + FOOTER,
        reply_markup=main_menu_kb(lang),
        parse_mode="HTML",
    )
    await callback.answer()
