from datetime import date

import pytest

from app.database.models import BudgetLevel, DietType, User
from app.services.menu_service import NoRecipesAvailableError, format_menu_plan, generate_menu_plan


async def test_generate_menu_plan_creates_entry_per_meal_per_day(db_session, user: User):
    plan = await generate_menu_plan(
        db_session,
        user,
        start=date(2024, 1, 1),
        days=7,
        budget_level=BudgetLevel.high,
        diet_type=DietType.regular,
    )

    assert len(plan.entries) == 7 * 3
    assert plan.start_date == date(2024, 1, 1)
    assert plan.end_date == date(2024, 1, 7)


async def test_generate_menu_plan_respects_allergies(db_session, user: User):
    user.allergies = ["nuts"]

    plan = await generate_menu_plan(
        db_session,
        user,
        start=date(2024, 1, 1),
        days=3,
        budget_level=BudgetLevel.high,
        diet_type=DietType.regular,
    )

    for entry in plan.entries:
        assert not (set(entry.recipe.allergens) & set(user.allergies))


async def test_generate_menu_plan_raises_when_nothing_matches(db_session, user: User):
    user.allergies = ["eggs", "dairy", "fish", "nuts"]

    with pytest.raises(NoRecipesAvailableError):
        await generate_menu_plan(
            db_session,
            user,
            start=date(2024, 1, 1),
            days=3,
            budget_level=BudgetLevel.low,
            diet_type=DietType.vegan,
        )


async def test_format_menu_plan_contains_dates_and_meals(db_session, user: User):
    plan = await generate_menu_plan(
        db_session,
        user,
        start=date(2024, 1, 1),
        days=2,
        budget_level=BudgetLevel.high,
        diet_type=DietType.regular,
    )

    text = format_menu_plan(plan)
    assert "01.01" in text
    assert "02.01" in text
    assert "Завтрак" in text and "Обед" in text and "Ужин" in text
