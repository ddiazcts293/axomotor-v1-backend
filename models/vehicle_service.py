import uuid
from datetime import datetime, date, timezone
from typing import Optional, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship
from models.enums import VehicleServiceStatus

if TYPE_CHECKING:
    from models.vehicle import Vehicle
    from models.user import User

class VehicleService(SQLModel, table=True):
    __tablename__ = 'vehicle_services'

    service_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    vehicle_id: uuid.UUID = Field(foreign_key='vehicles.vehicle_id', index=True)
    status: VehicleServiceStatus = Field(default=VehicleServiceStatus.pending)
    date: datetime
    next_service_date: Optional[datetime] = None
    created_by_id: uuid.UUID = Field(foreign_key='users.user_id', index=True)
    authorized_by_id: Optional[uuid.UUID] = Field(default=None, foreign_key='users.user_id', index=True)
    registered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    vehicle: Optional['Vehicle'] = Relationship(back_populates='services')
    created_by: Optional['User'] = Relationship(back_populates='vehicle_services_created')
    authorized_by: Optional['User'] = Relationship(back_populates='vehicle_services_authorized')
