from typing import Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal

from pydantic import Field
from sqlmodel import SQLModel

from models.enums import TripStatus
from schemas.vehicle import VehicleResponse, VehicleResponseShort
from schemas.known_location import KnownLocationResponseShort
from schemas.driver import DriverResponse, DriverResponseShort

class TripCreate(SQLModel):
    vehicle_id: UUID
    driver_id: UUID
    origin_id: UUID
    destination_id: UUID
    departure_date: datetime
    arrive_date: Optional[datetime] = Field(default=None)
    status: TripStatus = Field(default=TripStatus.planned)

class TripUpdate(SQLModel):
    vehicle_id: Optional[UUID] = Field(default=None)
    driver_id: Optional[UUID] = Field(default=None)
    origin_id: Optional[UUID] = Field(default=None)
    destination_id: Optional[UUID] = Field(default=None)
    departure_date: Optional[datetime] = Field(default=None)
    arrive_date: Optional[datetime] = Field(default=None)
    status: Optional[TripStatus] = Field(default=None)

class TripResponse(SQLModel):
    trip_id: UUID
    vehicle_id: UUID
    driver_id: UUID
    origin_id: UUID
    destination_id: UUID
    departure_date: datetime
    arrive_date: Optional[datetime] = None
    status: TripStatus
    distance: Optional[Decimal] = None
    average_speed: Optional[Decimal] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

    vehicle: VehicleResponseShort
    driver: DriverResponseShort
    origin: KnownLocationResponseShort
    destination: KnownLocationResponseShort

    model_config = {"from_attributes": True}

class TripResponseExtended(TripResponse):
    vehicle: VehicleResponse
    driver: DriverResponse
