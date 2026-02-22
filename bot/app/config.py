from pydantic_settings import BaseSettings


class BotSettings(BaseSettings):
    """Bot settings loaded from environment variables."""

    telegram_bot_token: str = ""
    backend_url: str = "http://backend:8000"

    model_config = {"env_file": ".env", "extra": "ignore"}


bot_settings = BotSettings()
