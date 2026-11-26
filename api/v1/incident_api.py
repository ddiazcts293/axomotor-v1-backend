from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from geoalchemy2.elements import WKTElement
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
from models import (
    Incident,
    EventCode,
    Trip,
    User,
    IncidentStatus,
    PriorityLevel,
)
from schemas.incident import (
    IncidentCreate,
    IncidentResponse,
    IncidentResponseExtended,
    IncidentUpdate,
)

router = APIRouter()

CONFLICT_DETAIL = "The incident could not be saved due to a conflicting or invalid reference"
CLOSING_STATUSES = {IncidentStatus.closed, IncidentStatus.discarded}


def _stamp_status_timestamps(
    incident: Incident, previous_status: Optional[IncidentStatus]
) -> None:
    if incident.status == previous_status:
        return

    now = datetime.now(timezone.utc)
    if incident.status != IncidentStatus.open and incident.reviewed_at is None:
        incident.reviewed_at = now
    if incident.status in CLOSING_STATUSES and incident.closed_at is None:
        incident.closed_at = now


@router.post(
    "/",
    response_model=IncidentResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_incident(
    incident_data: IncidentCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Incident:
    get_or_404(session, Trip, incident_data.trip_id, "Trip")
    get_or_404(session, EventCode, incident_data.code, "Incident code")
    if incident_data.related_incident_id is not None:
        get_or_404(session, Incident, incident_data.related_incident_id, "Related incident")

    data = incident_data.model_dump(
        exclude={"latitude", "longitude", "has_position"},
        exclude_none=True,
    )
    if incident_data.has_position:
        data["position"] = WKTElement(
            f"POINT({incident_data.longitude} {incident_data.latitude})",
            srid=4326,
        )

    incident = Incident(**data, created_by_id=current_user.user_id)

    _stamp_status_timestamps(incident, None)
    if incident.reviewed_at is not None:
        incident.reviewed_by_id = current_user.user_id

    session.add(incident)
    commit_or_409(session, CONFLICT_DETAIL)
    session.refresh(incident)
    return incident


@router.get("/", response_model=list[IncidentResponse])
def get_incidents(
    response: Response,
    page: PaginationDep,
    trip_id: Optional[UUID] = None,
    code: Optional[str] = None,
    incident_status: Optional[IncidentStatus] = Query(default=None, alias="status"),
    priority: Optional[PriorityLevel] = None,
    created_by_id: Optional[UUID] = None,
    reviewed_by_id: Optional[UUID] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_user),
) -> list[Incident]:
    statement = select(Incident)

    if trip_id is not None:
        statement = statement.where(Incident.trip_id == trip_id)
    if code is not None:
        statement = statement.where(Incident.code == code)
    if incident_status is not None:
        statement = statement.where(Incident.status == incident_status)
    if priority is not None:
        statement = statement.where(Incident.priority == priority)
    if created_by_id is not None:
        statement = statement.where(Incident.created_by_id == created_by_id)
    if reviewed_by_id is not None:
        statement = statement.where(Incident.reviewed_by_id == reviewed_by_id)
    if from_date is not None:
        statement = statement.where(Incident.registered_at >= from_date)
    if to_date is not None:
        statement = statement.where(Incident.registered_at <= to_date)

    statement = statement.order_by(col(Incident.registered_at).desc())
    return paginate(session, statement, page, response)


@router.get("/{incident_id}", response_model=IncidentResponseExtended)
def get_incident(
    incident_id: UUID,
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_user),
) -> Incident:
    statement = (
        select(Incident)
        .where(Incident.incident_id == incident_id)
        .options(
            joinedload(Incident.info),
            joinedload(Incident.trip),
            joinedload(Incident.created_by),
            joinedload(Incident.reviewed_by),
            joinedload(Incident.media_files),
        )
    )

    incident = session.exec(statement).first()

    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found",
        )
    return incident


@router.put("/{incident_id}", response_model=IncidentResponse)
def update_incident(
    incident_id: UUID,
    incident_data: IncidentUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Incident:
    incident = get_or_404(session, Incident, incident_id, "Incident")

    if incident_data.code is not None:
        get_or_404(session, EventCode, incident_data.code, "Incident code")
    if incident_data.related_incident_id is not None:
        if incident_data.related_incident_id == incident_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="An incident cannot be related to itself",
            )
        get_or_404(session, Incident, incident_data.related_incident_id, "Related incident")

    previous_status = incident.status
    apply_update(incident, incident_data)
    _stamp_status_timestamps(incident, previous_status)
    incident.reviewed_by_id = current_user.user_id

    session.add(incident)
    commit_or_409(session, CONFLICT_DETAIL)
    session.refresh(incident)
    return incident
