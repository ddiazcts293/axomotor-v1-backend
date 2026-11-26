from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import joinedload
from sqlmodel import Session, col, select

from api.v1.common import (
    PaginationDep,
    apply_update,
    commit_or_409,
    get_or_404,
    paginate,
)
from api.v1.dependencies import get_current_user
from db.database import get_session
from models import User, Vehicle, VehicleService
from models.enums import VehicleServiceStatus
from schemas.vehicle_service import (
    VehicleServiceCreate,
    VehicleServiceResponse,
    VehicleServiceResponseExtended,
    VehicleServiceUpdate,
)

router = APIRouter()

CONFLICT_DETAIL = "The service could not be saved due to a conflicting or invalid reference"


@router.post(
    "/",
    response_model=VehicleServiceResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_service(
    service_data: VehicleServiceCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> VehicleService:
    get_or_404(session, Vehicle, service_data.vehicle_id, "Vehicle")

    service = VehicleService(
        **service_data.model_dump(),
        created_by_id=current_user.user_id,
    )
    if service.status == VehicleServiceStatus.completed:
        service.authorized_by_id = current_user.user_id

    session.add(service)
    commit_or_409(session, CONFLICT_DETAIL)
    session.refresh(service)
    return service


@router.get("/", response_model=list[VehicleServiceResponse])
def get_services(
    response: Response,
    page: PaginationDep,
    vehicle_id: Optional[UUID] = None,
    service_status: Optional[VehicleServiceStatus] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_user),
) -> list[VehicleService]:
    statement = select(VehicleService)

    if vehicle_id is not None:
        statement = statement.where(VehicleService.vehicle_id == vehicle_id)
    if service_status is not None:
        statement = statement.where(VehicleService.status == service_status)
    if from_date is not None:
        statement = statement.where(VehicleService.date >= from_date)
    if to_date is not None:
        statement = statement.where(VehicleService.date <= to_date)

    statement = statement.order_by(col(VehicleService.date).desc())
    return paginate(session, statement, page, response)


@router.get("/{service_id}", response_model=VehicleServiceResponseExtended)
def get_service(
    service_id: UUID,
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_user),
) -> VehicleService:
    statement = (
        select(VehicleService)
        .where(VehicleService.service_id == service_id)
        .options(
            joinedload(VehicleService.vehicle),
            joinedload(VehicleService.created_by),
            joinedload(VehicleService.authorized_by),
        )
    )

    service = session.exec(statement).first()

    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found",
        )
    return service


@router.put("/{service_id}", response_model=VehicleServiceResponse)
def update_service(
    service_id: UUID,
    service_data: VehicleServiceUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> VehicleService:
    service = get_or_404(session, VehicleService, service_id, "Service")

    previous_status = service.status
    apply_update(service, service_data)

    if (
        service.status == VehicleServiceStatus.completed
        and previous_status != VehicleServiceStatus.completed
    ):
        service.authorized_by_id = current_user.user_id

    session.add(service)
    commit_or_409(session, CONFLICT_DETAIL)
    session.refresh(service)
    return service
