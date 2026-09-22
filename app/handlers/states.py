from aiogram.fsm.state import State, StatesGroup


class RecipeSearchStates(StatesGroup):
    waiting_query = State()


class MenuFormStates(StatesGroup):
    choosing_days = State()
    choosing_budget = State()
    waiting_allergies = State()
    waiting_disliked = State()


class DietFormStates(StatesGroup):
    choosing_diet = State()
    choosing_goal = State()
    choosing_days = State()


class SettingsStates(StatesGroup):
    waiting_allergies = State()
    waiting_disliked = State()
    waiting_reminder_time = State()
