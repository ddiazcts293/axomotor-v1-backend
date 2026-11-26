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
    vehicle_id: UUID = Field(description="UUID del vehículo asignado.")
    driver_id: UUID = Field(description="UUID del perfil de conductor asignado.")
    origin_id: UUID = Field(description="UUID de la ubicación conocida de origen.")
    destination_id: UUID = Field(description="UUID de la ubicación conocida de destino.")
    departure_date: datetime = Field(description="Fecha y hora programada de salida.")
    arrive_date: Optional[datetime] = Field(default=None, description="Fecha y hora estimada de llegada; no puede ser anterior a la salida.")
    status: TripStatus = Field(default=TripStatus.planned, description="Estado del viaje; por defecto PLANNED.")

class TripUpdate(SQLModel):
    vehicle_id: Optional[UUID] = Field(default=None, description="Nuevo UUID de vehículo.")
    driver_id: Optional[UUID] = Field(default=None, description="Nuevo UUID de conductor.")
    origin_id: Optional[UUID] = Field(default=None, description="Nuevo UUID de ubicación de origen.")
    destination_id: Optional[UUID] = Field(default=None, description="Nuevo UUID de ubicación de destino.")
    departure_date: Optional[datetime] = Field(default=None, description="Nueva fecha y hora de salida.")
    arrive_date: Optional[datetime] = Field(default=None, description="Nueva fecha y hora estimada de llegada.")
    status: Optional[TripStatus] = Field(default=None, description="Nuevo estado del viaje.")

class TripResponse(SQLModel):
    trip_id: UUID = Field(description="Identificador único del viaje.")
    vehicle_id: UUID = Field(description="Identificador del vehículo asignado.")
    driver_id: UUID = Field(description="Identificador del conductor asignado.")
    origin_id: UUID = Field(description="Identificador de la ubicación de origen.")
    destination_id: UUID = Field(description="Identificador de la ubicación de destino.")
    departure_date: datetime = Field(description="Fecha y hora programada de salida.")
    arrive_date: Optional[datetime] = Field(default=None, description="Fecha y hora estimada de llegada.")
    status: TripStatus = Field(description="Estado actual del viaje.")
    distance: Optional[Decimal] = Field(default=None, description="Distancia registrada en kilómetros.")
    average_speed: Optional[Decimal] = Field(default=None, description="Velocidad promedio registrada en km/h.")
    created_at: datetime = Field(description="Fecha y hora de creación del viaje.")
    started_at: Optional[datetime] = Field(default=None, description="Fecha y hora real de inicio.")
    finished_at: Optional[datetime] = Field(default=None, description="Fecha y hora de finalización.")

    vehicle: VehicleResponseShort = Field(description="Resumen del vehículo asignado.")
    driver: DriverResponseShort = Field(description="Resumen del conductor asignado.")
    origin: KnownLocationResponseShort = Field(description="Resumen de la ubicación de origen.")
    destination: KnownLocationResponseShort = Field(description="Resumen de la ubicación de destino.")

    model_config = {"from_attributes": True}

class TripResponseExtended(TripResponse):
    vehicle: VehicleResponse = Field(description="Datos completos del vehículo asignado.")
    driver: DriverResponse = Field(description="Datos completos del conductor asignado.")
