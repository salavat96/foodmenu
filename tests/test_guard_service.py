from app.services.guard_service import RateLimiter, is_on_topic


def test_on_topic_keyword_match():
    assert is_on_topic("Хочу рецепт борща на обед")
    assert is_on_topic("Составь мне меню на неделю с учётом бюджета")
    assert is_on_topic("У меня аллергия на орехи")


def test_on_topic_short_message_passes():
    assert is_on_topic("борщ")
    assert is_on_topic("курица гречка")


def test_off_topic_long_unrelated_message():
    assert not is_on_topic("расскажи анекдот про программистов пожалуйста мне скучно")


def test_off_topic_empty_message():
    assert not is_on_topic("")
    assert not is_on_topic("   ")


def test_rate_limiter_blocks_after_threshold():
    limiter = RateLimiter(max_messages=3, period=10.0)
    user_id = 1

    assert limiter.is_allowed(user_id)
    assert limiter.is_allowed(user_id)
    assert limiter.is_allowed(user_id)
    assert not limiter.is_allowed(user_id)


def test_rate_limiter_tracks_users_independently():
    limiter = RateLimiter(max_messages=1, period=10.0)

    assert limiter.is_allowed(1)
    assert not limiter.is_allowed(1)
    assert limiter.is_allowed(2)
