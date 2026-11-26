from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import EmailStr, Field, computed_field, field_validator
from sqlmodel import SQLModel

from models.enums import UserRole

class UserCreate(SQLModel):
    first_name: str = Field(min_length=2, max_length=60, description="Nombre de pila del usuario.")
    last_name: Optional[str] = Field(default=None, max_length=60, description="Apellidos del usuario, si se conocen.")
    email: EmailStr = Field(max_length=120, description="Correo electrónico único para iniciar sesión o recibir comunicaciones.")
    username: str = Field(
        min_length=3,
        max_length=16,
        description="Nombre de usuario único; admite letras, números, puntos y guiones bajos. Se normaliza a minúsculas.",
        pattern=r"^[\d\w._]+$"
    )
    phone_number: str = Field(
        max_length=16,
        pattern=r"^\+\d{1,3} \d{3}-\d{3}-\d{3,4}$",
        description="Teléfono único con prefijo internacional, por ejemplo +52 664-123-4567.",
        examples=["+52 664-123-4567", "+1 619-123-4567"]
    )
    password: str = Field(min_length=8, max_length=120, description="Contraseña inicial; mínimo 8 y máximo 120 caracteres.")
    role: UserRole = Field(description="Rol del usuario: ADMIN, DRIVER o AGENT.")

    @field_validator("username", mode="after")
    @classmethod
    def normalize_username(cls, v: str) -> str:
        return v.strip().lower()

class UserUpdate(SQLModel):
    first_name: Optional[str] = Field(default=None, min_length=2, max_length=60, description="Nuevo nombre de pila.")
    last_name: Optional[str] = Field(default=None, max_length=60, description="Nuevos apellidos.")
    email: Optional[EmailStr] = Field(default=None, max_length=120, description="Nuevo correo electrónico único.")
    username: Optional[str] = Field(default=None,
        min_length=3,
        max_length=16,
        description="Nuevo nombre de usuario único; admite letras, números, puntos y guiones bajos. Se normaliza a minúsculas.",
        pattern=r"^[\d\w._]+$"
    )
    phone_number: Optional[str] = Field(
        default=None,
        max_length=16,
        pattern=r"^\+\d{1,3} \d{3}-\d{3}-\d{3,4}$",
        description="Nuevo teléfono único con prefijo internacional.",
        examples=["+52 664-123-4567", "+1 619-123-4567"]
    )
    is_enabled: Optional[bool] = Field(default=None, description="Habilita o deshabilita la cuenta.")

    @field_validator("username", mode="after")
    @classmethod
    def normalize_username(cls, v: Optional[str]) -> Optional[str]:
        return v.strip().lower() if v is not None else None

class UserUpdatePassword(SQLModel):
    current_password: str = Field(description="Contraseña vigente, necesaria para autorizar el cambio.")
    new_password: str = Field(min_length=8, max_length=120, description="Nueva contraseña; mínimo 8 y máximo 120 caracteres.")

class UserResponse(SQLModel):
    user_id: UUID = Field(description="Identificador único del usuario.")
    first_name: str = Field(min_length=2, max_length=60, description="Nombre de pila.")
    last_name: Optional[str] = Field(max_length=60, description="Apellidos, si se registraron.")
    email: EmailStr = Field(max_length=120, description="Correo electrónico.")
    username: str = Field(min_length=3, max_length=16, description="Nombre de usuario.")
    phone_number: str = Field(max_length=16, description="Teléfono con prefijo internacional.")
    role: UserRole = Field(description="Rol asignado: ADMIN, DRIVER o AGENT.")
    is_enabled: bool = Field(description="Indica si la cuenta está habilitada.")
    registered_at: datetime = Field(description="Fecha y hora de registro.")
    updated_at: Optional[datetime] = Field(default=None, description="Fecha y hora de la última actualización.")
    logged_in_at: Optional[datetime] = Field(default=None, description="Fecha y hora del último inicio de sesión.")

    model_config = {"from_attributes": True}

class UserResponseShort(SQLModel):
    first_name: str = Field(description="Nombre de pila.")
    last_name: Optional[str] = Field(description="Apellidos, si se registraron.")
    role: UserRole = Field(description="Rol asignado al usuario.")
    phone_number: str = Field(max_length=16, description="Teléfono con prefijo internacional.")
    email: EmailStr = Field(max_length=120, description="Correo electrónico.")
