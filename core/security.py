from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from core.config import settings

password_context = CryptContext(
    schemes=[settings.HASHING_ALGORITHM],
    deprecated="auto",
)

def get_password_hash(password: str) -> str:
    return password_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return password_context.verify(password, hashed_password)

def create_access_token(data: dict, expires_delta=None) -> str:
    payload = data.copy()
    expires_at = datetime.now(timezone.utc) + (
        expires_delta
        if expires_delta is not None
        else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload["exp"] = expires_at
    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.TOKEN_ALGORITHM,
    )
