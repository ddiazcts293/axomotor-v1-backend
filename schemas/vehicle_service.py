from typing import Optional
from uuid import UUID
from datetime import datetime

from pydantic import Field
from sqlmodel import SQLModel

from models.enums import VehicleServiceStatus
from schemas.user import UserResponseShort

class VehicleServiceCreate(SQLModel):
    vehicle_id: UUID
    name: str = Field(max_length=60)
    description: Optional[str] = Field(default=None, max_length=500)
    status: VehicleServiceStatus = Field(default=VehicleServiceStatus.pending)
    date: datetime
    next_service_date: Optional[datetime] = Field(default=None)

class VehicleServiceUpdate(SQLModel):
    name: Optional[str] = Field(default=None, max_length=60)
    description: Optional[str] = Field(default=None, max_length=500)
    status: Optional[VehicleServiceStatus] = Field(default=None)
    date: Optional[datetime] = Field(default=None)
    next_service_date: Optional[datetime] = Field(default=None)

class VehicleServiceResponse(SQLModel):
    service_id: UUID
    vehicle_id: UUID
    name: str = Field(max_length=60)
    description: Optional[str] = Field(max_length=500)
    status: VehicleServiceStatus
    date: datetime
    next_service_date: Optional[datetime] = None
    registered_at: datetime
    updated_at: Optional[datetime] = None
    created_by_id: UUID
    authorized_by_id: Optional[UUID] = None

    model_config = {"from_attributes": True}

class VehicleServiceResponseExtended(VehicleServiceResponse):
    created_by: UserResponseShort
    authorized_by: Optional[UserResponseShort]
