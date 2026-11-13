from enum import Enum

class SeverityLevel(str, Enum):
    info = 'INFO'
    warning = 'WARNING'
    danger = 'DANGER'

class PriorityLevel(str, Enum):
    low = 'LOW'
    medium = 'MEDIUM'
    high = 'HIGH'

class UserRole(str, Enum):
    admin = 'ADMIN'
    driver = 'DRIVER'
    agent = 'AGENT'

class VehicleType(str, Enum):
    passenger_car = 'PASSENGER_CAR'
    pickup = 'PICKUP'
    panel = 'PANEL'
    van = 'VAN'
    bus = 'BUS'
    truck = 'TRUCK'

class VehicleStatus(str, Enum):
    operative = 'OPERATIVE'
    in_use = 'IN_USE'
    out_of_service = 'OUT_OF_SERVICE'
    under_maintenance = 'UNDER_MAINTENANCE'
    documents_expired = 'DOCUMENTS_EXPIRED'
    held_by_authorities = 'HELD_BY_AUTHORITIES'

class AlertType(str, Enum):
    account = 'ACCOUNT'
    system = 'SYSTEM'
    vehicle_incident = 'VEHICLE_INCIDENT'
    trip_incident = 'TRIP_INCIDENT'
    incident_update = 'INCIDENT_UPDATE'

class LicenseClass(str, Enum):
    A = 'A'
    A1 = 'A1'
    A2 = 'A2'
    B = 'B'
    C = 'C'
    D = 'D'
    E = 'E'

class VehicleServiceStatus(str, Enum):
    pending = 'PENDING'
    in_progress = 'IN_PROGRESS'
    completed = 'COMPLETED'
    cancelled = 'CANCELLED'
    discarded = 'DISCARDED'

class VehicleDeviceType(str, Enum):
    hub = 'HUB'
    node = 'NODE'

class TripStatus(str, Enum):
    planned = 'PLANNED'
    delayed = 'DELAYED'
    on_route = 'ON_ROUTE'
    at_base = 'AT_BASE'
    stopped = 'STOPPED'
    finished = 'FINISHED'
    cancelled = 'CANCELLED'
    aborted = 'ABORTED'
    gps_signal_lost = 'GPS_SIGNAL_LOST'

class IncidentStatus(str, Enum):
    open = 'OPEN'
    in_revision = 'IN_REVISION'
    closed = 'CLOSED'
    discarded = 'DISCARDED'

class MediaType(str, Enum):
    image = 'IMAGE'
    video = 'VIDEO'
