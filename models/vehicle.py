import uuid
from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship
from models.enums import VehicleType, VehicleStatus

if TYPE_CHECKING:
    from models.vehicle_service import VehicleService
    from models.vehicle_device import VehicleDevice
    from models.vehicle_event import VehicleEvent
    from models.trip import Trip

class Vehicle(SQLModel, table=True):
    __tablename__ = 'vehicles'

    vehicle_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    plate_number: str = Field(index=True, unique=True, min_length=8, max_length=12)
    reg_number: str = Field(index=True, unique=True, min_length=16, max_length=22)
    series_vin: str = Field(index=True, unique=True, max_length=17)
    brand: str = Field(index=True, max_length=60)
    model: str = Field(index=True, max_length=60)
    year: int
    type: VehicleType
    axes: int = Field(default=2)
    status: VehicleStatus = Field(default=VehicleStatus.operative)
    registered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    services: List['VehicleService'] = Relationship(
        back_populates='vehicle',
        sa_relationship_kwargs={'cascade': 'all, delete-orphan'}
    )
    devices: List['VehicleDevice'] = Relationship(
        back_populates='vehicle',
        sa_relationship_kwargs={'cascade': 'all, delete-orphan'}
    )
    events: List['VehicleEvent'] = Relationship(
        back_populates='vehicle',
        sa_relationship_kwargs={'cascade': 'all, delete-orphan'}
    )
    trips: List['Trip'] = Relationship(
        back_populates='vehicle',
        sa_relationship_kwargs={'cascade': 'all, delete-orphan'}
    )
