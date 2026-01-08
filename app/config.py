from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = ""


class LoggingSettings(BaseSettings):
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "text"  # "text" or "json"
    ENV: str = "dev"  # dev | staging | prod

    class Config:
        env_prefix = "APP_"


logging_settings = LoggingSettings()  # type: ignore

settings = Settings()  # type: ignore
