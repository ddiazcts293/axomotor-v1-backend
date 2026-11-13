import uuid
from datetime import datetime, timezone
from typing import Optional, List, Any, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship, Column
from geoalchemy2 import Geometry

if TYPE_CHECKING:
    from models.trip import Trip

class KnownLocation(SQLModel, table=True):
    __tablename__ = 'known_locations'

    location_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(index=True, unique=True, min_length=1, max_length=60)
    type: Optional[str] = Field(default=None, max_length=40)
    address: str = Field(index=True, max_length=240)
    # Se usa sa_column para definir el tipo espacial de PostGIS
    location_area: Any = Field(sa_column=Column(Geometry('POLYGON', srid=4326)))
    registered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    trip_origins: List['Trip'] = Relationship(
        back_populates='origin',
        sa_relationship_kwargs={'cascade': 'all, delete-orphan'}
    )
    trip_destinations: List['Trip'] = Relationship(
        back_populates='destination',
        sa_relationship_kwargs={'cascade': 'all, delete-orphan'}
    )
