import uuid
from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING
from pydantic import EmailStr

import sqlalchemy as sa
from sqlmodel import SQLModel, Field, Relationship
from models.enums import UserRole

if TYPE_CHECKING:
    from models.driver import Driver
    from models.user_alert import UserAlert
    from models.vehicle_service import VehicleService
    from models.incident import Incident
    from models.incident_media_file import IncidentMediaFile

class User(SQLModel, table=True):
    __tablename__ = 'users'

    user_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    first_name: str = Field(index=True, min_length=2, max_length=60)
    last_name: Optional[str] = Field(default=None, index=True, min_length=2, max_length=60)
    email: EmailStr = Field(index=True, unique=True, max_length=120)
    username: str = Field(index=True, unique=True, min_length=3, max_length=16)
    phone_number: str = Field(index=True, unique=True, max_length=16)
    hashed_password: str
    role: UserRole
    is_enabled: bool = Field(default=True)
    registered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column_kwargs={
            'onupdate': sa.func.now(),
            'server_default': sa.func.now(),
        }
    )
    logged_in_at: Optional[datetime] = None

    driver: Optional['Driver'] = Relationship(
        back_populates='user',
        sa_relationship_kwargs={'cascade': 'all, delete-orphan', 'uselist': False}
    )
    alerts: List['UserAlert'] = Relationship(
        back_populates='user',
        sa_relationship_kwargs={'cascade': 'all, delete-orphan'}
    )
    vehicle_services_created: List['VehicleService'] = Relationship(
        back_populates='created_by',
        sa_relationship_kwargs={
            'cascade': 'all, delete-orphan',
            'foreign_keys': '[VehicleService.created_by_id]'
        }
    )
    vehicle_services_authorized: List['VehicleService'] = Relationship(
        back_populates='authorized_by',
        sa_relationship_kwargs={
            'cascade': 'all, delete-orphan',
            'foreign_keys': '[VehicleService.authorized_by_id]'
        }
    )
    incidents_created: List['Incident'] = Relationship(
        back_populates='created_by',
        sa_relationship_kwargs={
            'cascade': 'all, delete-orphan',
            'foreign_keys': '[Incident.created_by_id]'
        }
    )
    incidents_reviewed: List['Incident'] = Relationship(
        back_populates='reviewed_by',
        sa_relationship_kwargs={
            'cascade': 'all, delete-orphan',
            'foreign_keys': '[Incident.reviewed_by_id]'
        }
    )
    media_files: List['IncidentMediaFile'] = Relationship(
        back_populates='uploaded_by',
        sa_relationship_kwargs={
            'cascade': 'all, delete-orphan',
            'foreign_keys': '[IncidentMediaFile.uploaded_by_id]'
        }
    )
