from __future__ import annotations

import random
from datetime import date, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import BudgetLevel, DietType, MealType, MenuPlan, Recipe, User
from app.database.repo import create_menu_plan, list_recipes_by_meal
from app.utils.texts import BUDGET_LABELS, DIET_TYPE_LABELS, MEAL_TYPE_LABELS

MEAL_ORDER = [MealType.breakfast, MealType.lunch, MealType.dinner]


class NoRecipesAvailableError(Exception):
    """Не нашлось ни одного рецепта под заданные ограничения."""


async def generate_menu_plan(
    session: AsyncSession,
    user: User,
    *,
    start: date,
    days: int,
    budget_level: BudgetLevel,
    diet_type: DietType,
) -> MenuPlan:
    """Общий движок генерации меню.

    Используется и для обычного меню на период, и для меню для похудения/диеты —
    разница только в параметре diet_type и (в перспективе) в фильтре по калорийности.
    """
    candidates_by_meal: dict[MealType, list[Recipe]] = {}
    for meal_type in MEAL_ORDER:
        recipes = await list_recipes_by_meal(
            session,
            meal_type,
            diet_type=diet_type,
            budget_level=budget_level,
            exclude_allergens=user.allergies,
            exclude_names=user.disliked_products,
        )
        if not recipes:
            raise NoRecipesAvailableError(
                f"Нет подходящих рецептов для «{MEAL_TYPE_LABELS[meal_type.value]}» "
                "с учётом заданных ограничений"
            )
        candidates_by_meal[meal_type] = recipes

    entries: list[tuple[date, MealType, int]] = []
    last_used: dict[MealType, int | None] = {meal: None for meal in MEAL_ORDER}

    for day_offset in range(days):
        current_date = start + timedelta(days=day_offset)
        for meal_type in MEAL_ORDER:
            pool = candidates_by_meal[meal_type]
            choices = [r for r in pool if r.id != last_used[meal_type]] or pool
            recipe = random.choice(choices)
            last_used[meal_type] = recipe.id
            entries.append((current_date, meal_type, recipe.id))

    end = start + timedelta(days=days - 1)
    return await create_menu_plan(
        session,
        user,
        start=start,
        end=end,
        budget_level=budget_level,
        diet_type=diet_type,
        entries=entries,
    )


def format_menu_plan(plan: MenuPlan) -> str:
    by_date: dict[date, dict[MealType, str]] = {}
    for entry in plan.entries:
        by_date.setdefault(entry.entry_date, {})[entry.meal_type] = entry.recipe.title

    lines = [
        f"📅 Меню с {plan.start_date.strftime('%d.%m')} по {plan.end_date.strftime('%d.%m')}",
        f"Диета: {DIET_TYPE_LABELS[plan.diet_type.value]} · Бюджет: {BUDGET_LABELS[plan.budget_level.value]}",
        "",
    ]

    for day, meals in sorted(by_date.items()):
        lines.append(f"<b>{day.strftime('%d.%m')}</b>")
        for meal_type in MEAL_ORDER:
            title = meals.get(meal_type, "—")
            lines.append(f"  {MEAL_TYPE_LABELS[meal_type.value]}: {title}")
        lines.append("")

    return "\n".join(lines).strip()
