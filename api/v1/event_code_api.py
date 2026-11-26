from typing import Optional

from fastapi import APIRouter, Depends, Response
from sqlmodel import Session, col, select

from api.v1.common import PaginationDep, paginate
from api.v1.dependencies import get_current_user
from db.database import get_session
from models import EventCode, User
from models.enums import SeverityLevel, EventCategory, EventType
from schemas.event_code import EventCodeResponse

router = APIRouter()

@router.get("/", response_model=list[EventCodeResponse])
def get_incident_codes(
    severity: Optional[SeverityLevel] = None,
    category: Optional[EventCategory] = None,
    type: Optional[EventType] = None,
    is_enabled: Optional[bool] = None,
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
