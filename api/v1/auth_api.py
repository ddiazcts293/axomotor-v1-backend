from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from api.v1.dependencies import get_current_user, verify_token
from core.security import create_token_pair, get_password_hash, verify_password
from db.database import get_session
from models import User
from schemas.token import TokenCreate, TokenRefresh
from schemas.user import UserUpdatePassword

router = APIRouter()

@router.post("/token", response_model=TokenCreate)
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_session),
) -> TokenCreate:
    user = session.exec(
        select(User).where(
            (User.username == form_data.username) |
            (User.email == form_data.username) |
            (User.phone_number == form_data.username)
        )
    ).first()

    if user is None or not verify_password(
        form_data.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    return create_token_pair(user.username, user.role)

@router.post("/refresh", response_model=TokenCreate)
def refresh_token(
    form_data: TokenRefresh,
    session: Session = Depends(get_session),
) -> TokenCreate:
    payload = verify_token(form_data.refresh_token, "refresh")
    username = payload["sub"]

    user = session.exec(
        select(User).where(User.username == username)
    ).first()

    if user is None or not user.is_enabled:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is inactive or does not exist",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return create_token_pair(user.username, user.role)

@router.put("/change_password", status_code=status.HTTP_204_NO_CONTENT)
def update_password(
    form_data: UserUpdatePassword,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> None:
    if not verify_password(form_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Current password is incorrect",
        )

    current_user.hashed_password = get_password_hash(form_data.new_password)
    session.add(current_user)

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot update password",
        ) from None
