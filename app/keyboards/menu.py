from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.database.models import BudgetLevel, DietType, Goal
from app.utils.texts import BUDGET_LABELS, DIET_TYPE_LABELS, GOAL_LABELS

DAY_OPTIONS = [7, 14]


def days_keyboard(prefix: str) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=f"{d} дней", callback_data=f"{prefix}:days:{d}")]
        for d in DAY_OPTIONS
    ]
    buttons.append([InlineKeyboardButton(text="⬅️ В главное меню", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def budget_keyboard(prefix: str) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=label, callback_data=f"{prefix}:budget:{level.value}")]
        for level, label in BUDGET_LABELS_ORDERED
    ]
    buttons.append([InlineKeyboardButton(text="⬅️ В главное меню", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


BUDGET_LABELS_ORDERED = [
    (BudgetLevel.low, BUDGET_LABELS["low"]),
    (BudgetLevel.medium, BUDGET_LABELS["medium"]),
    (BudgetLevel.high, BUDGET_LABELS["high"]),
]


def diet_type_keyboard(prefix: str) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=DIET_TYPE_LABELS[diet.value], callback_data=f"{prefix}:diet:{diet.value}")]
        for diet in DietType
    ]
    buttons.append([InlineKeyboardButton(text="⬅️ В главное меню", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def goal_keyboard(prefix: str) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=label, callback_data=f"{prefix}:goal:{goal.value}")]
        for goal, label in [(g, GOAL_LABELS[g.value]) for g in Goal]
    ]
    buttons.append([InlineKeyboardButton(text="⬅️ В главное меню", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def menu_result_keyboard(prefix: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔁 Сгенерировать заново", callback_data=f"{prefix}:restart")],
            [InlineKeyboardButton(text="⬅️ В главное меню", callback_data="menu:main")],
        ]
    )
