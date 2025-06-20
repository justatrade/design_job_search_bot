from pydantic_settings import BaseSettings, SettingsConfigDict


class TelegramSettings(BaseSettings):
    api_id: int
    api_hash: str
    login: str
    session_dir: str = "./session"
    target_channel_id: int | None = None
    enable_filter: bool = True
    max_message_age_days: int = 1

    model_config = SettingsConfigDict(extra="ignore")


class AppSettings(BaseSettings):
    app_name: str = "Telegram Filter Bot"
    environment: str = "development"
    listen_address: str = "127.0.0.1"
    listen_port: int = 8000
    api_key: str
    db_path: str

    model_config = SettingsConfigDict(extra="ignore")


class Settings(BaseSettings):
    app: AppSettings
    telegram: TelegramSettings

    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
        extra="ignore"
    )


settings = Settings()
