import uuid
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship
from models.enums import AlertType

if TYPE_CHECKING:
    from models.user import User

class UserAlert(SQLModel, table=True):
    __tablename__ = 'user_alerts'

    alert_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key='users.user_id', index=True)
    title: str = Field(index=True, max_length=80)
    content: Optional[str] = Field(default=None, max_length=240)
    type: AlertType
    is_read: bool
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user: Optional['User'] = Relationship(back_populates='alerts')
