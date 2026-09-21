from datetime import date

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.database.models import BudgetLevel, DietType, Goal
from app.database.repo import get_or_create_user, update_user_profile
from app.database.session import session_scope
from app.handlers.states import DietFormStates, MenuFormStates
from app.keyboards.common import back_to_main_keyboard
from app.keyboards.menu import budget_keyboard, days_keyboard, diet_type_keyboard, goal_keyboard, menu_result_keyboard
from app.services.menu_service import NoRecipesAvailableError, format_menu_plan, generate_menu_plan

router = Router(name="menu")


async def _get_user(callback: CallbackQuery, session):
    return await get_or_create_user(
        session,
        telegram_id=callback.from_user.id,
        username=callback.from_user.username,
        full_name=callback.from_user.full_name,
    )


# ---------- Обычное меню на период ----------


@router.callback_query(F.data == "menu:plan")
@router.callback_query(F.data == "planform:restart")
async def start_plan_form(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(MenuFormStates.choosing_days)
    await callback.message.edit_text(
        "На сколько дней составить меню?", reply_markup=days_keyboard("planform")
    )
    await callback.answer()


@router.callback_query(MenuFormStates.choosing_days, F.data.startswith("planform:days:"))
async def plan_choose_days(callback: CallbackQuery, state: FSMContext) -> None:
    days = int(callback.data.split(":")[-1])
    await state.update_data(days=days)
    await state.set_state(MenuFormStates.choosing_budget)
    await callback.message.edit_text(
        "Какой бюджет на питание в этот период?", reply_markup=budget_keyboard("planform")
    )
    await callback.answer()


@router.callback_query(MenuFormStates.choosing_budget, F.data.startswith("planform:budget:"))
async def plan_choose_budget(callback: CallbackQuery, state: FSMContext) -> None:
    budget_level = BudgetLevel(callback.data.split(":")[-1])
    data = await state.get_data()
    days = data["days"]

    async with session_scope() as session:
        user = await _get_user(callback, session)
        user = await update_user_profile(session, user, budget_level=budget_level)
        try:
            plan = await generate_menu_plan(
                session,
                user,
                start=date.today(),
                days=days,
                budget_level=budget_level,
                diet_type=user.diet_type,
            )
        except NoRecipesAvailableError as exc:
            await state.clear()
            await callback.message.edit_text(
                f"⚠️ {exc}.\nПопробуй смягчить аллергии/нелюбимые продукты в настройках или другой бюджет.",
                reply_markup=back_to_main_keyboard(),
            )
            await callback.answer()
            return

    await state.clear()
    await callback.message.edit_text(format_menu_plan(plan), reply_markup=menu_result_keyboard("planform"))
    await callback.answer()


# ---------- Меню для похудения / по диете ----------


@router.callback_query(F.data == "menu:diet")
@router.callback_query(F.data == "dietform:restart")
async def start_diet_form(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(DietFormStates.choosing_diet)
    await callback.message.edit_text(
        "Какой тип питания тебе подходит?", reply_markup=diet_type_keyboard("dietform")
    )
    await callback.answer()


@router.callback_query(DietFormStates.choosing_diet, F.data.startswith("dietform:diet:"))
async def diet_choose_diet(callback: CallbackQuery, state: FSMContext) -> None:
    diet_type = DietType(callback.data.split(":")[-1])
    await state.update_data(diet_type=diet_type.value)
    await state.set_state(DietFormStates.choosing_goal)
    await callback.message.edit_text("Какая у тебя цель?", reply_markup=goal_keyboard("dietform"))
    await callback.answer()


@router.callback_query(DietFormStates.choosing_goal, F.data.startswith("dietform:goal:"))
async def diet_choose_goal(callback: CallbackQuery, state: FSMContext) -> None:
    goal = Goal(callback.data.split(":")[-1])
    await state.update_data(goal=goal.value)
    await state.set_state(DietFormStates.choosing_days)
    await callback.message.edit_text(
        "На сколько дней составить меню?", reply_markup=days_keyboard("dietform")
    )
    await callback.answer()


@router.callback_query(DietFormStates.choosing_days, F.data.startswith("dietform:days:"))
async def diet_choose_days(callback: CallbackQuery, state: FSMContext) -> None:
    days = int(callback.data.split(":")[-1])
    data = await state.get_data()
    diet_type = DietType(data["diet_type"])
    goal = Goal(data["goal"])

    async with session_scope() as session:
        user = await _get_user(callback, session)
        user = await update_user_profile(session, user, diet_type=diet_type, goal=goal)
        try:
            plan = await generate_menu_plan(
                session,
                user,
                start=date.today(),
                days=days,
                budget_level=user.budget_level,
                diet_type=diet_type,
            )
        except NoRecipesAvailableError as exc:
            await state.clear()
            await callback.message.edit_text(
                f"⚠️ {exc}.\nПопробуй выбрать другой тип питания или смягчить ограничения в настройках.",
                reply_markup=back_to_main_keyboard(),
            )
            await callback.answer()
            return

    await state.clear()
    await callback.message.edit_text(format_menu_plan(plan), reply_markup=menu_result_keyboard("dietform"))
    await callback.answer()
