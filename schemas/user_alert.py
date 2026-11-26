from typing import Optional, Any, Dict
from uuid import UUID
from datetime import datetime

from pydantic import Field
from sqlmodel import SQLModel

from models.enums import AlertType

class UserAlertUpdate(SQLModel):
    is_read: bool = Field(description="Marca la alerta como leída (true) o no leída (false).")

class UserAlertResponse(SQLModel):
    alert_id: UUID = Field(description="Identificador único de la alerta.")
    user_id: UUID = Field(description="Identificador del usuario destinatario.")
    title: str = Field(max_length=80, description="Título breve de la alerta.")
    content: Optional[str] = Field(max_length=240, description="Contenido adicional de la alerta.")
    type: AlertType = Field(description="Categoría de alerta: ACCOUNT, SYSTEM, VEHICLE_INCIDENT, TRIP_INCIDENT o INCIDENT_UPDATE.")
    is_read: bool = Field(description="Indica si el usuario ya leyó la alerta.")
    created_at: datetime = Field(description="Fecha y hora de creación de la alerta.")

    model_config = {"from_attributes": True}
