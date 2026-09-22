from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    bot_token: str
    database_url: str = "sqlite+aiosqlite:///./foodmenu.db"
    default_timezone: str = "Europe/Moscow"

    anthropic_api_key: str | None = None
    ai_model: str = "claude-haiku-4-5"
    ai_max_concurrent_requests: int = 5
    ai_daily_limit_per_user: int = 10


settings = Settings()
