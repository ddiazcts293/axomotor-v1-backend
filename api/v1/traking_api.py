from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, cast
from sqlmodel import Session, col, select
from geoalchemy2 import Geography, Geometry

from api.v1.dependencies import get_current_user
from db.database import get_session
from models import User, Position
from schemas.position import PositionResponse, RouteResponse

router = APIRouter()

METERS_PER_DEGREE = 111_320.0 # Standart approx WGS84 (SRID 4326)

def _solve_degree_tolerance(
    from_date: Optional[datetime],
    to_date: Optional[datetime],
    m_tolerance: Optional[float],
    auto_optimize: bool,
) -> Optional[float]:
    # 1. Prioridad a la tolerancia explícita enviada por el cliente
    if m_tolerance is not None:
        return (m_tolerance / METERS_PER_DEGREE) if m_tolerance > 0 else None

    # 2. Ajuste automático si el cliente activó auto_optimizar
    if auto_optimize and from_date and to_date:
        duracion = to_date - from_date
        if duracion > timedelta(days=7):
            return 50.0 / METERS_PER_DEGREE   # ~50m para rangos mayores a 1 semana
        if duracion > timedelta(hours=24):
            return 15.0 / METERS_PER_DEGREE   # ~15m para rangos mayores a 1 día

    return None

@router.get(
    "/positions",
    response_model=list[PositionResponse],
    summary="Consultar posiciones de vehículos",
    description="Devuelve posiciones GPS registradas y admite filtros por vehículo, viaje e intervalo de fechas.",
)
def get_positions(
    vehicle_id: Optional[UUID] = Query(
        default=None, description="Limita los resultados a este UUID de vehículo."
    ),
    trip_id: Optional[UUID] = Query(
        default=None, description="Limita los resultados a este UUID de viaje."
    ),
    from_date: Optional[datetime] = Query(
        default=None, description="Incluye posiciones registradas desde esta fecha y hora."
    ),
    to_date: Optional[datetime] = Query(
        default=None, description="Incluye posiciones registradas hasta esta fecha y hora."
    ),
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_user),
):
    statement = select(
        Position.position_id,
        Position.vehicle_id,
        Position.trip_id,
        func.ST_AsGeoJSON(Position.position).label("geojson"),
        Position.speed,
        Position.registered_at
    ) # type: ignore

    if vehicle_id is not None:
        statement = statement.where(Position.vehicle_id == vehicle_id)
    if trip_id is not None:
        statement = statement.where(Position.trip_id == trip_id)
    if from_date is not None:
        statement = statement.where(Position.registered_at >= from_date)
    if to_date is not None:
        statement = statement.where(Position.registered_at <= to_date)

    statement = statement.order_by(col(Position.registered_at).desc())
    return list(session.exec(statement).all())

@router.get(
    "/routes",
    response_model=list[RouteResponse],
    summary="Consultar rutas de vehículos",
    description="Agrupa posiciones por vehículo y viaje; solo devuelve grupos con dos o más puntos.",
)
def get_routes(
    vehicle_id: Optional[UUID] = Query(
        default=None, description="Limita los resultados a este UUID de vehículo."
    ),
    trip_id: Optional[UUID] = Query(
        default=None, description="Limita los resultados a este UUID de viaje."
    ),
    from_date: Optional[datetime] = Query(
        default=None, description="Incluye posiciones registradas desde esta fecha y hora."
    ),
    to_date: Optional[datetime] = Query(
        default=None, description="Incluye posiciones registradas hasta esta fecha y hora."
    ),
    tolerance: Optional[float] = Query(
        default=None,
        ge=0.0,
        le=1000.0,
        description="Tolerancia de simplificación geométrica en metros (0 desactiva la simplificación); rango 0–1000.",
    ),
    auto_optimize: bool = Query(
        default=False,
        description="Activa una tolerancia automática según el intervalo; se requiere from_date y to_date."
    ),
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_user),
):
    if from_date is not None and to_date is not None and to_date <= from_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="to_date must be after from_date"
        )

    deg_tolerance = _solve_degree_tolerance(
        from_date=from_date,
        to_date=to_date,
        m_tolerance=tolerance,
        auto_optimize=auto_optimize
    )

    original_line = func.ST_MakeLine(
        cast(Position.position, Geometry).op("ORDER BY")(
            col(Position.registered_at).asc()
        )
    )

    render_line = (
        func.ST_SimplifyPreserveTopology(original_line, deg_tolerance)
        if deg_tolerance is not None
        else original_line
    )

    statement = select(
        Position.vehicle_id,
        Position.trip_id,
        func.ST_AsGeoJSON(render_line).label("geojson"),
        func.count(Position.position_id).label("point_count"), # type: ignore
        func.ST_NPoints(render_line).label("render_point_count"),
        func.coalesce(
            func.ST_Length(cast(original_line, Geography)), 0.0
        ).label("distance"),
        func.round(func.avg(Position.speed), 2).label("average_speed"),
        func.min(Position.registered_at).label("started_at"),
        func.max(Position.registered_at).label("finished_at"),
    ) # type: ignore

    if from_date is not None:
        statement = statement.where(Position.registered_at >= from_date)
    if to_date is not None:
        statement = statement.where(Position.registered_at <= to_date)

    statement = statement \
        .group_by(col(Position.vehicle_id), col(Position.trip_id)) \
        .having(func.count(col(Position.position_id)) >= 2)

    if vehicle_id is not None:
        statement = statement.where(Position.vehicle_id == vehicle_id)
    if trip_id is not None:
        statement = statement.where(Position.trip_id == trip_id)

    return list(session.exec(statement).all())
