from fastapi import HTTPException, status

from app.core.config import settings


def verify_api_key(x_api_key: str | None) -> None:
    if not settings.api_key_enabled:
        return
    if not x_api_key or x_api_key != settings.api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key inválida")
