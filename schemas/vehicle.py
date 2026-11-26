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
        description="Plate number (alphanumerical, spaces, and dashes are allowed)"
    )
    reg_number: str = Field(
        min_length=12,
        max_length=22,
        pattern=r"^\d+$",
        description="Registration number (digits only)"
    )
    series_vin: str = Field(
        min_length=17,
        max_length=17,
        pattern=r"^\d+$",
        description="Vehicle Identification Number (digits only)"
    )
    brand: str = Field(min_length=1, max_length=60)
    model: str = Field(min_length=1, max_length=60)
    year: int = Field(gt=1900, le=datetime.now(timezone.utc).year + 2)
    type: VehicleType
    status: VehicleStatus = Field(default=VehicleStatus.operative)

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
        description="Plate number (alphanumerical, spaces, and dashes are allowed)"
    )
    reg_number: Optional[str] = Field(
        default=None,
        min_length=12,
        max_length=22,
        pattern=r"^\d+$",
        description="Registration number (digits only)"
    )
    series_vin: Optional[str] = Field(
        default=None,
        min_length=17,
        max_length=17,
        pattern=r"^\d+$",
        description="Vehicle Identification Number (digits only)"
    )
    brand: Optional[str] = Field(default=None, min_length=1, max_length=60)
    model: Optional[str] = Field(default=None, min_length=1, max_length=60)
    year: Optional[int] = Field(default=None, gt=1900, le=datetime.now(timezone.utc).year + 2)
    type: Optional[VehicleType] = Field(default=None)
    status: Optional[VehicleStatus] = Field(default=None)

    @field_validator("plate_number", mode="after")
    @classmethod
    def normalize_plate_number(cls, v: Optional[str]) -> Optional[str]:
        return v.strip().upper() if v is not None else None

class VehicleResponse(SQLModel):
    vehicle_id: UUID
    plate_number: str = Field(max_length=12)
    reg_number: str = Field(max_length=22)
    series_vin: str = Field(max_length=17)
    brand: str = Field(max_length=60)
    model: str = Field(max_length=60)
    year: int
    type: VehicleType
    status: VehicleStatus
    registered_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
