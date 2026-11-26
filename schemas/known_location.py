from typing import Optional, Any, List, Dict
from uuid import UUID
from datetime import datetime

from pydantic import Field, computed_field, field_validator
from sqlmodel import SQLModel
from geoalchemy2.shape import to_shape
from shapely.geometry import Polygon, mapping
from shapely.validation import explain_validity

def validate_spatial_poligon(vertices: List[List[float]]) -> List[List[float]]:
    # 1. Verificar formato y rangos geográficos de cada vértice
    for vertex in vertices:
        if len(vertex) != 2:
            raise ValueError("Each vertex must contain exactly [longitude, latitude]")
        lon, lat = vertex
        if not (-180.0 <= lon <= 180.0) or not (-90.0 <= lat <= 90.0):
            raise ValueError(f"Vertex outside the geographic range: [{lon}, {lat}]")

    # 2. Verificar que el anillo esté cerrado (primer punto == último punto)[cite: 3]
    if vertices[0] != vertices[-1]:
        raise ValueError(
            "The polygon must be closed: the first and last coordinates must be identical"
        )

    # 3. Validar integridad topológica con Shapely (evita auto-intersecciones / moños)
    polygon = Polygon(vertices)
    if not polygon.is_valid:
        reason = explain_validity(polygon)
        raise ValueError(f"Invalid polygon geometry: {reason}")

    if polygon.area == 0:
        raise ValueError("A polygon cannot have an area of zero (collinear vertices).")

    return vertices

class KnownLocationCreate(SQLModel):
    name: str = Field(min_length=1, max_length=60)
    type: Optional[str] = Field(default=None, max_length=40)
    address: str = Field(max_length=240)
    location_area: List[List[float]] = Field(
        min_length=4,
        description="Vertices list [longitude, latitude]"
    )

    @field_validator("location_area", mode="after")
    @classmethod
    def validate_location_area(cls, vertices: List[List[float]]) -> List[List[float]]:
        return validate_spatial_poligon(vertices)

class KnownLocationUpdate(SQLModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=60)
    type: Optional[str] = Field(default=None, max_length=40)
    address: Optional[str] = Field(default=None, max_length=240)
    location_area: Optional[List[List[float]]] = Field(
        default=None,
        min_length=4,
        description="Vertices list [longitude, latitude]"
    )

    @field_validator("location_area", mode="after")
    @classmethod
    def validate_location_area(
        cls, vertices: Optional[List[List[float]]]
    ) -> Optional[List[List[float]]]:
        return validate_spatial_poligon(vertices) if vertices is not None else None

class KnownLocationResponse(SQLModel):
    location_id: UUID
    name: str = Field(max_length=60)
    type: Optional[str] = Field(default=None, max_length=40)
    address: str = Field(max_length=240)
    location_area: Any = Field(exclude=True)
    registered_at: datetime

    @computed_field
    @property
    def geojson(self) -> Dict[str, Any]:
        polygon = to_shape(self.location_area)
        return mapping(polygon)

class KnownLocationResponseShort(SQLModel):
    name: str = Field(max_length=60)
    type: Optional[str] = Field(default=None, max_length=40)
    address: str = Field(max_length=240)
