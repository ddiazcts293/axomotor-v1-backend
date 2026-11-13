import uuid
from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from models.enums import MediaType

if TYPE_CHECKING:
    from models.incident import Incident

class IncidentMedia(SQLModel, table=True):
    __tablename__ = 'incident_media'

    media_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    incident_id: uuid.UUID = Field(foreign_key='incidents.incident_id', index=True)
    file_url: str = Field(max_length=240)
    type: MediaType
    file_metadata: dict = Field(default=None, sa_column=Column(JSON))
    captured_at: datetime
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    incident: Optional['Incident'] = Relationship(back_populates='media_files')
