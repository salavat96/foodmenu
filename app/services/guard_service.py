from __future__ import annotations

import re
import time
from collections import defaultdict, deque

# Ключевые слова, по которым сообщение считается "по теме" бота
# (еда, рецепты, меню, диеты, настройки). Список специально с запасом —
# лучше пропустить пограничное сообщение в обработчик, чем ошибочно
# отбить релевантный запрос пользователя.
TOPIC_KEYWORDS = [
    "рецепт", "готов", "блюдо", "еда", "продукт", "ингредиент",
    "завтрак", "обед", "ужин", "перекус", "меню", "план питания",
    "диет", "похуде", "вес", "калори", "белк", "углевод", "жир",
    "аллерг", "не люблю", "бюджет", "напомин", "настройк",
    "готовить", "приготов", "кухня", "порци", "вкус",
]

_KEYWORD_PATTERN = re.compile("|".join(TOPIC_KEYWORDS), re.IGNORECASE)


def is_on_topic(text: str) -> bool:
    text = (text or "").strip()
    if not text:
        return False
    # Короткие сообщения (например, название продукта или блюда одним словом)
    # намеренно пропускаем — их отфильтрует сам поиск рецептов.
    if len(text.split()) <= 3:
        return True
    return bool(_KEYWORD_PATTERN.search(text))


class RateLimiter:
    """Простой rate limit в памяти: не больше `max_messages` за `period` секунд."""

    def __init__(self, max_messages: int = 5, period: float = 10.0) -> None:
        self.max_messages = max_messages
        self.period = period
        self._history: dict[int, deque[float]] = defaultdict(deque)

    def is_allowed(self, user_id: int) -> bool:
        now = time.monotonic()
        history = self._history[user_id]

        while history and now - history[0] > self.period:
            history.popleft()

        if len(history) >= self.max_messages:
            return False

        history.append(now)
        return True
