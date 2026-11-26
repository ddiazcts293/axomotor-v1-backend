import uuid
from datetime import datetime, timezone
from typing import Optional, List, Any, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship, Column
from geoalchemy2 import Geography
from models.enums import IncidentStatus, PriorityLevel

if TYPE_CHECKING:
    from models.trip import Trip
    from models.user import User
    from models.event_code import EventCode
    from models.incident_media_file import IncidentMediaFile

class Incident(SQLModel, table=True):
    __tablename__ = 'incidents'

    incident_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    trip_id: uuid.UUID = Field(foreign_key='trips.trip_id', index=True)
    code: str = Field(foreign_key='event_codes.code', max_length=12)
    priority: PriorityLevel = Field(default=PriorityLevel.medium)
    status: IncidentStatus = Field(default=IncidentStatus.open)
    # Se usa sa_column para definir el tipo espacial de PostGIS
    position: Optional[Any] = Field(default=None, sa_column=Column(Geography('POINT', srid=4326)))
    description: str = Field(min_length=2, max_length=500)
    comments: Optional[str] = Field(default=None, min_length=2, max_length=500)
    related_incident_id: Optional[uuid.UUID] = Field(default=None, foreign_key='incidents.incident_id', index=True)
    registered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    reviewed_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    created_by_id: Optional[uuid.UUID] = Field(default=None, foreign_key='users.user_id', index=True)
    reviewed_by_id: Optional[uuid.UUID] = Field(default=None, foreign_key='users.user_id', index=True)

    related_incident: Optional['Incident'] = Relationship(
        back_populates='subsequent_incident',
        sa_relationship_kwargs={'remote_side': '[Incident.incident_id]'}
    )
    subsequent_incident: Optional['Incident'] = Relationship(
        back_populates='related_incident'
    )
    trip: Optional['Trip'] = Relationship(back_populates='incidents')
    info: Optional['EventCode'] = Relationship(back_populates='incidents')
    created_by: Optional['User'] = Relationship(
        back_populates='incidents_created',
        sa_relationship_kwargs={'foreign_keys': '[Incident.created_by_id]'}
    )
    reviewed_by: Optional['User'] = Relationship(
        back_populates='incidents_reviewed',
        sa_relationship_kwargs={'foreign_keys': '[Incident.reviewed_by_id]'}
    )
    media_files: List['IncidentMediaFile'] = Relationship(
        back_populates='incident',
        sa_relationship_kwargs={'cascade': 'all, delete-orphan'}
    )
