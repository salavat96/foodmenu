from __future__ import annotations

from datetime import date, time

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import (
    BudgetLevel,
    DietType,
    Goal,
    MealType,
    MenuEntry,
    MenuPlan,
    Recipe,
    ReminderSetting,
    User,
)


async def get_or_create_user(
    session: AsyncSession, telegram_id: int, username: str | None, full_name: str | None
) -> User:
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    if user is not None:
        return user

    user = User(telegram_id=telegram_id, username=username, full_name=full_name)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def update_user_profile(
    session: AsyncSession,
    user: User,
    *,
    allergies: list[str] | None = None,
    disliked_products: list[str] | None = None,
    diet_type: DietType | None = None,
    goal: Goal | None = None,
    budget_level: BudgetLevel | None = None,
    timezone: str | None = None,
) -> User:
    if allergies is not None:
        user.allergies = allergies
    if disliked_products is not None:
        user.disliked_products = disliked_products
    if diet_type is not None:
        user.diet_type = diet_type
    if goal is not None:
        user.goal = goal
    if budget_level is not None:
        user.budget_level = budget_level
    if timezone is not None:
        user.timezone = timezone

    await session.commit()
    await session.refresh(user)
    return user


async def list_recipes_by_meal(
    session: AsyncSession,
    meal_type: MealType,
    *,
    diet_type: DietType | None = None,
    budget_level: BudgetLevel | None = None,
    exclude_allergens: list[str] | None = None,
    exclude_names: list[str] | None = None,
) -> list[Recipe]:
    stmt = (
        select(Recipe)
        .where(Recipe.meal_type == meal_type)
        .options(selectinload(Recipe.ingredients), selectinload(Recipe.steps))
    )
    result = await session.execute(stmt)
    recipes = list(result.scalars().all())

    exclude_allergens = {a.strip().lower() for a in (exclude_allergens or []) if a.strip()}
    exclude_names = {n.strip().lower() for n in (exclude_names or []) if n.strip()}

    filtered = []
    for recipe in recipes:
        recipe_allergens = {a.lower() for a in recipe.allergens}
        if recipe_allergens & exclude_allergens:
            continue

        ingredient_names = {i.name.lower() for i in recipe.ingredients}
        if ingredient_names & exclude_names:
            continue
        if recipe.title.lower() in exclude_names:
            continue

        if diet_type is not None and diet_type != DietType.regular:
            if diet_type.value not in recipe.diet_tags:
                continue

        if budget_level is not None:
            budget_order = {BudgetLevel.low: 0, BudgetLevel.medium: 1, BudgetLevel.high: 2}
            if budget_order[recipe.budget_level] > budget_order[budget_level]:
                continue

        filtered.append(recipe)

    return filtered


async def get_recipe(session: AsyncSession, recipe_id: int) -> Recipe | None:
    stmt = (
        select(Recipe)
        .where(Recipe.id == recipe_id)
        .options(selectinload(Recipe.ingredients), selectinload(Recipe.steps))
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def search_recipes(session: AsyncSession, query: str) -> list[Recipe]:
    stmt = select(Recipe).options(selectinload(Recipe.ingredients), selectinload(Recipe.steps))
    result = await session.execute(stmt)
    recipes = list(result.scalars().all())

    query_lower = query.lower().strip()
    matches = []
    for recipe in recipes:
        haystacks = [recipe.title.lower()] + [i.name.lower() for i in recipe.ingredients]
        if any(query_lower in h for h in haystacks):
            matches.append(recipe)
    return matches


async def create_menu_plan(
    session: AsyncSession,
    user: User,
    *,
    start: date,
    end: date,
    budget_level: BudgetLevel,
    diet_type: DietType,
    entries: list[tuple[date, MealType, int]],
) -> MenuPlan:
    plan = MenuPlan(
        user_id=user.id,
        start_date=start,
        end_date=end,
        budget_level=budget_level,
        diet_type=diet_type,
    )
    session.add(plan)
    await session.flush()

    for entry_date, meal_type, recipe_id in entries:
        session.add(
            MenuEntry(
                menu_plan_id=plan.id,
                entry_date=entry_date,
                meal_type=meal_type,
                recipe_id=recipe_id,
            )
        )

    await session.commit()

    stmt = (
        select(MenuPlan)
        .where(MenuPlan.id == plan.id)
        .options(selectinload(MenuPlan.entries).selectinload(MenuEntry.recipe))
    )
    result = await session.execute(stmt)
    return result.scalar_one()


async def get_latest_menu_plan(session: AsyncSession, user: User) -> MenuPlan | None:
    stmt = (
        select(MenuPlan)
        .where(MenuPlan.user_id == user.id)
        .order_by(MenuPlan.created_at.desc())
        .options(selectinload(MenuPlan.entries).selectinload(MenuEntry.recipe))
    )
    result = await session.execute(stmt)
    return result.scalars().first()


async def get_menu_entry_for_date(
    session: AsyncSession, user: User, entry_date: date, meal_type: MealType
) -> MenuEntry | None:
    stmt = (
        select(MenuEntry)
        .join(MenuPlan)
        .where(
            MenuPlan.user_id == user.id,
            MenuEntry.entry_date == entry_date,
            MenuEntry.meal_type == meal_type,
        )
        .order_by(MenuPlan.created_at.desc())
        .options(selectinload(MenuEntry.recipe))
    )
    result = await session.execute(stmt)
    return result.scalars().first()


async def upsert_reminder_setting(
    session: AsyncSession, user: User, meal_type: MealType, remind_at: time, enabled: bool = True
) -> ReminderSetting:
    stmt = select(ReminderSetting).where(
        ReminderSetting.user_id == user.id, ReminderSetting.meal_type == meal_type
    )
    result = await session.execute(stmt)
    setting = result.scalar_one_or_none()

    if setting is None:
        setting = ReminderSetting(
            user_id=user.id, meal_type=meal_type, remind_at=remind_at, enabled=enabled
        )
        session.add(setting)
    else:
        setting.remind_at = remind_at
        setting.enabled = enabled

    await session.commit()
    await session.refresh(setting)
    return setting


async def list_reminder_settings(session: AsyncSession, user: User) -> list[ReminderSetting]:
    stmt = select(ReminderSetting).where(ReminderSetting.user_id == user.id)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def list_due_reminders(session: AsyncSession, at_time: time) -> list[ReminderSetting]:
    stmt = (
        select(ReminderSetting)
        .where(
            ReminderSetting.enabled.is_(True),
            ReminderSetting.remind_at == at_time,
        )
        .options(selectinload(ReminderSetting.user))
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())
