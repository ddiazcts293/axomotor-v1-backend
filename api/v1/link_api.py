from datetime import timedelta
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from api.v1.dependencies import get_current_user
from db.database import get_session
from models import Driver, User, UserRole, LinkingToken
from schemas.driver import DriverResponse, DriverLink, LinkCreateResponse

router = APIRouter()

@router.post(
    "/",
    response_model=LinkCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear token de vinculación",
    description="Emite para el conductor autenticado un token temporal y la URL para iniciar la vinculación con Telegram.",
)
def create_link(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> LinkingToken:
    driver = session.exec(
        select(Driver).where(Driver.user_id == current_user.user_id)
    ).first()

    if current_user.role != UserRole.driver or driver is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must be registered as driver",
        )

    token = LinkingToken(driver_id=driver.driver_id)
    session.add(token)

    try:
        session.commit()
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot create linking token: {e}",
        ) from None

    session.refresh(token)
    return token

@router.put(
    "/",
    response_model=DriverResponse,
    summary="Vincular cuenta de Telegram",
    description="Canjea un token de vinculación vigente y guarda el identificador de Telegram en el perfil del conductor.",
)
def link_driver(
    user_data: DriverLink,
    session: Session = Depends(get_session)
) -> Driver:
    linking_token = session.get(LinkingToken, user_data.token)

    if linking_token is None or not linking_token.is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Linking token invalid or expired",
        )

    driver = session.get(Driver, linking_token.driver_id)
    if driver is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found",
        )

    driver.telegram_user_id = user_data.telegram_user_id

    session.add(driver)
    session.delete(linking_token)

    try:
        session.commit()
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot link Telegram user with the driver",
        ) from None

    session.refresh(driver)
    return driver
