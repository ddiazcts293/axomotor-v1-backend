from typing import Optional
from uuid import UUID
from datetime import datetime, timezone

from pydantic import Field, field_validator
from sqlmodel import SQLModel

from models.enums import VehicleType, VehicleStatus

class VehicleCreate(SQLModel):
    plate_number: str = Field(
        min_length=6,
        max_length=12,
        pattern=r"^[\d\w -]+$",
        description="Placas del vehículo; admite letras, números, espacios y guiones."
    )
    reg_number: str = Field(
        min_length=12,
        max_length=22,
        pattern=r"^\d+$",
        description="Número de registro de la tarjeta de circulación, solo dígitos."
    )
    series_vin: str = Field(
        min_length=17,
        max_length=17,
        pattern=r"^\d+$",
        description="Número de identificación vehicular (VIN), exactamente 17 dígitos."
    )
    brand: str = Field(min_length=1, max_length=60, description="Marca del vehículo.")
    model: str = Field(min_length=1, max_length=60, description="Modelo del vehículo.")
    year: int = Field(gt=1900, le=datetime.now(timezone.utc).year + 2, description="Año de fabricación; mayor que 1900 y hasta dos años en el futuro.")
    type: VehicleType = Field(description="Tipo de vehículo.")
    status: VehicleStatus = Field(default=VehicleStatus.operative, description="Estado operativo; por defecto OPERATIVE.")

    @field_validator("plate_number", mode="after")
    @classmethod
    def normalize_plate_number(cls, v: str) -> str:
        return v.strip().upper()

class VehicleUpdate(SQLModel):
    plate_number: Optional[str] = Field(
        default=None,
        min_length=6,
        max_length=12,
        pattern=r"^[\d\w -]+$",
        description="Placas actualizadas; admite letras, números, espacios y guiones."
    )
    reg_number: Optional[str] = Field(
        default=None,
        min_length=12,
        max_length=22,
        pattern=r"^\d+$",
        description="Número de registro actualizado de la tarjeta de circulación, solo dígitos."
    )
    series_vin: Optional[str] = Field(
        default=None,
        min_length=17,
        max_length=17,
        pattern=r"^\d+$",
        description="VIN actualizado, exactamente 17 dígitos."
    )
    brand: Optional[str] = Field(default=None, min_length=1, max_length=60, description="Nueva marca del vehículo.")
    model: Optional[str] = Field(default=None, min_length=1, max_length=60, description="Nuevo modelo del vehículo.")
    year: Optional[int] = Field(default=None, gt=1900, le=datetime.now(timezone.utc).year + 2, description="Nuevo año de fabricación.")
    type: Optional[VehicleType] = Field(default=None, description="Nuevo tipo de vehículo.")
    status: Optional[VehicleStatus] = Field(default=None, description="Nuevo estado operativo.")

    @field_validator("plate_number", mode="after")
    @classmethod
    def normalize_plate_number(cls, v: Optional[str]) -> Optional[str]:
        return v.strip().upper() if v is not None else None

class VehicleResponseShort(SQLModel):
    plate_number: str = Field(max_length=12, description="Placas del vehículo.")
    brand: str = Field(max_length=60, description="Marca del vehículo.")
    model: str = Field(max_length=60, description="Modelo del vehículo.")
    year: int = Field(description="Año de fabricación.")
    type: VehicleType = Field(description="Tipo de vehículo.")
    status: VehicleStatus = Field(description="Estado operativo.")

class VehicleResponse(SQLModel):
    vehicle_id: UUID = Field(description="Identificador único del vehículo.")
    plate_number: str = Field(max_length=12, description="Placas del vehículo.")
    reg_number: str = Field(max_length=22, description="Número de registro de la tarjeta de circulación.")
    series_vin: str = Field(max_length=17, description="Número de identificación vehicular (VIN).")
    brand: str = Field(max_length=60, description="Marca del vehículo.")
    model: str = Field(max_length=60, description="Modelo del vehículo.")
    year: int = Field(description="Año de fabricación.")
    type: VehicleType = Field(description="Tipo de vehículo.")
    status: VehicleStatus = Field(description="Estado operativo.")
    registered_at: datetime = Field(description="Fecha y hora de registro.")
    updated_at: Optional[datetime] = Field(default=None, description="Fecha y hora de la última actualización.")

    model_config = {"from_attributes": True}
