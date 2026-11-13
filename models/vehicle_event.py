import uuid
from datetime import datetime, timezone
from typing import Optional, Any, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from geoalchemy2 import Geography

if TYPE_CHECKING:
    from models.codes import VehicleEventCode
    from models.vehicle import Vehicle

class VehicleEvent(SQLModel, table=True):
    __tablename__ = 'vehicle_events'

    event_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    vehicle_id: uuid.UUID = Field(foreign_key='vehicles.vehicle_id', index=True)
    code: str = Field(foreign_key='vehicle_event_codes.code', index=True, max_length=12)
    # Se usa sa_column para definir el tipo espacial de PostGIS
    position: Any = Field(sa_column=Column(Geography('POINT', srid=4326)))
    additional_data: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    registered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    vehicle: Optional['Vehicle'] = Relationship(back_populates='devices')
    info: Optional['VehicleEventCode'] = Relationship(back_populates='events')
