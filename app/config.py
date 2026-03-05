from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "FinTrack API"
    app_env: str = "development"
    app_port: int = 8000
    app_host: str = "0.0.0.0"
    debug: bool = True

    database_url: str = "postgresql+asyncpg://fintrack:fintrack123@localhost:5432/fintrack_db"
    redis_url: str = "redis://localhost:6379/0"

    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    openai_api_key: str = ""

    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""

    rate_limit_per_minute: int = 60
    frontend_url: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
