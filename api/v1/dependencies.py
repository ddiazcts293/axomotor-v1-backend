import secrets
from typing import Annotated

from fastapi import Depends, Header, Security, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from jose import JWTError, jwt
from sqlmodel import Session, select

from core.config import settings
from db.database import get_session
from models import User, UserRole, Driver

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/token",
    refreshUrl="/api/v1/auth/refresh",
)
mqtt_consumer_key_header = APIKeyHeader(name="X-MQTT-Consumer-API-Key", auto_error=False)
bot_key_header = APIKeyHeader(name="X-Bot-API-Key", auto_error=False)

def verify_mqtt_consumer(
    api_key: Annotated[str | None, Security(mqtt_consumer_key_header)]
) -> bool:
    if not api_key or settings.X_MQTT_CONSUMER_API_KEY is None or \
        not secrets.compare_digest(api_key, settings.X_MQTT_CONSUMER_API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate API Key"
        )

    return True

def verify_bot(
    api_key: Annotated[str | None, Security(bot_key_header)]
) -> bool:
    if not api_key or settings.X_BOT_API_KEY is None or \
        secrets.compare_digest(api_key, settings.X_BOT_API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate API Key"
        )

    return True

def verify_token(token: str, expected_type: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.TOKEN_ALGORITHM],
        )
        if payload.get("type") != expected_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token type, expected: '{expected_type}'",
                headers={"WWW-Authenticate": "Bearer"},
            )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload

def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.TOKEN_ALGORITHM],
        )
        username = payload.get("sub")
        if not isinstance(username, str) or not username:
            raise credentials_exception
    except JWTError:
        raise credentials_exception from None

    user = session.exec(
        select(User).where(User.username == username)
    ).first()

    if user is None:
        raise credentials_exception
    elif not user.is_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    return user

def get_user_from_telegram_id(
    _: Annotated[bool, Depends(verify_bot)],
    session: Annotated[Session, Depends(get_session)],
    x_telegram_user_id: Annotated[str | None, Header()] = None
) -> User:
    if not x_telegram_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing X-Telegram-User-Id header"
        )

    driver = session.exec(
        select(Driver).where(Driver.telegram_user_id == x_telegram_user_id)
    ).first()

    if not driver or not driver.user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No user is associated with this Telegram User Id"
        )

    if not driver.user.is_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    user = driver.user
    user.role = UserRole.driver
    return user

def get_web_or_bot_user(
    session: Annotated[Session, Depends(get_session)],
    token: Annotated[str | None, Depends(oauth2_scheme)] = None,
    bot_api_key: Annotated[str | None, Security(bot_key_header)] = None,
    x_telegram_user_id: Annotated[str | None, Header()] = None,
) -> User:
    # Caso A: Petición desde el servicio del Bot en nombre de un usuario
    if bot_api_key:
        verify_bot(bot_api_key)
        return get_user_from_telegram_id(True, session, x_telegram_user_id)

    # Caso B: Petición desde Web con JWT
    if token:
        return get_current_user(token, session)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials"
    )

def get_user_or_service(
    session: Annotated[Session, Depends(get_session)],
    token: Annotated[str | None, Depends(oauth2_scheme)] = None,
    mqtt_api_key: Annotated[str | None, Security(mqtt_consumer_key_header)] = None,
    bot_api_key: Annotated[str | None, Security(bot_key_header)] = None,
    x_telegram_user_id: Annotated[str | None, Header()] = None,
) -> bool | User:
    # Caso A: Petición desde el servicio MQTT Consumer
    if mqtt_api_key:
        return verify_mqtt_consumer(mqtt_api_key)

    return get_web_or_bot_user(session, token, bot_api_key, x_telegram_user_id)
