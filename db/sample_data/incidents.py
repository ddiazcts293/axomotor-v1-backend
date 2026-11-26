from collections import defaultdict
from datetime import timedelta

from geoalchemy2.elements import WKTElement
from sqlmodel import Session

from models import Incident, VehicleEvent
from models.enums import (
    IncidentStatus,
    PriorityLevel,
    SeverityLevel,
    TripStatus,
    UserRole,
    VehicleDeviceType,
    VehicleStatus,
)

from .codes import EVENT_KEYS, INCIDENT_KEYS
from .common import SeedContext
from .trips import BASE_NAME, PLACES, _point_inside, _wkt_point

PRIORITY_BY_SEVERITY = {
    SeverityLevel.critical: PriorityLevel.high,
    SeverityLevel.high: PriorityLevel.high,
    SeverityLevel.medium: PriorityLevel.medium,
    SeverityLevel.low: PriorityLevel.low,
    SeverityLevel.info: PriorityLevel.low,
}

GENERIC_KEYS = [
    ("heavy_traffic", 3),
    ("delay_eta", 2),
    ("minor_hit", 1),
    ("route_deviation", 1),
    ("police_check", 1),
    ("flat_tire", 1),
    ("road_block", 1),
    ("severe_weather", 1),
]

SEVERE_KEYS = ("collision", "crash")

DESCRIPTIONS = {
    "minor_hit": [
        "Percance vial menor sin lesionados en el trayecto hacia {destination}. Se intercambiaron datos con la otra parte.",
        "Golpe leve al maniobrar cerca de {origin}. Sin lesionados ni daños mayores.",
    ],
    "collision": [
        "Colisión vehicular detectada por el módulo durante el trayecto de {origin} a {destination}. Se solicitó confirmación inmediata al conductor.",
    ],
    "crash": [
        "Accidente vehicular grave durante el trayecto de {origin} a {destination}. El viaje fue interrumpido.",
    ],
    "heavy_traffic": [
        "Congestión vehicular severa en el trayecto de {origin} a {destination}.",
        "Tráfico detenido por congestión en la ruta hacia {destination}.",
    ],
    "route_deviation": [
        "Desvío de ruta forzoso por obras viales entre {origin} y {destination}.",
    ],
    "delay_eta": [
        "Retraso estimado en la hora de llegada a {destination}.",
        "Se prevé llegar con retraso a {destination} por las condiciones de la ruta.",
    ],
    "police_check": [
        "Retén de inspección durante el trayecto hacia {destination}. Documentación en regla.",
    ],
    "flat_tire": [
        "Ponchadura de neumático en ruta hacia {destination}. El conductor realizó el cambio de llanta.",
    ],
    "road_block": [
        "Bloqueo parcial de carretera cerca de {destination}; se tomó una vía alterna.",
    ],
    "severe_weather": [
        "Condiciones climáticas adversas (lluvia intensa) en la ruta de {origin} a {destination}.",
    ],
}

COMMENTS = {
    IncidentStatus.in_revision: [
        "Incidente en seguimiento por parte del agente asignado.",
        "Se solicitó información adicional al conductor.",
    ],
    IncidentStatus.closed: [
        "Se contactó al conductor y se confirmó que no hubo afectaciones.",
        "Situación atendida y resuelta; no se requieren acciones adicionales.",
    ],
    IncidentStatus.discarded: [
        "Falsa alarma: el evento coincide con una condición normal de la vía.",
        "Se descartó tras revisar el historial de posiciones del viaje.",
    ],
}
SEVERE_COMMENT = "Se contactó al conductor y se coordinó asistencia; el viaje fue abortado."


def _clone_point(position) -> WKTElement:
    # El texto WKT ya viene en orden longitud, latitud
    return WKTElement(str(position.data).split(";")[-1], srid=4326)


def _generic_key(rng) -> str:
    keys, weights = zip(*GENERIC_KEYS)
    return rng.choices(keys, weights=weights)[0]


def _plan_trip_incidents(rng, trip, count_positions: int) -> list:
    n = count_positions
    if trip.status == TripStatus.aborted:
        plan = [("collision", n - 2), ("crash", n - 1)]
        if rng.random() < 0.5:
            plan.append((_generic_key(rng), rng.randint(1, n - 3)))
    else:
        count = rng.choices([0, 1, 2, 3], weights=[1, 1, 2, 2])[0]
        indices = rng.sample(range(1, n), count)
        plan = [(_generic_key(rng), index) for index in indices]
    return sorted(plan, key=lambda item: item[1])


