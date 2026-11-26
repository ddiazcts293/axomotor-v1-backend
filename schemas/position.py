from uuid import UUID
from datetime import datetime
from typing import Optional, Any, Dict
import json

from sqlmodel import SQLModel
from pydantic import Field, field_validator, model_validator, computed_field

class PositionCreateBase(SQLModel):
    latitude: Optional[float] = Field(default=None, ge=-90.0, le=90.0, description="Latitud WGS 84 entre -90 y 90; envíese junto con longitude.")
    longitude: Optional[float] = Field(default=None, ge=-180.0, le=180.0, description="Longitud WGS 84 entre -180 y 180; envíese junto con latitude.")

    @model_validator(mode="after")
    def validate_coordinates(self) -> "PositionCreateBase":
        if ([self.latitude, self.longitude].count(None) == 1) or \
            (self.latitude == 0.0 and self.longitude == 0.0):
            raise ValueError("Invalid GPS coordinates")
        return self

    @computed_field(description="Indica si se enviaron ambas coordenadas y se puede construir una posición.")
    @property
    def has_position(self) -> bool:
        return self.latitude is not None and self.longitude is not None

class PositionResponse(SQLModel):
    position_id: UUID = Field(description="Identificador único de la posición registrada.")
    vehicle_id: UUID = Field(description="Identificador del vehículo.")
    trip_id: Optional[UUID] = Field(description="Viaje al que pertenece la posición, si se asoció.")
    geojson: Dict[str, Any] = Field(description="Geometría GeoJSON Point con coordenadas [longitud, latitud].")
    speed: float = Field(description="Velocidad instantánea en km/h.")
    registered_at: datetime = Field(description="Fecha y hora de captura de la posición.")

    @field_validator("geojson", mode="before")
    @classmethod
    def parse_geojson(cls, v: Any) -> Dict[str, Any]:
        return json.loads(v) if isinstance(v, str) else v

class RouteResponse(SQLModel):
    vehicle_id: UUID = Field(description="Identificador del vehículo.")
    trip_id: Optional[UUID] = Field(description="Viaje al que pertenece la ruta, si se asoció.")
    geojson: Dict[str, Any] = Field(description="Geometría GeoJSON LineString; los puntos pueden simplificarse.")
    point_count: int = Field(description="Cantidad de posiciones originales usadas para construir la ruta.")
    render_point_count: int = Field(description="Cantidad de vértices en la geometría devuelta.")
    distance: float = Field(description="Distancia total en metros.")
    average_speed: float = Field(description="Velocidad promedio en km/h.")
    started_at: datetime = Field(description="Fecha y hora de la primera posición del grupo.")
    finished_at: datetime = Field(description="Fecha y hora de la última posición del grupo.")

    @field_validator("geojson", mode="before")
    @classmethod
    def parse_geojson(cls, v: Any) -> Dict[str, Any]:
        return json.loads(v) if isinstance(v, str) else v

    @field_validator("distance", mode="before")
    @classmethod
    def parse_distance(cls, v: Any) -> float:
        return round(v, 2)
