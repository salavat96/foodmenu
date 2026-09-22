from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.database.models import MealType, User
from app.utils.texts import MEAL_TYPE_LABELS


def settings_menu_keyboard(user: User) -> InlineKeyboardMarkup:
    allergies = ", ".join(user.allergies) or "не заданы"
    disliked = ", ".join(user.disliked_products) or "не заданы"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"🚫 Аллергии: {allergies}", callback_data="settings:allergies")],
            [InlineKeyboardButton(text=f"😐 Не люблю: {disliked}", callback_data="settings:disliked")],
            [InlineKeyboardButton(text="⏰ Время напоминаний", callback_data="settings:reminders")],
            [InlineKeyboardButton(text="⬅️ В главное меню", callback_data="menu:main")],
        ]
    )


def reminders_menu_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=f"⏰ {label}", callback_data=f"settings:reminder:{meal.value}")]
        for meal, label in [
            (MealType.breakfast, MEAL_TYPE_LABELS["breakfast"]),
            (MealType.lunch, MEAL_TYPE_LABELS["lunch"]),
            (MealType.dinner, MEAL_TYPE_LABELS["dinner"]),
        ]
    ]
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="menu:settings")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
