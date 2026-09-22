from datetime import time

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.database.models import MealType
from app.database.repo import get_or_create_user, update_user_profile, upsert_reminder_setting
from app.database.session import session_scope
from app.handlers.states import SettingsStates
from app.keyboards.settings import reminders_menu_keyboard, settings_menu_keyboard
from app.utils.texts import MEAL_TYPE_LABELS

router = Router(name="settings")


async def _get_user(from_user, session):
    return await get_or_create_user(
        session, telegram_id=from_user.id, username=from_user.username, full_name=from_user.full_name
    )


@router.callback_query(F.data == "menu:settings")
async def show_settings(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    async with session_scope() as session:
        user = await _get_user(callback.from_user, session)

    await callback.message.edit_text("⚙️ Настройки", reply_markup=settings_menu_keyboard(user))
    await callback.answer()


@router.callback_query(F.data == "settings:allergies")
async def ask_allergies(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(SettingsStates.waiting_allergies)
    await callback.message.edit_text(
        "Перечисли аллергии через запятую (например: орехи, молоко, рыба).\n"
        "Если аллергий нет — отправь «нет»."
    )
    await callback.answer()


@router.message(SettingsStates.waiting_allergies)
async def save_allergies(message: Message, state: FSMContext) -> None:
    allergies = _parse_list(message.text)
    async with session_scope() as session:
        user = await _get_user(message.from_user, session)
        user = await update_user_profile(session, user, allergies=allergies)
        keyboard = settings_menu_keyboard(user)

    await state.clear()
    await message.answer("Готово, сохранил ✅", reply_markup=keyboard)


@router.callback_query(F.data == "settings:disliked")
async def ask_disliked(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(SettingsStates.waiting_disliked)
    await callback.message.edit_text(
        "Перечисли нелюбимые продукты через запятую (например: грибы, оливки).\n"
        "Если таких нет — отправь «нет»."
    )
    await callback.answer()


@router.message(SettingsStates.waiting_disliked)
async def save_disliked(message: Message, state: FSMContext) -> None:
    disliked = _parse_list(message.text)
    async with session_scope() as session:
        user = await _get_user(message.from_user, session)
        user = await update_user_profile(session, user, disliked_products=disliked)
        keyboard = settings_menu_keyboard(user)

    await state.clear()
    await message.answer("Готово, сохранил ✅", reply_markup=keyboard)


@router.callback_query(F.data == "settings:reminders")
async def show_reminders(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text(
        "Для какого приёма пищи настроить напоминание?", reply_markup=reminders_menu_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("settings:reminder:"))
async def ask_reminder_time(callback: CallbackQuery, state: FSMContext) -> None:
    meal_value = callback.data.split(":")[-1]
    await state.update_data(meal_type=meal_value)
    await state.set_state(SettingsStates.waiting_reminder_time)
    label = MEAL_TYPE_LABELS[meal_value]
    await callback.message.edit_text(
        f"Во сколько напоминать про {label.lower()}? Напиши время в формате ЧЧ:ММ (например, 08:30)."
    )
    await callback.answer()


@router.message(SettingsStates.waiting_reminder_time)
async def save_reminder_time(message: Message, state: FSMContext) -> None:
    parsed = _parse_time(message.text)
    if parsed is None:
        await message.answer("Не понял время. Формат: ЧЧ:ММ, например 19:00.")
        return

    data = await state.get_data()
    meal_type = MealType(data["meal_type"])

    async with session_scope() as session:
        user = await _get_user(message.from_user, session)
        await upsert_reminder_setting(session, user, meal_type, parsed)

    await state.clear()
    label = MEAL_TYPE_LABELS[meal_type.value]
    await message.answer(
        f"Готово! Буду напоминать про {label.lower()} в {parsed.strftime('%H:%M')} ✅",
        reply_markup=reminders_menu_keyboard(),
    )


def _parse_list(text: str | None) -> list[str]:
    if not text or text.strip().lower() in {"нет", "-", "none"}:
        return []
    return [item.strip() for item in text.split(",") if item.strip()]


def _parse_time(text: str | None) -> time | None:
    if not text:
        return None
    try:
        hours_str, minutes_str = text.strip().split(":")
        return time(hour=int(hours_str), minute=int(minutes_str))
    except (ValueError, AttributeError):
        return None
