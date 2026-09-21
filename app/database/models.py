from __future__ import annotations

import enum
from datetime import date, datetime, time

from sqlalchemy import (
    JSON,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Time,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class MealType(str, enum.Enum):
    breakfast = "breakfast"
    lunch = "lunch"
    dinner = "dinner"


class DietType(str, enum.Enum):
    regular = "regular"
    low_carb = "low_carb"
    keto = "keto"
    vegetarian = "vegetarian"
    vegan = "vegan"
    high_protein = "high_protein"
    mediterranean = "mediterranean"


class BudgetLevel(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Goal(str, enum.Enum):
    lose_weight = "lose_weight"
    maintain = "maintain"
    gain_weight = "gain_weight"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    allergies: Mapped[list[str]] = mapped_column(JSON, default=list)
    disliked_products: Mapped[list[str]] = mapped_column(JSON, default=list)

    diet_type: Mapped[DietType] = mapped_column(Enum(DietType), default=DietType.regular)
    goal: Mapped[Goal] = mapped_column(Enum(Goal), default=Goal.maintain)
    budget_level: Mapped[BudgetLevel] = mapped_column(Enum(BudgetLevel), default=BudgetLevel.medium)
    timezone: Mapped[str] = mapped_column(String(64), default="Europe/Moscow")

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    reminder_settings: Mapped[list["ReminderSetting"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    menu_plans: Mapped[list["MenuPlan"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    meal_type: Mapped[MealType] = mapped_column(Enum(MealType))
    diet_tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    allergens: Mapped[list[str]] = mapped_column(JSON, default=list)
    budget_level: Mapped[BudgetLevel] = mapped_column(Enum(BudgetLevel), default=BudgetLevel.medium)

    calories: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cook_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    servings: Mapped[int] = mapped_column(Integer, default=2)

    ingredients: Mapped[list["Ingredient"]] = relationship(
        back_populates="recipe", cascade="all, delete-orphan", order_by="Ingredient.order_index"
    )
    steps: Mapped[list["RecipeStep"]] = relationship(
        back_populates="recipe", cascade="all, delete-orphan", order_by="RecipeStep.step_number"
    )


class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"))
    name: Mapped[str] = mapped_column(String(255))
    amount: Mapped[str] = mapped_column(String(64))
    order_index: Mapped[int] = mapped_column(Integer, default=0)

    recipe: Mapped[Recipe] = relationship(back_populates="ingredients")


class RecipeStep(Base):
    __tablename__ = "recipe_steps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"))
    step_number: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(String(1024))
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    recipe: Mapped[Recipe] = relationship(back_populates="steps")


class MenuPlan(Base):
    __tablename__ = "menu_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    budget_level: Mapped[BudgetLevel] = mapped_column(Enum(BudgetLevel))
    diet_type: Mapped[DietType] = mapped_column(Enum(DietType))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped[User] = relationship(back_populates="menu_plans")
    entries: Mapped[list["MenuEntry"]] = relationship(
        back_populates="menu_plan", cascade="all, delete-orphan", order_by="MenuEntry.entry_date"
    )


class MenuEntry(Base):
    __tablename__ = "menu_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    menu_plan_id: Mapped[int] = mapped_column(ForeignKey("menu_plans.id"))
    entry_date: Mapped[date] = mapped_column(Date)
    meal_type: Mapped[MealType] = mapped_column(Enum(MealType))
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"))

    menu_plan: Mapped[MenuPlan] = relationship(back_populates="entries")
    recipe: Mapped[Recipe] = relationship()


class ReminderSetting(Base):
    __tablename__ = "reminder_settings"
    __table_args__ = (UniqueConstraint("user_id", "meal_type", name="uq_reminder_user_meal"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    meal_type: Mapped[MealType] = mapped_column(Enum(MealType))
    remind_at: Mapped[time] = mapped_column(Time)
    enabled: Mapped[bool] = mapped_column(default=True)

    user: Mapped[User] = relationship(back_populates="reminder_settings")
