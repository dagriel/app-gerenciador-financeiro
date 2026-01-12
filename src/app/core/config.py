from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    database_url: str = "sqlite:///./app.db"
    api_key_enabled: bool = True
    api_key: str = "CHANGE_ME_LOCAL"
    log_level: str = "INFO"


settings = Settings()