def _pick_status(rng, key: str, age: timedelta) -> IncidentStatus:
    if age < timedelta(minutes=30):
        return IncidentStatus.open
    if key in SEVERE_KEYS:
        return IncidentStatus.closed if age > timedelta(days=1) else IncidentStatus.in_revision
    if age < timedelta(days=1):
        options, weights = [IncidentStatus.open, IncidentStatus.in_revision], [6, 4]
    elif age < timedelta(days=14):
        options = [IncidentStatus.open, IncidentStatus.in_revision,
                   IncidentStatus.closed, IncidentStatus.discarded]
        weights = [25, 25, 40, 10]
    else:
        options = [IncidentStatus.in_revision, IncidentStatus.closed, IncidentStatus.discarded]
        weights = [10, 70, 20]
    return rng.choices(options, weights=weights)[0]


def _pick_reviewer(rng, creator, staff):
    # Los usuarios también pueden revisar sus propios incidentes
    if creator.role == UserRole.driver and rng.random() < 0.25:
        return creator
    return rng.choice(staff)


def seed_incidents_and_events(session: Session, ctx: SeedContext, catalog: dict) -> tuple:
    rng = ctx.rng
    users_by_id = {user.user_id: user for user in ctx.users}
    driver_users = {d.driver_id: users_by_id[d.user_id] for d in ctx.drivers}
    agents = [u for u in ctx.users if u.role == UserRole.agent]
    staff = [u for u in ctx.users if u.role in (UserRole.admin, UserRole.agent)]
    names = {location.location_id: location.name for location in ctx.locations}

    positions_by_trip = defaultdict(list)
    for position in ctx.positions:
        if position.trip_id is not None:
            positions_by_trip[position.trip_id].append(position)
    for items in positions_by_trip.values():
        items.sort(key=lambda p: p.registered_at)

    # ---------- Incidentes ----------
    incidents = []  # (incidente, clave, viaje, índice de posición)
    for trip in ctx.trips:
        positions = positions_by_trip.get(trip.trip_id)
        if not positions:
            continue

        previous = None
        for key, index in _plan_trip_incidents(rng, trip, len(positions)):
            position = positions[index]
            if key == "crash":
                registered_at = position.registered_at
            else:
                registered_at = position.registered_at + timedelta(seconds=rng.randint(0, 5))

            creator = driver_users[trip.driver_id] if rng.random() < 0.8 else rng.choice(agents)
            age = ctx.now - registered_at
            status = _pick_status(rng, key, age)

            reviewer = reviewed_at = closed_at = comments = None
            if status != IncidentStatus.open:
                reviewer = _pick_reviewer(rng, creator, staff)
                delay = min(rng.uniform(10, 360) * 60, age.total_seconds() - 60)
                reviewed_at = (registered_at + timedelta(seconds=delay)).replace(microsecond=0)
                if status in (IncidentStatus.closed, IncidentStatus.discarded):
                    closed_at = min(
                        reviewed_at + timedelta(minutes=rng.uniform(10, 1440)), ctx.now
                    ).replace(microsecond=0)
                if key in SEVERE_KEYS and status == IncidentStatus.closed:
                    comments = SEVERE_COMMENT
                else:
                    comments = rng.choice(COMMENTS[status])

            if key == "crash" or (previous is not None and rng.random() < 0.2):
                related_id = previous.incident_id if previous is not None else None
            else:
                related_id = None

            code = INCIDENT_KEYS[key]
            incident = Incident(
                trip_id=trip.trip_id,
                code=code,
                priority=PRIORITY_BY_SEVERITY[catalog[code].severity],
                status=status,
                position=_clone_point(position.position),
                description=rng.choice(DESCRIPTIONS[key]).format(
                    origin=names[trip.origin_id], destination=names[trip.destination_id]
                ),
                comments=comments,
                related_incident_id=related_id,
                registered_at=registered_at.replace(microsecond=0),
                reviewed_at=reviewed_at,
                closed_at=closed_at,
                created_by_id=creator.user_id,
                reviewed_by_id=reviewer.user_id if reviewer else None,
            )
            incidents.append((incident, key, trip, index))
            previous = incident

    # Los incidentes padre se insertan antes que los relacionados
    session.add_all([item[0] for item in incidents])
    session.flush()

    # ---------- Eventos de vehículo ----------
    events = []

    def add_event(vehicle_id, key, moment, point=None, data=None):
        events.append(
            VehicleEvent(
                vehicle_id=vehicle_id,
                code=EVENT_KEYS[key],
                position=point,
                additional_data=data,
                registered_at=moment.replace(microsecond=0),
            )
        )

    def point_of(position) -> WKTElement:
        return _clone_point(position.position)

    for trip in ctx.trips:
        positions = positions_by_trip.get(trip.trip_id)
        if not positions:
            continue
        n = len(positions)
        first, last = positions[0], positions[-1]

        # Eventos propios del viaje
        add_event(trip.vehicle_id, "driver_access", trip.started_at - timedelta(minutes=3),
                  point_of(first), {"driver_id": str(trip.driver_id)})
        add_event(trip.vehicle_id, "movement_start", trip.started_at,
                  point_of(first), {"trip_id": str(trip.trip_id)})
        if trip.status in (TripStatus.finished, TripStatus.aborted):
            add_event(trip.vehicle_id, "movement_stop", trip.finished_at,
                      point_of(last), {"trip_distance_km": float(trip.distance)})
        if trip.status == TripStatus.finished:
            add_event(trip.vehicle_id, "parked", trip.finished_at + timedelta(minutes=1),
                      point_of(last))

        # Frenado brusco ocasional
        if rng.random() < 0.4:
            position = positions[rng.randint(2, n - 2)]
            add_event(trip.vehicle_id, "harsh_brake", position.registered_at,
                      point_of(position), {"deceleration_ms2": round(rng.uniform(4.0, 7.5), 1)})

        # Pérdidas y recuperaciones de señal GPS y de red móvil
        for lost_key, restored_key, probability in (
            ("gps_lost", "gps_restored", 0.3),
            ("data_lost", "data_restored", 0.2),
        ):
            if rng.random() >= probability:
                continue
            index = rng.randint(2, n - 4)
            lost_at = positions[index].registered_at + timedelta(seconds=10)
            duration = rng.randint(60, 300)
            restored_at = lost_at + timedelta(seconds=duration)
            if restored_at > ctx.now or (
                trip.finished_at is not None and restored_at > trip.finished_at
            ):
                continue
            add_event(trip.vehicle_id, lost_key, lost_at,
                      point_of(positions[index]), {"duration_s": duration})
            add_event(trip.vehicle_id, restored_key, restored_at,
                      point_of(positions[min(index + 2, n - 1)]), {"duration_s": duration})

    # Impactos detectados en los incidentes de choque, con grabación de evidencia
    for incident, key, trip, index in incidents:
        if key not in ("minor_hit", "collision"):
            continue

        positions = positions_by_trip[trip.trip_id]
        moment = max(
            incident.registered_at - timedelta(seconds=rng.randint(5, 30)), trip.started_at
        )
        g_force = rng.uniform(1.5, 3.0) if key == "minor_hit" else rng.uniform(4.5, 8.0)
        add_event(trip.vehicle_id, "impact", moment, point_of(positions[index]),
                  {"g_force": round(g_force, 1)})

        video_start = moment + timedelta(seconds=5)
        video_stop = video_start + timedelta(seconds=rng.randint(60, 120))
        if video_start <= ctx.now:
            add_event(trip.vehicle_id, "video_start", video_start, point_of(positions[index]))
        if video_stop <= ctx.now:
            add_event(trip.vehicle_id, "video_stop", video_stop, point_of(positions[index]))

    # Casos sueltos
    operative = next(v for v in ctx.vehicles if v.status == VehicleStatus.operative)
    night = (ctx.now - timedelta(days=2)).replace(hour=9, minute=rng.randint(0, 59), second=0)
    lon, lat = _point_inside(rng, PLACES[BASE_NAME])
    add_event(operative.vehicle_id, "activity_detected", night, _wkt_point(lon, lat),
              {"zone": "cabina", "duration_s": rng.randint(20, 90)})

    low_battery = next(d for d in ctx.devices if d.battery_level == 12)
    add_event(low_battery.vehicle_id, "battery_critical", ctx.now - timedelta(hours=6),
              None, {"device_tag": low_battery.tag, "battery_level": 12})

    offline = next(d for d in ctx.devices if d.is_active is False)
    add_event(offline.vehicle_id, "device_disconnected", ctx.now - timedelta(hours=20),
              None, {"device_tag": offline.tag})

    for hub in (d for d in ctx.devices if d.type == VehicleDeviceType.hub):
        add_event(hub.vehicle_id, "battery_level", hub.updated_at, None,
                  {"device_tag": hub.tag, "battery_level": hub.battery_level})

    session.add_all(events)
    session.flush()

    return len(incidents), len(events)