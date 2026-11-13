import uuid
from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING
from decimal import Decimal

from sqlmodel import SQLModel, Field, Relationship
from models.enums import TripStatus

if TYPE_CHECKING:
    from models.vehicle import Vehicle
    from models.driver import Driver
    from models.known_location import KnownLocation
    from models.trip_position import TripPosition

class Trip(SQLModel, table=True):
    __tablename__ = 'trips'

    trip_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    vehicle_id: uuid.UUID = Field(foreign_key='vehicles.vehicle_id', index=True)
    driver_id: uuid.UUID = Field(foreign_key='drivers.driver_id', index=True)
    origin_id: uuid.UUID = Field(foreign_key='known_locations.location_id', index=True)
    destination_id: uuid.UUID = Field(foreign_key='known_locations.location_id', index=True)
    departure_date: datetime
    arrive_date: Optional[datetime] = None
    status: TripStatus = Field(default=TripStatus.planned)
    distance: Optional[Decimal] = Field(default=None, max_digits=5, decimal_places=2)
    average_speed: Optional[Decimal] = Field(default=None, max_digits=5, decimal_places=2)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

    vehicle: Optional['Vehicle'] = Relationship(back_populates='trips')
    driver: Optional['Driver'] = Relationship(back_populates='trips')
    origin: Optional['KnownLocation'] = Relationship(back_populates='trip_origins')
    destination: Optional['KnownLocation'] = Relationship(back_populates='trip_destinations')
    positions: List['TripPosition'] = Relationship(
        back_populates='trip',
        sa_relationship_kwargs={'cascade': 'all, delete-orphan'}
    )
