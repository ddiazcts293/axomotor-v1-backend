from typing import Optional, Any, Dict
from uuid import UUID
from datetime import datetime

from geoalchemy2.shape import to_shape
from shapely.geometry import mapping
from pydantic import Field, computed_field
from sqlmodel import SQLModel

from schemas.position import PositionCreateBase
from schemas.event_code import EventCodeResponse

class VehicleEventCreate(PositionCreateBase):
    code: str = Field(max_length=12, description="Código habilitado del catálogo que identifica el evento.")
    additional_data: Optional[Dict[str, Any]] = Field(default=None, description="Datos complementarios del dispositivo en formato JSON.")

class VehicleEventResponse(SQLModel):
    event_id: UUID = Field(description="Identificador único del evento.")
    vehicle_id: UUID = Field(description="Identificador del vehículo que generó el evento.")
    code: str = Field(exclude=True, description="Código interno del catálogo; se expone mediante info.")
    info: EventCodeResponse = Field(description="Descripción, categoría y severidad del código.")
    position: Any = Field(exclude=True, description="Geometría interna; se representa como geojson.")
    additional_data: Optional[Dict[str, Any]] = Field(default=None, description="Datos complementarios recibidos.")
    registered_at: datetime = Field(description="Fecha y hora en que se registró el evento.")

    @computed_field(description="Geometría GeoJSON Point de la ubicación, o null si no se registraron coordenadas.")
    @property
    def geojson(self) -> Optional[Dict[str, Any]]:
        if self.position:
            point = to_shape(self.position)
            return mapping(point)
        else:
            return None
