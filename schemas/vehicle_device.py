from typing import Optional
from uuid import UUID
from datetime import datetime

from pydantic import Field
from sqlmodel import SQLModel

from models.enums import VehicleDeviceType

class VehicleDeviceCreate(SQLModel):
    vehicle_id: UUID = Field(description="UUID del vehículo donde se instala el dispositivo.")
    serial_number: str = Field(min_length=12, max_length=12, description="Número de serie único de exactamente 12 caracteres.")
    tag: str = Field(max_length=16, description="Etiqueta visible asignada al dispositivo.")
    type: VehicleDeviceType = Field(description="Tipo de dispositivo: HUB o NODE.")
    is_enabled: bool = Field(default=True, description="Indica si el dispositivo queda habilitado; por defecto true.")

class VehicleDeviceUpdate(SQLModel):
    vehicle_id: Optional[UUID] = Field(default=None, description="UUID del nuevo vehículo asociado.")
    serial_number: Optional[str] = Field(default=None, min_length=12, max_length=12, description="Nuevo número de serie único de exactamente 12 caracteres.")
    tag: Optional[str] = Field(default=None, max_length=16, description="Nueva etiqueta visible.")
    type: Optional[VehicleDeviceType] = Field(default=None, description="Nuevo tipo: HUB o NODE.")
    is_enabled: Optional[bool] = Field(default=None, description="Habilita o deshabilita el dispositivo.")

class VehicleDeviceResponse(SQLModel):
    device_id: UUID = Field(description="Identificador único del dispositivo.")
    vehicle_id: UUID = Field(description="Identificador del vehículo asociado.")
    serial_number: str = Field(max_length=12, description="Número de serie.")
    tag: str = Field(max_length=16, description="Etiqueta visible.")
    type: VehicleDeviceType = Field(description="Tipo de dispositivo: HUB o NODE.")
    battery_level: Optional[int] = Field(default=None, description="Nivel de batería, si está disponible.")
    is_active: bool = Field(description="Indica si el dispositivo está activo.")
    is_enabled: bool = Field(description="Indica si el dispositivo está habilitado.")
    registered_at: datetime = Field(description="Fecha y hora de registro.")
    updated_at: Optional[datetime] = Field(default=None, description="Fecha y hora de la última actualización.")

    model_config = {"from_attributes": True}
