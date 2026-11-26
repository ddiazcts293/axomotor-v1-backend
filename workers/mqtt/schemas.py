from datetime import datetime
from decimal import Decimal
from uuid import UUID
from typing import Optional, Any, Dict

from pydantic import BaseModel, Field, model_validator, computed_field

class EventBase(BaseModel):
    latitude: Optional[float] = Field(default=None, ge=-90.0, le=90.0, description="Latitud WGS 84; debe enviarse junto con longitude.")
    longitude: Optional[float] = Field(default=None, ge=-180.0, le=180.0, description="Longitud WGS 84; debe enviarse junto con latitude.")
    registered_at: datetime = Field(description="Fecha y hora de generación del mensaje.")

    @model_validator(mode="after")
    def validate_coordinates(self) -> "EventBase":
        if ([self.latitude, self.longitude].count(None) == 1) or \
            (self.latitude == 0.0 and self.longitude == 0.0):
            raise ValueError("Invalid GPS coordinates")
        return self

    @computed_field(description="Indica si el mensaje incluye las dos coordenadas GPS.")
    @property
    def has_position(self) -> bool:
        return self.latitude is not None and self.longitude is not None

class VehicleEventCreate(EventBase):
    code: str = Field(max_length=12, description="Código de evento existente en el catálogo.")
    additional_data: Optional[Dict[str, Any]] = Field(default=None, description="Información complementaria del dispositivo.")

class PositionCreate(EventBase):
    trip_id: Optional[UUID] = Field(description="UUID del viaje asociado, si corresponde.")
    speed: Decimal = Field(default=Decimal(0), ge=0.0, le=300.0, description="Velocidad del vehículo en km/h, entre 0 y 300.")

class IncidentCreate(EventBase):
    trip_id: UUID = Field(description="UUID del viaje en el que ocurrió el incidente.")
    code: str = Field(max_length=12, description="Código de incidente existente en el catálogo.")
    description: str = Field(min_length=2, max_length=500, description="Descripción de lo ocurrido, entre 2 y 500 caracteres.")
