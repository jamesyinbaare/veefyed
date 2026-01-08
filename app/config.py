from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = ""
    storage_backend: str = "local"  # local, s3, azure
    storage_path: str = "storage/images"
    storage_max_size: int = 5 * 1024 * 1024  # 5MB max file size


class LoggingSettings(BaseSettings):
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "text"  # "text" or "json"
    ENV: str = "dev"  # dev | staging | prod

    class Config:
        env_prefix = "APP_"


logging_settings = LoggingSettings()  # type: ignore

settings = Settings()  # type: ignore
