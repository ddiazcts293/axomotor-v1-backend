from uuid import UUID
from typing import Annotated, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from sqlmodel import Session, select, col
from geoalchemy2.elements import WKTElement

from api.v1.common import (
    PaginationDep,
    apply_update,
    commit_or_409,
    get_or_404,
    paginate
)
from api.v1.dependencies import get_current_user, verify_mqtt_consumer
from db.database import get_session
from models import (
    Vehicle,
    User,
    VehicleEvent,
    EventCode,
    VehicleType,
    VehicleStatus,
)
from schemas.vehicle import VehicleCreate, VehicleUpdate, VehicleResponse
from schemas.vehicle_event import VehicleEventCreate, VehicleEventResponse

router = APIRouter()

CONFLICT_DETAIL = "The vehicle could not be saved due to a conflicting or invalid reference"
EVENT_CONFLICT_DETAIL = "The event could not be saved due to a conflicting or invalid reference"

@router.post(
    "/",
    response_model=VehicleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar vehículo",
    description="Crea un vehículo; placas, número de registro y VIN no deben estar registrados previamente.",
)
def register_vehicle(
    vehicle_data: VehicleCreate,
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_user),
) -> Vehicle:
    existing_vehicle = session.exec(
        select(Vehicle).where(
            (Vehicle.plate_number == vehicle_data.plate_number) |
            (Vehicle.reg_number == vehicle_data.reg_number) |
            (Vehicle.series_vin == vehicle_data.series_vin)
        )
    ).first()

    if existing_vehicle:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=CONFLICT_DETAIL
        )

    data = vehicle_data.model_dump(exclude_none=True)
    vehicle = Vehicle(**data)

    session.add(vehicle)
    commit_or_409(session, CONFLICT_DETAIL)
    session.refresh(vehicle)
    return vehicle

@router.get(
    "/",
    response_model=list[VehicleResponse],
    summary="Listar vehículos",
    description="Devuelve vehículos paginados y permite filtrar por identificadores, datos descriptivos, tipo y estado.",
)
def get_vehicles(
    response: Response,
    page: PaginationDep,
    plate_number: Optional[str] = Query(default=None, description="Filtra por placas exactas."),
    reg_number: Optional[str] = Query(default=None, description="Filtra por número de registro exacto."),
    series_vin: Optional[str] = Query(default=None, description="Filtra por VIN exacto."),
    brand: Optional[str] = Query(default=None, description="Filtra por marca exacta."),
    model: Optional[str] = Query(default=None, description="Filtra por modelo exacto."),
    year: Optional[int] = Query(default=None, description="Filtra por año de fabricación."),
    vehicle_type: Optional[VehicleType] = Query(default=None, description="Filtra por tipo de vehículo."),
    status: Optional[VehicleStatus] = Query(default=None, description="Filtra por estado operativo."),
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_user),
) -> list[Vehicle]:
    statement = select(Vehicle)

    if plate_number is not None:
        statement = statement.where(Vehicle.plate_number == plate_number)
    if reg_number is not None:
        statement = statement.where(Vehicle.reg_number == reg_number)
    if series_vin is not None:
        statement = statement.where(Vehicle.series_vin == series_vin)
    if brand is not None:
        statement = statement.where(Vehicle.brand == brand)
    if model is not None:
        statement = statement.where(Vehicle.model == model)
    if year is not None:
        statement = statement.where(Vehicle.year == year)
    if vehicle_type is not None:
        statement = statement.where(Vehicle.type == vehicle_type)
    if status is not None:
        statement = statement.where(Vehicle.status == status)

    return paginate(session, statement, page, response)

@router.get(
    "/{vehicle_id}",
    response_model=VehicleResponse,
    summary="Consultar vehículo",
    description="Obtiene los datos de un vehículo por UUID.",
)
def get_vehicle(
    vehicle_id: Annotated[UUID, Path(description="UUID del vehículo.")],
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_user),
) -> Vehicle:
    return get_or_404(session, Vehicle, vehicle_id, "Vehicle")

@router.put(
    "/{vehicle_id}",
    response_model=VehicleResponse,
    summary="Actualizar vehículo",
    description="Actualiza los campos proporcionados del vehículo.",
)
def update_vehicle(
    vehicle_id: Annotated[UUID, Path(description="UUID del vehículo que se desea actualizar.")],
    vehicle_data: VehicleUpdate,
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_user),
) -> Vehicle:
    vehicle = get_or_404(session, Vehicle, vehicle_id, "Vehicle")

    apply_update(vehicle, vehicle_data)
    session.add(vehicle)
    commit_or_409(session, CONFLICT_DETAIL)
    session.refresh(vehicle)
    return vehicle

@router.get(
    "/{vehicle_id}/events",
    response_model=list[VehicleEventResponse],
    summary="Listar eventos del vehículo",
    description="Devuelve eventos paginados del vehículo; permite filtrar por código y rango de registro.",
)
def get_events(
    response: Response,
    page: PaginationDep,
    vehicle_id: Annotated[UUID, Path(description="UUID del vehículo cuyos eventos se consultan.")],
    code: Optional[str] = Query(default=None, description="Filtra por código de evento."),
    from_date: Optional[datetime] = Query(default=None, description="Fecha y hora mínima de registro, inclusive."),
    to_date: Optional[datetime] = Query(default=None, description="Fecha y hora máxima de registro, inclusive."),
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_user),
) -> list[VehicleEvent]:
    statement = select(VehicleEvent) \
        .where(VehicleEvent.vehicle_id == vehicle_id) \
        .options(joinedload(VehicleEvent.info)) # type: ignore

    if code is not None:
        statement = statement.where(VehicleEvent.code == code)
    if from_date is not None:
        statement = statement.where(VehicleEvent.registered_at >= from_date)
    if to_date is not None:
        statement = statement.where(VehicleEvent.registered_at <= to_date)

    statement = statement.order_by(col(VehicleEvent.registered_at).desc())
    return paginate(session, statement, page, response)

@router.post(
    "/{vehicle_id}/events",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(verify_mqtt_consumer)],
    summary="Registrar evento del vehículo",
    description="Recibe un evento de un consumidor MQTT autenticado mediante API key y devuelve 204 sin contenido.",
)
def create_event(
    vehicle_id: Annotated[UUID, Path(description="UUID del vehículo que generó el evento.")],
    event_data: VehicleEventCreate,
    session: Session = Depends(get_session),
):
    get_or_404(session, Vehicle, vehicle_id, "Vehicle")
    get_or_404(session, EventCode, event_data.code, "Event Code")

    event = VehicleEvent(
        code = event_data.code,
        vehicle_id = vehicle_id,
        additional_data=event_data.additional_data
    )

    if event_data.has_position:
        position_wkt = f"POINT({event_data.longitude} {event_data.latitude})"
        event.position=WKTElement(position_wkt, srid=4326)

    session.add(event)
    commit_or_409(session, EVENT_CONFLICT_DETAIL)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
