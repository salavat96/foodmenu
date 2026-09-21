"""Начальный набор рецептов для наполнения БД при первом запуске.

Каждый рецепт — словарь с ингредиентами и пошаговыми инструкциями.
Список специально небольшой (демо-набор); дальше база рецептов расширяется
без изменения кода бота.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import BudgetLevel, Ingredient, MealType, Recipe, RecipeStep

RECIPES: list[dict] = [
    {
        "title": "Овсянка с бананом и орехами",
        "description": "Быстрый сытный завтрак с медленными углеводами.",
        "meal_type": MealType.breakfast,
        "diet_tags": ["vegetarian", "regular"],
        "allergens": ["nuts"],
        "budget_level": BudgetLevel.low,
        "calories": 380,
        "cook_minutes": 10,
        "servings": 1,
        "ingredients": [
            ("Овсяные хлопья", "60 г"),
            ("Молоко или вода", "200 мл"),
            ("Банан", "1 шт"),
            ("Грецкие орехи", "20 г"),
            ("Мёд", "1 ч.л."),
        ],
        "steps": [
            "Всыпать овсяные хлопья в кастрюлю, залить молоком или водой.",
            "Варить на среднем огне 5-7 минут, помешивая, до загустения.",
            "Нарезать банан кружочками, орехи слегка порубить.",
            "Выложить кашу в тарелку, украсить бананом и орехами, полить мёдом.",
        ],
    },
    {
        "title": "Яичница с овощами",
        "description": "Белковый завтрак с овощами, готовится за 10 минут.",
        "meal_type": MealType.breakfast,
        "diet_tags": ["low_carb", "keto", "high_protein", "vegetarian"],
        "allergens": ["eggs"],
        "budget_level": BudgetLevel.low,
        "calories": 320,
        "cook_minutes": 10,
        "servings": 1,
        "ingredients": [
            ("Яйца", "3 шт"),
            ("Помидор", "1 шт"),
            ("Болгарский перец", "0.5 шт"),
            ("Растительное масло", "1 ст.л."),
            ("Соль, перец", "по вкусу"),
        ],
        "steps": [
            "Нарезать помидор и перец небольшими кубиками.",
            "Разогреть масло на сковороде, обжарить овощи 3 минуты.",
            "Взбить яйца вилкой, вылить на сковороду к овощам.",
            "Готовить на среднем огне 3-4 минуты до желаемой степени прожарки.",
            "Посолить, поперчить и подавать сразу.",
        ],
    },
    {
        "title": "Творог с ягодами",
        "description": "Лёгкий белковый завтрак без готовки.",
        "meal_type": MealType.breakfast,
        "diet_tags": ["low_carb", "high_protein", "vegetarian"],
        "allergens": ["dairy"],
        "budget_level": BudgetLevel.medium,
        "calories": 250,
        "cook_minutes": 5,
        "servings": 1,
        "ingredients": [
            ("Творог 5%", "200 г"),
            ("Ягоды (свежие/замороженные)", "80 г"),
            ("Мёд", "1 ч.л."),
        ],
        "steps": [
            "Выложить творог в тарелку.",
            "Добавить ягоды.",
            "Полить мёдом и перемешать перед подачей.",
        ],
    },
    {
        "title": "Куриный суп с овощами",
        "description": "Классический лёгкий суп на обед.",
        "meal_type": MealType.lunch,
        "diet_tags": ["regular", "high_protein"],
        "allergens": [],
        "budget_level": BudgetLevel.low,
        "calories": 280,
        "cook_minutes": 40,
        "servings": 4,
        "ingredients": [
            ("Куриное филе", "300 г"),
            ("Картофель", "3 шт"),
            ("Морковь", "1 шт"),
            ("Лук", "1 шт"),
            ("Вода", "1.5 л"),
            ("Соль, специи", "по вкусу"),
        ],
        "steps": [
            "Куриное филе залить водой, довести до кипения, снять пену.",
            "Варить курицу 20 минут на среднем огне.",
            "Нарезать картофель кубиками, морковь и лук измельчить.",
            "Добавить овощи в бульон, варить ещё 15 минут.",
            "Посолить, добавить специи, дать настояться 5 минут перед подачей.",
        ],
    },
    {
        "title": "Гречка с грибами",
        "description": "Сытный вегетарианский обед.",
        "meal_type": MealType.lunch,
        "diet_tags": ["vegetarian", "vegan", "regular"],
        "allergens": [],
        "budget_level": BudgetLevel.low,
        "calories": 340,
        "cook_minutes": 30,
        "servings": 2,
        "ingredients": [
            ("Гречка", "150 г"),
            ("Шампиньоны", "200 г"),
            ("Лук", "1 шт"),
            ("Растительное масло", "2 ст.л."),
            ("Соль, перец", "по вкусу"),
        ],
        "steps": [
            "Отварить гречку в подсоленной воде до готовности (около 15 минут).",
            "Нарезать грибы и лук, обжарить на масле до золотистого цвета.",
            "Смешать грибы с луком и готовой гречкой.",
            "Прогреть всё вместе 2-3 минуты, посолить и поперчить по вкусу.",
        ],
    },
    {
        "title": "Салат с курицей и авокадо",
        "description": "Низкоуглеводный сытный обед.",
        "meal_type": MealType.lunch,
        "diet_tags": ["low_carb", "keto", "high_protein"],
        "allergens": [],
        "budget_level": BudgetLevel.medium,
        "calories": 420,
        "cook_minutes": 20,
        "servings": 2,
        "ingredients": [
            ("Куриное филе", "250 г"),
            ("Авокадо", "1 шт"),
            ("Листья салата", "50 г"),
            ("Черри", "100 г"),
            ("Оливковое масло", "1 ст.л."),
            ("Лимонный сок", "1 ч.л."),
        ],
        "steps": [
            "Отварить или обжарить куриное филе, нарезать полосками.",
            "Нарезать авокадо и черри, порвать листья салата руками.",
            "Смешать все ингредиенты в миске.",
            "Заправить оливковым маслом и лимонным соком перед подачей.",
        ],
    },
    {
        "title": "Запечённая рыба с овощами",
        "description": "Лёгкий полезный ужин.",
        "meal_type": MealType.dinner,
        "diet_tags": ["low_carb", "high_protein", "mediterranean"],
        "allergens": ["fish"],
        "budget_level": BudgetLevel.medium,
        "calories": 360,
        "cook_minutes": 35,
        "servings": 2,
        "ingredients": [
            ("Филе белой рыбы", "300 г"),
            ("Цукини", "1 шт"),
            ("Помидоры черри", "150 г"),
            ("Оливковое масло", "2 ст.л."),
            ("Соль, специи, лимон", "по вкусу"),
        ],
        "steps": [
            "Разогреть духовку до 200°C.",
            "Нарезать цукини кружочками, выложить на противень вместе с рыбой и черри.",
            "Полить оливковым маслом, посолить, добавить специи и дольку лимона.",
            "Запекать 20-25 минут до готовности рыбы.",
        ],
    },
    {
        "title": "Овощное рагу",
        "description": "Веганский лёгкий ужин.",
        "meal_type": MealType.dinner,
        "diet_tags": ["vegetarian", "vegan", "low_carb"],
        "allergens": [],
        "budget_level": BudgetLevel.low,
        "calories": 220,
        "cook_minutes": 30,
        "servings": 3,
        "ingredients": [
            ("Кабачок", "1 шт"),
            ("Баклажан", "1 шт"),
            ("Болгарский перец", "1 шт"),
            ("Помидоры", "2 шт"),
            ("Лук", "1 шт"),
            ("Растительное масло", "2 ст.л."),
        ],
        "steps": [
            "Нарезать все овощи средними кубиками.",
            "Обжарить лук на масле до прозрачности.",
            "Добавить остальные овощи, тушить под крышкой 20 минут на слабом огне.",
            "Посолить и поперчить в конце готовки.",
        ],
    },
    {
        "title": "Творожная запеканка",
        "description": "Лёгкий сладковатый ужин или перекус.",
        "meal_type": MealType.dinner,
        "diet_tags": ["vegetarian", "high_protein"],
        "allergens": ["dairy", "eggs"],
        "budget_level": BudgetLevel.medium,
        "calories": 300,
        "cook_minutes": 45,
        "servings": 4,
        "ingredients": [
            ("Творог", "400 г"),
            ("Яйца", "2 шт"),
            ("Манная крупа", "3 ст.л."),
            ("Сахар или мёд", "2 ст.л."),
            ("Изюм", "30 г"),
        ],
        "steps": [
            "Разогреть духовку до 180°C.",
            "Смешать творог, яйца, манку и сахар до однородности.",
            "Добавить изюм, перемешать.",
            "Выложить массу в форму, запекать 30-35 минут до золотистой корочки.",
        ],
    },
]


async def seed_recipes_if_empty(session: AsyncSession) -> None:
    result = await session.execute(select(Recipe.id).limit(1))
    if result.scalar_one_or_none() is not None:
        return

    for item in RECIPES:
        recipe = Recipe(
            title=item["title"],
            description=item["description"],
            meal_type=item["meal_type"],
            diet_tags=item["diet_tags"],
            allergens=item["allergens"],
            budget_level=item["budget_level"],
            calories=item["calories"],
            cook_minutes=item["cook_minutes"],
            servings=item["servings"],
        )
        for index, (name, amount) in enumerate(item["ingredients"]):
            recipe.ingredients.append(Ingredient(name=name, amount=amount, order_index=index))
        for index, text in enumerate(item["steps"], start=1):
            recipe.steps.append(RecipeStep(step_number=index, text=text))

        session.add(recipe)

    await session.commit()
