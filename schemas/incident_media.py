from typing import Optional, Any, Dict
from uuid import UUID
from datetime import datetime

from pydantic import Field, computed_field
from sqlmodel import SQLModel

from core.storage import generate_download_url
from models.enums import MediaType
from schemas.user import UserResponseShort

class IncidentMediaResponse(SQLModel):
    file_id: UUID
    incident_id: UUID
    object_key: str = Field(exclude=True)
    type: MediaType
    file_metadata: Optional[Dict[str, Any]]
    uploaded_at: datetime
    uploaded_by_id: UUID
    uploaded_by: UserResponseShort

    model_config = {"from_attributes": True}

    @computed_field
    @property
    def file_url(self) -> str:
        return generate_download_url(self.object_key)
