import hmac

from fastapi import HTTPException, status

from app.core.config import settings
from app.core.error_messages import ErrorMessage


def verify_api_key(x_api_key: str | None) -> None:
    """Verify the API key when enabled.

    Raises:
        HTTPException(401): When API key is enabled and missing/invalid.
    """
    if not settings.api_key_enabled:
        return
    if not x_api_key or not hmac.compare_digest(x_api_key, settings.api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ErrorMessage.API_KEY_INVALID,
        )
