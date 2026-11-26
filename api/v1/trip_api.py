from datetime import datetime, timezone
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response, status
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
from models import Driver, KnownLocation, Trip, User, Vehicle
from models.enums import TripStatus
from schemas.trip import (
    TripCreate,
    TripResponse,
    TripResponseExtended,
    TripUpdate,
)

router = APIRouter()

CONFLICT_DETAIL = "The trip could not be saved due to a conflicting or invalid reference"
FINISHED_STATUSES = {TripStatus.finished, TripStatus.cancelled, TripStatus.aborted}


def _check_references(session: Session, trip_data: TripCreate | TripUpdate) -> None:
    references = (
        ("vehicle_id", Vehicle, "Vehicle"),
        ("driver_id", Driver, "Driver"),
        ("origin_id", KnownLocation, "Origin location"),
        ("destination_id", KnownLocation, "Destination location"),
    )
    for field, model, name in references:
        value = getattr(trip_data, field, None)
        if value is not None:
            get_or_404(session, model, value, name)


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _check_dates(departure: datetime, arrive: Optional[datetime]) -> None:
    if arrive is not None and _as_utc(arrive) < _as_utc(departure):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="arrive_date cannot be earlier than departure_date",
        )


def _stamp_status_timestamps(trip: Trip, previous_status: Optional[TripStatus]) -> None:
    if trip.status == previous_status:
        return

    now = datetime.now(timezone.utc)
    if trip.status == TripStatus.on_route and trip.started_at is None:
        trip.started_at = now
    if trip.status in FINISHED_STATUSES and trip.finished_at is None:
        trip.finished_at = now


@router.post(
    "/",
    response_model=TripResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Programar viaje",
    description="Crea un viaje con referencias existentes; la fecha estimada de llegada no puede ser anterior a la salida.",
)
def register_trip(
    trip_data: TripCreate,
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_user),
) -> Trip:
    _check_references(session, trip_data)
    _check_dates(trip_data.departure_date, trip_data.arrive_date)

    trip = Trip(**trip_data.model_dump())
    _stamp_status_timestamps(trip, None)

    session.add(trip)
    commit_or_409(session, CONFLICT_DETAIL)
    session.refresh(trip)
    return trip


@router.get(
    "/",
    response_model=list[TripResponse],
    summary="Listar viajes",
    description="Devuelve viajes paginados, ordenados por salida, con filtros por vehículo, conductor, ubicaciones, estado y fechas.",
)
def get_trips(
    response: Response,
    page: PaginationDep,
    vehicle_id: Optional[UUID] = Query(default=None, description="Filtra por UUID del vehículo asignado."),
    driver_id: Optional[UUID] = Query(default=None, description="Filtra por UUID del conductor asignado."),
    origin_id: Optional[UUID] = Query(default=None, description="Filtra por UUID de la ubicación de origen."),
    destination_id: Optional[UUID] = Query(default=None, description="Filtra por UUID de la ubicación de destino."),
    trip_status: Optional[TripStatus] = Query(default=None, alias="status", description="Filtra por estado del viaje."),
    from_date: Optional[datetime] = Query(default=None, description="Fecha mínima de salida, inclusive."),
    to_date: Optional[datetime] = Query(default=None, description="Fecha máxima de salida, inclusive."),
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_user),
) -> list[Trip]:
    statement = select(Trip)

    if vehicle_id is not None:
        statement = statement.where(Trip.vehicle_id == vehicle_id)
    if driver_id is not None:
        statement = statement.where(Trip.driver_id == driver_id)
    if origin_id is not None:
        statement = statement.where(Trip.origin_id == origin_id)
    if destination_id is not None:
        statement = statement.where(Trip.destination_id == destination_id)
    if trip_status is not None:
        statement = statement.where(Trip.status == trip_status)
    if from_date is not None:
        statement = statement.where(Trip.departure_date >= from_date)
    if to_date is not None:
        statement = statement.where(Trip.departure_date <= to_date)

    statement = statement \
        .order_by(col(Trip.departure_date).desc()) \
        .options(
            joinedload(Trip.driver),
            joinedload(Trip.vehicle),
            joinedload(Trip.origin),
            joinedload(Trip.destination),
        )

    return paginate(session, statement, page, response)


@router.get(
    "/{trip_id}",
    response_model=TripResponseExtended,
    summary="Consultar viaje",
    description="Obtiene el detalle del viaje con datos ampliados del vehículo y conductor.",
)
def get_trip(
    trip_id: Annotated[UUID, Path(description="UUID del viaje.")],
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_user),
) -> Trip:
    statement = (
        select(Trip)
        .where(Trip.trip_id == trip_id)
        .options(
            joinedload(Trip.vehicle),
            joinedload(Trip.driver).joinedload(Driver.user),
            joinedload(Trip.origin),
            joinedload(Trip.destination),
        )
    )

    trip = session.exec(statement).first()

    if trip is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        )
    return trip


@router.put(
    "/{trip_id}",
    response_model=TripResponse,
    summary="Actualizar viaje",
    description="Actualiza datos o estado del viaje y registra automáticamente sus fechas de inicio o cierre cuando corresponda.",
)
def update_trip(
    trip_id: Annotated[UUID, Path(description="UUID del viaje que se desea actualizar.")],
    trip_data: TripUpdate,
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_user),
) -> Trip:
    trip = get_or_404(session, Trip, trip_id, "Trip")

    _check_references(session, trip_data)

    previous_status = trip.status
    apply_update(trip, trip_data)
    _check_dates(trip.departure_date, trip.arrive_date)
    _stamp_status_timestamps(trip, previous_status)

    session.add(trip)
    commit_or_409(session, CONFLICT_DETAIL)
    session.refresh(trip)
    return trip
