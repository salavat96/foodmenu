import pytest

from app.services.ai_recipe_service import AIRecipeError, parse_recipe_response


def test_parse_valid_response():
    text = """{
        "title": "Паста с курицей",
        "description": "Быстрый ужин",
        "meal_type": "dinner",
        "calories": 450,
        "cook_minutes": 25,
        "servings": 2,
        "ingredients": [["Паста", "200 г"], ["Куриное филе", "200 г"]],
        "steps": ["Отварить пасту", "Обжарить курицу", "Смешать"]
    }"""

    draft = parse_recipe_response(text)

    assert draft.title == "Паста с курицей"
    assert draft.meal_type == "dinner"
    assert draft.calories == 450
    assert draft.ingredients == [("Паста", "200 г"), ("Куриное филе", "200 г")]
    assert len(draft.steps) == 3


def test_parse_strips_markdown_code_fence():
    text = '```json\n{"title": "Салат", "ingredients": [["Огурец", "1 шт"]], "steps": ["Порезать"]}\n```'

    draft = parse_recipe_response(text)

    assert draft.title == "Салат"
    assert draft.meal_type == "lunch"  # значение по умолчанию


def test_parse_invalid_meal_type_falls_back_to_lunch():
    text = '{"title": "Блюдо", "meal_type": "snack", "ingredients": [["Х", "1"]], "steps": ["Шаг"]}'

    draft = parse_recipe_response(text)

    assert draft.meal_type == "lunch"


def test_parse_invalid_json_raises():
    with pytest.raises(AIRecipeError):
        parse_recipe_response("это не json")


def test_parse_missing_required_field_raises():
    with pytest.raises(AIRecipeError):
        parse_recipe_response('{"title": "Блюдо без шагов", "ingredients": [["Х", "1"]], "steps": []}')
