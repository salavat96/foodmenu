from __future__ import annotations

import logging
from datetime import date, datetime

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.database.repo import get_menu_entry_for_date, list_due_reminders
from app.database.session import session_scope
from app.utils.texts import MEAL_TYPE_LABELS

logger = logging.getLogger(__name__)


async def _send_due_reminders(bot: Bot) -> None:
    now = datetime.now().time().replace(second=0, microsecond=0)

    async with session_scope() as session:
        due = await list_due_reminders(session, now)
        for setting in due:
            user = setting.user
            entry = await get_menu_entry_for_date(session, user, date.today(), setting.meal_type)
            label = MEAL_TYPE_LABELS[setting.meal_type.value]

            if entry:
                text = f"⏰ Время: {label}!\nСегодня по меню: <b>{entry.recipe.title}</b>"
            else:
                text = (
                    f"⏰ Время: {label}!\n"
                    "Меню на сегодня ещё не составлено — загляни в раздел «Меню на неделю/две»."
                )

            try:
                await bot.send_message(user.telegram_id, text)
            except Exception:  # noqa: BLE001 - недоставленное напоминание не должно рушить job
                logger.exception("Не удалось отправить напоминание пользователю %s", user.telegram_id)


def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(_send_due_reminders, "cron", second=0, args=[bot], id="send_due_reminders")
    return scheduler
