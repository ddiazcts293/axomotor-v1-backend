from typing import Optional
from uuid import UUID
from datetime import datetime

from pydantic import Field
from sqlmodel import SQLModel

from models.enums import VehicleServiceStatus
from schemas.user import UserResponseShort
from schemas.vehicle import VehicleResponseShort

class VehicleServiceCreate(SQLModel):
    vehicle_id: UUID = Field(description="UUID del vehículo al que se realizó el servicio.")
    name: str = Field(max_length=60, description="Nombre del servicio de mantenimiento.")
    description: Optional[str] = Field(default=None, max_length=500, description="Detalle del trabajo realizado.")
    status: VehicleServiceStatus = Field(default=VehicleServiceStatus.pending, description="Estado del servicio; por defecto PENDING.")
    date: datetime = Field(description="Fecha y hora en que se realizó el servicio.")
    next_service_date: Optional[datetime] = Field(default=None, description="Fecha recomendada para el siguiente servicio.")

class VehicleServiceUpdate(SQLModel):
    name: Optional[str] = Field(default=None, max_length=60, description="Nuevo nombre del servicio.")
    description: Optional[str] = Field(default=None, max_length=500, description="Nueva descripción del trabajo.")
    status: Optional[VehicleServiceStatus] = Field(default=None, description="Nuevo estado del servicio.")
    date: Optional[datetime] = Field(default=None, description="Nueva fecha y hora de realización.")
    next_service_date: Optional[datetime] = Field(default=None, description="Nueva fecha recomendada para el siguiente servicio.")

class VehicleServiceResponse(SQLModel):
    service_id: UUID = Field(description="Identificador único del servicio.")
    vehicle_id: UUID = Field(description="Identificador del vehículo.")
    name: str = Field(max_length=60, description="Nombre del servicio.")
    description: Optional[str] = Field(max_length=500, description="Descripción del trabajo.")
    status: VehicleServiceStatus = Field(description="Estado actual del servicio.")
    date: datetime = Field(description="Fecha y hora de realización.")
    next_service_date: Optional[datetime] = Field(default=None, description="Fecha recomendada para el siguiente servicio.")
    registered_at: datetime = Field(description="Fecha y hora de registro.")
    updated_at: Optional[datetime] = Field(default=None, description="Fecha y hora de la última actualización.")
    created_by_id: UUID = Field(description="Identificador del usuario que registró el servicio.")
    authorized_by_id: Optional[UUID] = Field(default=None, description="Identificador del usuario que lo autorizó al completarse.")

    model_config = {"from_attributes": True}

class VehicleServiceResponseExtended(VehicleServiceResponse):
    created_by: UserResponseShort = Field(description="Usuario que registró el servicio.")
    authorized_by: Optional[UserResponseShort] = Field(description="Usuario que autorizó su finalización, si aplica.")
    vehicle: VehicleResponseShort = Field(description="Resumen del vehículo asociado.")
