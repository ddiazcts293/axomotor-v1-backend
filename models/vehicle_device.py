import uuid
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship
from models.enums import VehicleDeviceType

if TYPE_CHECKING:
    from models.vehicle import Vehicle

class VehicleDevice(SQLModel, table=True):
    __tablename__ = 'vehicle_devices'

    device_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    vehicle_id: uuid.UUID = Field(foreign_key='vehicles.vehicle_id', index=True)
    serial_number: str = Field(index=True, unique=True, max_length=12)
    tag: str = Field(index=True, max_length=16)
    type: VehicleDeviceType
    battery_level: Optional[int] = None
    is_active: bool
    is_enabled: bool = Field(default=True)
    registered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    vehicle: Optional['Vehicle'] = Relationship(back_populates='devices')
