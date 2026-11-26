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
    trip_id: UUID = Field(description="UUID del viaje en el que ocurrió el incidente.")
    code: str = Field(max_length=12, description="Código de incidente existente en el catálogo.")
    status: Optional[IncidentStatus] = Field(default=IncidentStatus.open, description="Estado inicial; por defecto OPEN.")
    description: str = Field(min_length=2, max_length=500, description="Descripción de lo ocurrido, entre 2 y 500 caracteres.")
    comments: Optional[str] = Field(default=None, min_length=2, max_length=500, description="Observaciones opcionales, entre 2 y 500 caracteres.")
    related_incident_id: Optional[UUID] = Field(default=None, description="UUID de otro incidente relacionado.")

class IncidentUpdate(SQLModel):
    code: Optional[str] = Field(default=None, max_length=12, description="Nuevo código de incidente.")
    priority: Optional[PriorityLevel] = Field(default=None, description="Prioridad de atención: LOW, MEDIUM o HIGH.")
    status: Optional[IncidentStatus] = Field(default=None, description="Nuevo estado: OPEN, IN_REVISION, CLOSED o DISCARDED.")
    description: Optional[str] = Field(default=None, min_length=2, max_length=500, description="Nueva descripción, entre 2 y 500 caracteres.")
    comments: Optional[str] = Field(default=None, min_length=2, max_length=500, description="Nuevas observaciones, entre 2 y 500 caracteres.")
    related_incident_id: Optional[UUID] = Field(default=None, description="UUID de otro incidente relacionado; no puede ser el propio.")

class IncidentResponse(SQLModel):
    incident_id: UUID = Field(description="Identificador único del incidente.")
    trip_id: UUID = Field(description="Identificador del viaje relacionado.")
    code: str = Field(exclude=True, description="Código interno, representado por el objeto info.")
    info: EventCodeResponse = Field(description="Datos del código de incidente.")
    position: Any = Field(exclude=True, description="Geometría interna; se expone como geojson.")
    priority: PriorityLevel = Field(description="Prioridad de atención: LOW, MEDIUM o HIGH.")
    status: IncidentStatus = Field(description="Estado actual del incidente.")
    description: str = Field(max_length=500, description="Descripción de lo ocurrido.")
    comments: Optional[str] = Field(default=None, max_length=500, description="Observaciones de seguimiento.")
    related_incident_id: Optional[UUID] = Field(description="Identificador de otro incidente relacionado, si existe.")
    registered_at: datetime = Field(description="Fecha y hora de registro.")
    reviewed_at: Optional[datetime] = Field(default=None, description="Fecha y hora de la primera revisión.")
    closed_at: Optional[datetime] = Field(default=None, description="Fecha y hora de cierre o descarte.")
    created_by_id: Optional[UUID] = Field(default=None, description="Identificador del usuario que creó el incidente; puede ser nulo.")
    reviewed_by_id: Optional[UUID] = Field(default=None, description="Identificador del usuario que lo revisó.")

    @computed_field(description="Geometría GeoJSON Point de la ubicación, o null si no se registraron coordenadas.")
    @property
    def geojson(self) -> Optional[Dict[str, Any]]:
        if self.position:
            point = to_shape(self.position)
            return mapping(point)
        else:
            return None

class IncidentResponseExtended(IncidentResponse):
    trip: TripResponse = Field(description="Resumen del viaje asociado.")
    created_by: Optional[UserResponseShort] = Field(description="Usuario creador, si existe.")
    reviewed_by: Optional[UserResponseShort] = Field(description="Usuario revisor, si existe.")
    media_files: list[IncidentMediaResponse] = Field(description="Archivos multimedia adjuntos al incidente.")
