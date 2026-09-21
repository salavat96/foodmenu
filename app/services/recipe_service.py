from __future__ import annotations

from app.database.models import Recipe
from app.utils.texts import MEAL_TYPE_LABELS


def format_recipe_intro(recipe: Recipe) -> str:
    lines = [f"🍽 <b>{recipe.title}</b>"]
    if recipe.description:
        lines.append(recipe.description)

    meta = []
    if recipe.cook_minutes:
        meta.append(f"⏱ {recipe.cook_minutes} мин")
    if recipe.calories:
        meta.append(f"🔥 {recipe.calories} ккал")
    meta.append(f"👥 {recipe.servings} порц.")
    lines.append(" · ".join(meta))

    lines.append("\n<b>Ингредиенты:</b>")
    for ingredient in recipe.ingredients:
        lines.append(f"• {ingredient.name} — {ingredient.amount}")

    lines.append(f"\nШагов приготовления: {len(recipe.steps)}")
    return "\n".join(lines)


def format_step(recipe: Recipe, step_index: int) -> str:
    """step_index — 0-based индекс шага."""
    total = len(recipe.steps)
    step = recipe.steps[step_index]
    lines = [f"🍽 <b>{recipe.title}</b>", f"Шаг {step.step_number}/{total}", "", step.text]
    if step.duration_minutes:
        lines.append(f"\n⏱ {step.duration_minutes} мин")
    return "\n".join(lines)


def meal_type_label(meal_type: str) -> str:
    return MEAL_TYPE_LABELS.get(meal_type, meal_type)
