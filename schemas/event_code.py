from pydantic import Field
from sqlmodel import SQLModel

from models.enums import SeverityLevel, EventCategory

class EventCodeResponse(SQLModel):
    code: str = Field(max_length=12, description="Identificador del código en el catálogo.")
    description: str = Field(max_length=40, description="Descripción legible del evento o incidente.")
    category: EventCategory = Field(description="Categoría del código, por ejemplo DEVICE, ACCIDENT o SECURITY.")
    severity: SeverityLevel = Field(description="Severidad: INFO, LOW, MEDIUM, HIGH o CRITICAL.")
    is_enabled: bool = Field(description="Indica si el código se puede utilizar.")

    model_config = {"from_attributes": True}
