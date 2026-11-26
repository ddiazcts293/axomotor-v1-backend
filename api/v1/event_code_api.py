from typing import Optional

from fastapi import APIRouter, Depends, Query, Response
from sqlmodel import Session, col, select

from api.v1.common import PaginationDep, paginate
from api.v1.dependencies import get_current_user
from db.database import get_session
from models import EventCode, User
from models.enums import SeverityLevel, EventCategory, EventType
from schemas.event_code import EventCodeResponse

router = APIRouter()

@router.get(
    "/",
    response_model=list[EventCodeResponse],
    summary="Consultar catálogo de códigos",
    description="Lista códigos de eventos e incidentes; admite filtros por severidad, categoría, tipo y habilitación.",
)
def get_incident_codes(
    severity: Optional[SeverityLevel] = Query(default=None, description="Filtra por severidad del código."),
    category: Optional[EventCategory] = Query(default=None, description="Filtra por categoría del evento."),
    type: Optional[EventType] = Query(default=None, description="Filtra por tipo VEHICLE, INCIDENT o BOTH."),
    is_enabled: Optional[bool] = Query(default=None, description="Filtra códigos habilitados o deshabilitados."),
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_user),
) -> list[EventCode]:
    statement = select(EventCode)

    if severity is not None:
        statement = statement.where(EventCode.severity == severity)
    if category is not None:
        statement = statement.where(EventCode.category == category)
    if type is not None:
        statement = statement.where(EventCode.type == type)
    if is_enabled is not None:
        statement = statement.where(EventCode.is_enabled == is_enabled)

    statement = statement.order_by(
        col(EventCode.type).asc(),
        col(EventCode.category).asc(),
    )

    return list(session.exec(statement).all())
