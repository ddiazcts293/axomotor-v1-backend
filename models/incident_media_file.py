import uuid
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from models.enums import MediaType

if TYPE_CHECKING:
    from models.incident import Incident
    from models.user import User

class IncidentMediaFile(SQLModel, table=True):
    __tablename__ = 'incident_media_files'

    file_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    incident_id: uuid.UUID = Field(foreign_key='incidents.incident_id', index=True)
    object_key: str
    type: MediaType
    file_metadata: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    uploaded_by_id: uuid.UUID = Field(foreign_key="users.user_id", index=True)

    incident: Optional['Incident'] = Relationship(back_populates='media_files')
    uploaded_by: Optional['User'] = Relationship(back_populates='media_files')
