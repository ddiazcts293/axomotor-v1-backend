from uuid import UUID
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response, status
from sqlalchemy import func
from sqlalchemy.orm import joinedload, contains_eager
from sqlmodel import Session, select, col

from api.v1.common import (
    PaginationDep,
    apply_update,
    commit_or_409,
    get_or_404,
    paginate
)
from api.v1.dependencies import get_current_user
from db.database import get_session
from models import Driver, User, UserRole, LicenseClass
from schemas.driver import (
    DriverCreate,
    DriverUpdate,
    DriverResponse
)

router = APIRouter()

CONFLICT_DETAIL = "The driver could not be saved due to a conflicting or invalid reference"

@router.post(
    "/",
    response_model=DriverResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar conductor",
    description="Crea un perfil de conductor para un usuario existente cuyo rol sea DRIVER.",
)
def register_driver(
    driver_data: DriverCreate,
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_user),
) -> Driver:
    user = get_or_404(session, User, driver_data.user_id, "User")
    if user.role != UserRole.driver:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must be registered as driver",
        )

    data = driver_data.model_dump(exclude_none=True)
    driver = Driver(**data)

    session.add(driver)
    commit_or_409(session, CONFLICT_DETAIL)
    session.refresh(driver)
    return driver

@router.get(
    "/",
    response_model=list[DriverResponse],
    summary="Listar conductores",
    description="Devuelve conductores paginados; permite filtrar por usuario, clase de licencia y estados.",
)
def get_drivers(
    response: Response,
    page: PaginationDep,
    user_id: Optional[UUID] = Query(default=None, description="Filtra por UUID del usuario asociado."),
    license_class: Optional[LicenseClass] = Query(default=None, description="Filtra por clase de licencia."),
    is_active: Optional[bool] = Query(default=None, description="Filtra por estado activo del perfil."),
    is_enabled: Optional[bool] = Query(default=None, description="Filtra por habilitación del conductor."),
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_user),
) -> list[Driver]:
    statement = select(Driver)

    if user_id is not None:
        statement = statement.where(Driver.user_id == user_id)
    if license_class is not None:
        statement = statement.where(Driver.license_class == license_class)
    if is_active is not None:
        statement = statement.where(Driver.is_active == is_active)
    if is_enabled is not None:
        statement = statement.where(Driver.is_enabled == is_enabled)

    statement = statement \
        .outerjoin(Driver.user) \
        .options(contains_eager(Driver.user)) \
        .order_by(
            func.lower(User.first_name).asc(),
            func.lower(User.last_name).asc().nulls_last(),
        )

    return paginate(session, statement, page, response)

@router.get(
    "/{driver_id}",
    response_model=DriverResponse,
    summary="Consultar conductor",
    description="Obtiene un perfil de conductor y el resumen del usuario asociado por UUID.",
)
def get_driver(
    driver_id: Annotated[UUID, Path(description="UUID del perfil de conductor.")],
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_user),
) -> Driver:
    statement = (
        select(Driver)
            .where(Driver.driver_id == driver_id)
            .options(joinedload(Driver.user))  # type: ignore
    )

    driver = session.exec(statement).first()

    if driver is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found",
        )
    return driver

@router.put(
    "/{driver_id}",
    response_model=DriverResponse,
    summary="Actualizar conductor",
    description="Actualiza los datos de licencia o la habilitación del conductor.",
)
def update_driver(
    driver_id: Annotated[UUID, Path(description="UUID del perfil de conductor que se desea actualizar.")],
    driver_data: DriverUpdate,
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_user),
) -> Driver:
    driver = get_or_404(session, Driver, driver_id, "Driver")

    apply_update(driver, driver_data)
    session.add(driver)
    commit_or_409(session, CONFLICT_DETAIL)
    session.refresh(driver)
    return driver
