from uuid import UUID
from datetime import datetime, date, timedelta
from typing import Optional, override

from pydantic import Field, computed_field, model_validator
from sqlmodel import SQLModel

from core.config import settings
from models.enums import LicenseClass
from schemas.user import UserResponse, UserResponseShort

class DriverCreate(SQLModel):
    user_id: UUID = Field(description="UUID de un usuario existente cuyo rol sea DRIVER.")
    license_number: str = Field(
        min_length=8,
        max_length=20,
        pattern=r"^\d+$",
        description="Número de licencia; de 8 a 20 dígitos, sin separadores."
    )
    license_class: LicenseClass = Field(description="Clase de licencia: A, A1, A2, B, C, D o E.")
    license_iss_date: date = Field(description="Fecha de expedición de la licencia.")
    license_exp_date: date = Field(description="Fecha de vencimiento; debe ser posterior a la expedición.")

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
        description="Número de licencia actualizado; de 8 a 20 dígitos, sin separadores."
    )
    license_class: Optional[LicenseClass] = Field(default=None, description="Nueva clase de licencia.")
    license_iss_date: Optional[date] = Field(default=None, description="Nueva fecha de expedición.")
    license_exp_date: Optional[date] = Field(default=None, description="Nueva fecha de vencimiento.")
    is_enabled: Optional[bool] = Field(default=None, description="Habilita o deshabilita al conductor.")

class DriverResponseShort(SQLModel):
    user: UserResponse = Field(exclude=True, description="Datos internos usados para construir los campos de usuario resumidos.")
    user_id: UUID = Field(description="UUID del usuario asociado.")

    @computed_field(description="Nombre de pila del usuario asociado.")
    @property
    def first_name(self) -> str:
        return self.user.first_name

    @computed_field(description="Apellidos del usuario asociado, si existen.")
    @property
    def last_name(self) -> Optional[str]:
        return self.user.last_name

    @computed_field(description="Teléfono del usuario asociado.")
    @property
    def phone_number(self) -> str:
        return self.user.phone_number

    @computed_field(description="Correo electrónico del usuario asociado.")
    @property
    def email(self) -> str:
        return self.user.email

    license_number: str = Field(max_length=20, description="Número de licencia.")
    license_class: LicenseClass = Field(description="Clase de licencia.")
    is_active: bool = Field(description="Indica si el perfil de conductor está activo.")
    is_enabled: bool = Field(description="Indica si el conductor está habilitado.")

class DriverResponse(SQLModel):
    driver_id: UUID = Field(description="Identificador único del perfil de conductor.")
    user_id: UUID = Field(description="Identificador del usuario vinculado.")
    telegram_user_id: Optional[int] = Field(exclude=True, description="Identificador de Telegram; se omite de la respuesta pública.")
    license_number: str = Field(max_length=20, description="Número de licencia.")
    license_class: LicenseClass = Field(description="Clase de licencia.")
    license_iss_date: date = Field(description="Fecha de expedición.")
    license_exp_date: date = Field(description="Fecha de vencimiento.")
    is_active: bool = Field(description="Indica si el perfil está activo.")
    is_enabled: bool = Field(description="Indica si el conductor está habilitado.")
    registered_at: datetime = Field(description="Fecha y hora de registro.")
    updated_at: Optional[datetime] = Field(default=None, description="Fecha y hora de la última actualización.")

    @computed_field(description="Indica si el conductor tiene una cuenta de Telegram vinculada.")
    @property
    def has_linked_telegram_account(self) -> bool:
        return self.telegram_user_id is not None

    user: UserResponseShort = Field(..., description="Datos resumidos del usuario asociado.")

    model_config = {"from_attributes": True}

class LinkCreateResponse(SQLModel):
    token: str = Field(max_length=60, description="Token temporal para vincular la cuenta con el bot.")
    created_at: datetime = Field(description="Fecha y hora de emisión del token.")

    @computed_field(description="Fecha y hora de expiración del token de vinculación.")
    @property
    def expires_on(self) -> datetime:
        return self.created_at + timedelta(minutes=settings.LINKING_TOKEN_EXPIRE_MINUTES)

    @computed_field(description="Enlace profundo para iniciar el bot con el token de vinculación.")
    @property
    def url(self) -> str:
        return f"https://t.me/{settings.TELEGRAM_BOT_USERNAME}?start={self.token}"

class DriverLink(SQLModel):
    token: str = Field(max_length=60, description="Token de vinculación vigente emitido por la API.")
    telegram_user_id: int = Field(description="Identificador numérico de la cuenta de Telegram.")
