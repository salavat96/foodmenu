from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

MAIN_MENU_KEYBOARD = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🍳 Рецепты", callback_data="menu:recipes")],
        [InlineKeyboardButton(text="📅 Меню на неделю/две", callback_data="menu:plan")],
        [InlineKeyboardButton(text="⚖️ Меню для похудения / диета", callback_data="menu:diet")],
        [InlineKeyboardButton(text="⚙️ Настройки", callback_data="menu:settings")],
    ]
)


def back_to_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="⬅️ В главное меню", callback_data="menu:main")]]
    )
