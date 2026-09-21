from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, TelegramObject

from app.keyboards.common import MAIN_MENU_KEYBOARD
from app.services.guard_service import RateLimiter, is_on_topic
from app.utils.texts import OFF_TOPIC_TEXT, RATE_LIMIT_TEXT


class AntiSpamMiddleware(BaseMiddleware):
    """Отсекает флуд и сообщения не по теме бота.

    Пропускает без проверки: команды и любые сообщения, когда пользователь
    находится в активном FSM-состоянии (там ожидается конкретный свободный
    текст — например, список аллергий или время напоминания).
    """

    def __init__(self, max_messages: int = 5, period: float = 10.0) -> None:
        self._rate_limiter = RateLimiter(max_messages=max_messages, period=period)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message) or not event.text:
            return await handler(event, data)

        user_id = event.from_user.id if event.from_user else None
        if user_id is not None and not self._rate_limiter.is_allowed(user_id):
            await event.answer(RATE_LIMIT_TEXT)
            return None

        if event.text.startswith("/"):
            return await handler(event, data)

        state: FSMContext | None = data.get("state")
        if state is not None and await state.get_state() is not None:
            return await handler(event, data)

        if not is_on_topic(event.text):
            await event.answer(OFF_TOPIC_TEXT, reply_markup=MAIN_MENU_KEYBOARD)
            return None

        return await handler(event, data)
