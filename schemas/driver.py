from uuid import UUID
from datetime import datetime, date, timedelta
from typing import Optional

from pydantic import Field, computed_field, model_validator
from sqlmodel import SQLModel

from core.config import settings
from models.enums import LicenseClass
from schemas.user import UserResponse

class DriverCreate(SQLModel):
    user_id: UUID
    license_number: str = Field(
        min_length=8,
        max_length=20,
        pattern=r"^\d+$",
        description="Driver's license number (digits only)"
    )
    license_class: LicenseClass
    license_iss_date: date
    license_exp_date: date

    @model_validator(mode="after")
    def validate_dates(self) -> "DriverCreate":
        if self.license_iss_date == self.license_exp_date:
            raise ValueError("Issue date and expiration date cannot be the same")
        if self.license_iss_date > self.license_exp_date:
            raise ValueError("Issue date must be before expiration date")
        return self

class DriverUpdate(SQLModel):
    license_number: Optional[str] = Field(default=None,
        min_length=8,
        max_length=20,
        pattern=r"^\d+$",
        description="Driver's license number (digits only)"
    )
    license_class: Optional[LicenseClass] = Field(default=None)
    license_iss_date: Optional[date] = Field(default=None)
    license_exp_date: Optional[date] = Field(default=None)
    is_enabled: Optional[bool] = None

class DriverResponse(SQLModel):
    driver_id: UUID
    user_id: UUID
    telegram_user_id: Optional[int] = Field(exclude=True)
    license_number: str = Field(max_length=20)
    license_class: LicenseClass
    license_iss_date: date
    license_exp_date: date
    is_active: bool
    is_enabled: bool
    registered_at: datetime
    updated_at: Optional[datetime] = None

    @computed_field
    @property
    def has_linked_telegram_account(self) -> bool:
        return self.telegram_user_id is not None

    model_config = {"from_attributes": True}

class DriverResponseExtended(DriverResponse):
    user: UserResponse

class LinkCreateResponse(SQLModel):
    token: str = Field(max_length=60)
    created_at: datetime

    @computed_field
    @property
    def expires_on(self) -> datetime:
        return self.created_at + timedelta(minutes=settings.LINKING_TOKEN_EXPIRE_MINUTES)

    @computed_field
    @property
    def url(self) -> str:
        return f"https://t.me/{settings.TELEGRAM_BOT_USERNAME}?start={self.token}"

class DriverLink(SQLModel):
    token: str = Field(max_length=60)
    telegram_user_id: int
