from datetime import UTC, datetime, timedelta
from typing import Any

from jose import jwt

from app.core.config import settings


def create_access_token(data: dict[str, Any]) -> str:
    to_encode: dict[str, Any] = data.copy()
    expire: datetime = datetime.now(UTC) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire, "sub": "access"})
    encoded_jwt: str = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def encode_token(token: str) -> dict[str, Any]:
    return jwt.decode(
        token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
    )
