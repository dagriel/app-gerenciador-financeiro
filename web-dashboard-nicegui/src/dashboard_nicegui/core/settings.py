from __future__ import annotations

from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Config do Dashboard (NiceGUI).

    Carrega variáveis de ambiente (e .env local) para manter o projeto
    reprodutível, sem hardcode de segredos/URLs no código.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    fin_api_base_url: HttpUrl = Field(alias="FIN_API_BASE_URL")
    fin_api_key: str = Field(alias="FIN_API_KEY", min_length=1)

    dashboard_port: int = Field(default=8081, alias="DASHBOARD_PORT", ge=1, le=65535)

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
