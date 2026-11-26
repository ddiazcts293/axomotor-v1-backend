from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from core.config import settings
from schemas.token import TokenCreate

password_context = CryptContext(
    schemes=[settings.HASHING_ALGORITHM],
    deprecated="auto",
)

def get_password_hash(password: str) -> str:
    return password_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return password_context.verify(password, hashed_password)

def create_token_pair(username, role, token_version: int = 1) -> TokenCreate:
    now = datetime.now(timezone.utc)

    access_payload = {
        "sub": username,
        "role": role,
        "type": "access",
        "ver": token_version,
        "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    refresh_payload = {
        "sub": username,
        "type": "refresh",
        "ver": token_version,
        "exp": now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    }

    return TokenCreate(
        access_token=jwt.encode(access_payload, settings.SECRET_KEY, algorithm=settings.TOKEN_ALGORITHM),
        refresh_token=jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm=settings.TOKEN_ALGORITHM),
        token_type="bearer"
    )
