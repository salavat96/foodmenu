from __future__ import annotations

import json
from dataclasses import dataclass

from anthropic import AsyncAnthropic

from app.config import settings

_VALID_MEAL_TYPES = {"breakfast", "lunch", "dinner"}

_SYSTEM_PROMPT = (
    "Ты — кулинарный ассистент в Telegram-боте. По свободному запросу пользователя "
    "придумай ОДИН конкретный, реально готовящийся рецепт. Строго учитывай "
    "перечисленные ограничения (аллергии, нелюбимые продукты) — такие продукты "
    "не должны встречаться ни в ингредиентах, ни в шагах.\n\n"
    "Ответь ТОЛЬКО валидным JSON без markdown-разметки и без пояснений, "
    "строго в следующем формате:\n"
    '{"title": "название блюда", "description": "1-2 предложения о блюде", '
    '"meal_type": "breakfast|lunch|dinner", "calories": число или null, '
    '"cook_minutes": число, "servings": число, '
    '"ingredients": [["продукт", "количество"], ...], '
    '"steps": ["шаг 1", "шаг 2", ...]}'
)


class AIRecipeError(Exception):
    """Не удалось получить или разобрать рецепт от API."""


@dataclass
class RecipeDraft:
    title: str
    description: str
    meal_type: str
    ingredients: list[tuple[str, str]]
    steps: list[str]
    calories: int | None
    cook_minutes: int | None
    servings: int


def parse_recipe_response(text: str) -> RecipeDraft:
    """Разбирает JSON-ответ модели в RecipeDraft. Вынесено отдельно, чтобы тестировать без сети."""
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise AIRecipeError("Не удалось разобрать ответ от ИИ") from exc

    try:
        title = str(data["title"]).strip()[:255]
        description = str(data.get("description", "")).strip()[:500]
        meal_type = str(data.get("meal_type", "lunch")).strip().lower()
        if meal_type not in _VALID_MEAL_TYPES:
            meal_type = "lunch"

        ingredients = [(str(name).strip(), str(amount).strip()) for name, amount in data["ingredients"]]
        steps = [str(step).strip() for step in data["steps"]]
        if not title or not ingredients or not steps:
            raise AIRecipeError("ИИ вернул неполный рецепт")

        calories = data.get("calories")
        calories = int(calories) if calories is not None else None
        cook_minutes = data.get("cook_minutes")
        cook_minutes = int(cook_minutes) if cook_minutes is not None else None
        servings = int(data.get("servings") or 2)
    except (KeyError, TypeError, ValueError) as exc:
        raise AIRecipeError("Ответ ИИ пришёл в неожиданном формате") from exc

    return RecipeDraft(
        title=title,
        description=description,
        meal_type=meal_type,
        ingredients=ingredients,
        steps=steps,
        calories=calories,
        cook_minutes=cook_minutes,
        servings=servings,
    )


async def generate_recipe(query: str, *, allergies: list[str], disliked: list[str]) -> RecipeDraft:
    if not settings.anthropic_api_key:
        raise AIRecipeError("Функция генерации рецептов по описанию сейчас не настроена")

    constraints = []
    if allergies:
        constraints.append(f"Аллергии, которые нужно исключить полностью: {', '.join(allergies)}.")
    if disliked:
        constraints.append(f"Нелюбимые продукты, которые нужно исключить: {', '.join(disliked)}.")

    user_message = f"Запрос пользователя: {query.strip()}"
    if constraints:
        user_message += "\n" + "\n".join(constraints)

    client = AsyncAnthropic(api_key=settings.anthropic_api_key)
    try:
        response = await client.messages.create(
            model=settings.ai_model,
            max_tokens=1500,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )
    except Exception as exc:  # noqa: BLE001 - любая ошибка API превращается в понятный ответ пользователю
        raise AIRecipeError("Не получилось связаться с сервисом генерации рецептов") from exc

    text_parts = [block.text for block in response.content if getattr(block, "type", None) == "text"]
    return parse_recipe_response("".join(text_parts))
