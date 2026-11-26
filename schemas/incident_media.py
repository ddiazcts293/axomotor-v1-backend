from typing import Optional, Any, Dict
from uuid import UUID
from datetime import datetime

from pydantic import Field, computed_field
from sqlmodel import SQLModel

from core.storage import generate_download_url
from models.enums import MediaType
from schemas.user import UserResponseShort

class IncidentMediaResponse(SQLModel):
    file_id: UUID = Field(description="Identificador único del archivo multimedia.")
    incident_id: UUID = Field(description="Incidente al que pertenece el archivo.")
    object_key: str = Field(exclude=True, description="Clave interna de almacenamiento; no se expone en la respuesta.")
    type: MediaType = Field(description="Tipo de archivo: IMAGE o VIDEO.")
    file_metadata: Optional[Dict[str, Any]] = Field(description="Metadatos opcionales del archivo.")
    uploaded_at: datetime = Field(description="Fecha y hora de carga al servidor.")
    uploaded_by_id: UUID = Field(description="Identificador del usuario que cargó el archivo.")
    uploaded_by: UserResponseShort = Field(description="Datos resumidos del usuario que cargó el archivo.")

    model_config = {"from_attributes": True}

    @computed_field(description="URL temporal de descarga generada para el archivo almacenado.")
    @property
    def file_url(self) -> str:
        return generate_download_url(self.object_key)
