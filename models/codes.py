from typing import List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from models.enums import SeverityLevel

if TYPE_CHECKING:
    from models.vehicle_event import VehicleEvent
    from models.incident import Incident

class VehicleEventCode(SQLModel, table=True):
    __tablename__ = 'vehicle_event_codes'

    code: str = Field(primary_key=True, max_length=12)
    description: str = Field(index=True, unique=True, max_length=40)
    severity: SeverityLevel = Field()

    events: List['VehicleEvent'] = Relationship(
        back_populates='info',
        sa_relationship_kwargs={'cascade': 'all, delete-orphan'}
    )

class IncidentCode(SQLModel, table=True):
    __tablename__ = 'incident_codes'

    code: str = Field(primary_key=True, max_length=12)
    description: str = Field(index=True, unique=True, max_length=40)
    severity: SeverityLevel = Field()

    incidents: List['Incident'] = Relationship(
        back_populates='info',
        sa_relationship_kwargs={'cascade': 'all, delete-orphan'}
    )
