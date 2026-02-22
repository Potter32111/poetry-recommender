from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    database_url: str = "postgresql+asyncpg://poetry:poetry_secret_123@db:5432/poetry_bot"
    google_api_key: str = ""
    debug: bool = False

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
