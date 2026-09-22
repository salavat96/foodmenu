from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.database.models import MealType
from app.database.repo import (
    create_ai_recipe,
    get_or_create_user,
    get_recipe,
    list_recipes_by_meal,
    search_recipes,
)
from app.database.session import session_scope
from app.handlers.states import RecipeSearchStates
from app.keyboards.recipes import (
    meal_categories_keyboard,
    recipe_intro_keyboard,
    recipe_list_keyboard,
    recipe_step_keyboard,
)
from app.services.ai_recipe_service import AIRecipeError, generate_recipe
from app.services.recipe_service import format_recipe_intro, format_step

router = Router(name="recipes")


@router.callback_query(F.data == "menu:recipes")
@router.callback_query(F.data == "recipes:categories")
async def show_categories(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text(
        "Выбери категорию рецептов или найди блюдо по названию/продукту:",
        reply_markup=meal_categories_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("recipes:category:"))
async def show_recipes_by_category(callback: CallbackQuery) -> None:
    meal_value = callback.data.split(":")[-1]
    meal_type = MealType(meal_value)

    async with session_scope() as session:
        recipes = await list_recipes_by_meal(session, meal_type)

    if not recipes:
        await callback.answer("В этой категории пока нет рецептов", show_alert=True)
        return

    await callback.message.edit_text(
        "Выбери рецепт:", reply_markup=recipe_list_keyboard(recipes, meal_type=meal_value)
    )
    await callback.answer()


@router.callback_query(F.data == "recipes:search")
async def ask_search_query(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(RecipeSearchStates.waiting_query)
    await callback.message.edit_text(
        "Напиши, что хочешь съесть — название блюда, продукт, который есть дома, "
        "или просто опиши словами. Если готового рецепта в базе нет — сам придумаю."
    )
    await callback.answer()


@router.message(RecipeSearchStates.waiting_query)
async def handle_search_query(message: Message, state: FSMContext) -> None:
    query = message.text or ""

    async with session_scope() as session:
        recipes = await search_recipes(session, query)

    if recipes:
        await state.clear()
        await message.answer("Нашёл вот что:", reply_markup=recipe_list_keyboard(recipes))
        return

    await message.answer("В базе такого не нашёл, спрошу у ИИ, минутку… 🤖")

    async with session_scope() as session:
        user = await get_or_create_user(
            session,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name,
        )
        try:
            draft = await generate_recipe(
                query, user_id=user.id, allergies=user.allergies, disliked=user.disliked_products
            )
        except AIRecipeError as exc:
            await state.clear()
            await message.answer(
                f"⚠️ {exc}. Попробуй переформулировать запрос или посмотри категории.",
                reply_markup=meal_categories_keyboard(),
            )
            return

        recipe = await create_ai_recipe(
            session,
            title=draft.title,
            description=draft.description,
            meal_type=MealType(draft.meal_type),
            calories=draft.calories,
            cook_minutes=draft.cook_minutes,
            servings=draft.servings,
            ingredients=draft.ingredients,
            steps=draft.steps,
        )

    await state.clear()
    await message.answer(
        format_recipe_intro(recipe) + "\n\n<i>Рецепт придуман ИИ по твоему запросу 🤖</i>",
        reply_markup=recipe_intro_keyboard(recipe.id),
    )


@router.callback_query(F.data.startswith("recipes:open:"))
async def open_recipe(callback: CallbackQuery) -> None:
    recipe_id = int(callback.data.split(":")[-1])
    async with session_scope() as session:
        recipe = await get_recipe(session, recipe_id)

    if recipe is None:
        await callback.answer("Рецепт не найден", show_alert=True)
        return

    await callback.message.edit_text(
        format_recipe_intro(recipe), reply_markup=recipe_intro_keyboard(recipe.id)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("recipes:step:"))
async def show_recipe_step(callback: CallbackQuery) -> None:
    _, _, recipe_id_raw, step_index_raw = callback.data.split(":")
    recipe_id = int(recipe_id_raw)
    step_index = int(step_index_raw)

    async with session_scope() as session:
        recipe = await get_recipe(session, recipe_id)

    if recipe is None or not (0 <= step_index < len(recipe.steps)):
        await callback.answer("Шаг не найден", show_alert=True)
        return

    await callback.message.edit_text(
        format_step(recipe, step_index), reply_markup=recipe_step_keyboard(recipe, step_index)
    )
    await callback.answer()
