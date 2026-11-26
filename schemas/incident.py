from typing import Optional, Any, Dict
from uuid import UUID
from datetime import datetime

from geoalchemy2.shape import to_shape
from shapely.geometry import mapping
from pydantic import Field, computed_field
from sqlmodel import SQLModel

from models.enums import IncidentStatus, PriorityLevel
from schemas.position import PositionCreateBase
from schemas.event_code import EventCodeResponse
from schemas.user import UserResponse, UserResponseShort
from schemas.trip import TripResponse
from schemas.incident_media import IncidentMediaResponse

class IncidentCreate(PositionCreateBase):
    trip_id: UUID
    code: str = Field(max_length=12)
    status: Optional[IncidentStatus] = Field(default=IncidentStatus.open)
    description: str = Field(min_length=2, max_length=500)
    comments: Optional[str] = Field(default=None, min_length=2, max_length=500)
    related_incident_id: Optional[UUID] = Field(default=None)

class IncidentUpdate(SQLModel):
    code: Optional[str] = Field(default=None, max_length=12)
    priority: Optional[PriorityLevel] = Field(default=None)
    status: Optional[IncidentStatus] = Field(default=None)
    description: Optional[str] = Field(default=None, min_length=2, max_length=500)
    comments: Optional[str] = Field(default=None, min_length=2, max_length=500)
    related_incident_id: Optional[UUID] = Field(default=None)

class IncidentResponse(SQLModel):
    incident_id: UUID
    trip_id: UUID
    code: str = Field(exclude=True)
    info: EventCodeResponse
    position: Any = Field(exclude=True)
    priority: PriorityLevel
    status: IncidentStatus
    description: str = Field(max_length=500)
    comments: Optional[str] = Field(default=None, max_length=500)
    related_incident_id: Optional[UUID]
    registered_at: datetime
    reviewed_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    created_by_id: Optional[UUID] = None
    reviewed_by_id: Optional[UUID] = None

    @computed_field
    @property
    def geojson(self) -> Optional[Dict[str, Any]]:
        if self.position:
            point = to_shape(self.position)
            return mapping(point)
        else:
            return None

class IncidentResponseExtended(IncidentResponse):
    trip: TripResponse
    created_by: Optional[UserResponse]
    reviewed_by: Optional[UserResponseShort]
    media_files: list[IncidentMediaResponse]
