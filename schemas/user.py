from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import EmailStr, Field, computed_field, field_validator
from sqlmodel import SQLModel

from models.enums import UserRole

class UserCreate(SQLModel):
    first_name: str = Field(min_length=2, max_length=60)
    last_name: Optional[str] = Field(default=None, max_length=60)
    email: EmailStr = Field(max_length=120)
    username: str = Field(
        min_length=3,
        max_length=16,
        description="Nickname (alphanumerical, periods, and underscores are allowed)",
        pattern=r"^[\d\w._]+$"
    )
    phone_number: str = Field(
        max_length=16,
        pattern=r"^\+\d{1,3} \d{3}-\d{3}-\d{3,4}$",
        description="Format +00 000-000-0000",
        examples=["+52 664-123-4567", "+1 619-123-4567"]
    )
    password: str = Field(min_length=8, max_length=120)
    role: UserRole

    @field_validator("username", mode="after")
    @classmethod
    def normalize_username(cls, v: str) -> str:
        return v.strip().lower()

class UserUpdate(SQLModel):
    first_name: Optional[str] = Field(default=None, min_length=2, max_length=60)
    last_name: Optional[str] = Field(default=None, max_length=60)
    email: Optional[EmailStr] = Field(default=None, max_length=120)
    username: Optional[str] = Field(default=None,
        min_length=3,
        max_length=16,
        description="Nickname (alphanumerical, periods, and underscores are allowed)",
        pattern=r"^[\d\w._]+$"
    )
    phone_number: Optional[str] = Field(
        default=None,
        max_length=16,
        pattern=r"^\+\d{1,3} \d{3}-\d{3}-\d{3,4}$",
        description="Format +00 000-000-0000",
        examples=["+52 664-123-4567", "+1 619-123-4567"]
    )
    is_enabled: Optional[bool] = None

    @field_validator("username", mode="after")
    @classmethod
    def normalize_username(cls, v: Optional[str]) -> Optional[str]:
        return v.strip().lower() if v is not None else None

class UserUpdatePassword(SQLModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=120)

class UserResponse(SQLModel):
    user_id: UUID
    first_name: str = Field(min_length=2, max_length=60)
    last_name: Optional[str] = Field(max_length=60)
    email: EmailStr = Field(max_length=120)
    username: str = Field(min_length=3, max_length=16)
    phone_number: str = Field(max_length=16)
    role: UserRole
    is_enabled: bool
    registered_at: datetime
    updated_at: Optional[datetime] = None
    logged_in_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

class UserResponseShort(SQLModel):
    user_id: UUID
    first_name: str = Field(exclude=True)
    last_name: Optional[str] = Field(exclude=True)
    role: UserRole

    @computed_field
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()
