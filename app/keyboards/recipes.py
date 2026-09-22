from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.database.models import MealType, Recipe
from app.utils.texts import MEAL_TYPE_LABELS


def meal_categories_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=label, callback_data=f"recipes:category:{meal.value}")]
        for meal, label in [
            (MealType.breakfast, "🍳 Завтраки"),
            (MealType.lunch, "🍲 Обеды"),
            (MealType.dinner, "🍽 Ужины"),
        ]
    ]
    buttons.append([InlineKeyboardButton(text="✍️ Написать, что хочу съесть", callback_data="recipes:search")])
    buttons.append([InlineKeyboardButton(text="⬅️ В главное меню", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def recipe_list_keyboard(recipes: list[Recipe], meal_type: str | None = None) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=recipe.title, callback_data=f"recipes:open:{recipe.id}")]
        for recipe in recipes
    ]
    back_target = "recipes:categories" if meal_type else "menu:recipes"
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=back_target)])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def recipe_intro_keyboard(recipe_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="▶️ Начать готовить", callback_data=f"recipes:step:{recipe_id}:0")],
            [InlineKeyboardButton(text="⬅️ К списку рецептов", callback_data="recipes:categories")],
        ]
    )


def recipe_step_keyboard(recipe: Recipe, step_index: int) -> InlineKeyboardMarkup:
    total = len(recipe.steps)
    nav_row = []
    if step_index > 0:
        nav_row.append(
            InlineKeyboardButton(
                text="◀️ Назад", callback_data=f"recipes:step:{recipe.id}:{step_index - 1}"
            )
        )
    if step_index < total - 1:
        nav_row.append(
            InlineKeyboardButton(
                text="Далее ▶️", callback_data=f"recipes:step:{recipe.id}:{step_index + 1}"
            )
        )

    rows = [nav_row] if nav_row else []
    if step_index == total - 1:
        rows.append([InlineKeyboardButton(text="✅ Готово!", callback_data="recipes:categories")])
    rows.append([InlineKeyboardButton(text="⬅️ К рецепту", callback_data=f"recipes:open:{recipe.id}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
