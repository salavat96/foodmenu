from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.database.repo import get_or_create_user
from app.database.session import session_scope
from app.keyboards.common import MAIN_MENU_KEYBOARD
from app.utils.texts import WELCOME_TEXT

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    async with session_scope() as session:
        await get_or_create_user(
            session,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name,
        )
    await message.answer(WELCOME_TEXT, reply_markup=MAIN_MENU_KEYBOARD)


@router.callback_query(F.data == "menu:main")
async def show_main_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text(WELCOME_TEXT, reply_markup=MAIN_MENU_KEYBOARD)
    await callback.answer()
