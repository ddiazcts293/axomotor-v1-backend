import math
from datetime import datetime, time, timedelta, timezone
from decimal import Decimal
from typing import NamedTuple

from geoalchemy2.elements import WKTElement
from sqlmodel import Session

from models import Position, Trip
from models.enums import TripStatus, VehicleStatus

from .common import SeedContext, random_between
from .locations import LOCATION_SPECS

BASE_NAME = "Base AxoMotor Tijuana"
INDUSTRIAL_NAME = "Zona Industrial Mesa de Otay"
PANKY_USERNAME = "Panky"


class Place(NamedTuple):
    lon: float
    lat: float
    half_m: float


PLACES = {spec[0]: Place(spec[3], spec[4], spec[5]) for spec in LOCATION_SPECS}

# (estado, estado del vehículo a usar, conductor fijo)
HISTORICAL_PLAN = [
    (TripStatus.finished, VehicleStatus.under_maintenance, None),
    (TripStatus.finished, VehicleStatus.under_maintenance, None),
    (TripStatus.finished, VehicleStatus.operative, None),
    (TripStatus.finished, VehicleStatus.in_use, PANKY_USERNAME),
    (TripStatus.finished, VehicleStatus.operative, PANKY_USERNAME),
    (TripStatus.cancelled, VehicleStatus.operative, None),
    (TripStatus.aborted, VehicleStatus.in_use, None),
]


# ---------- utilidades geográficas ----------

def _haversine_km(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    radius = 6371.0088
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = phi2 - phi1
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return 2 * radius * math.asin(math.sqrt(a))


def _point_inside(rng, place: Place) -> tuple:
    d_lat = place.half_m / 111_320
    d_lon = place.half_m / (111_320 * math.cos(math.radians(place.lat)))
    return (
        place.lon + rng.uniform(-0.4, 0.4) * d_lon,
        place.lat + rng.uniform(-0.4, 0.4) * d_lat,
    )


def _route_point(rng, start: tuple, end: tuple, t: float, bend: float, interior: bool) -> tuple:
    dx, dy = end[0] - start[0], end[1] - start[1]
    lon = start[0] + dx * t
    lat = start[1] + dy * t
    if interior:
        curve = bend * math.sin(math.pi * t)
        lon += -dy * curve + rng.uniform(-0.0003, 0.0003)
        lat += dx * curve + rng.uniform(-0.0003, 0.0003)
    return lon, lat


def _wkt_point(lon: float, lat: float) -> WKTElement:
    # PostGIS: primero longitud, luego latitud
    return WKTElement(f"POINT({lon:.6f} {lat:.6f})", srid=4326)


def _dec(value: float) -> Decimal:
    return Decimal(str(round(min(max(value, 0.0), 999.99), 2))).quantize(Decimal("0.01"))


# ---------- planeación ----------

def _pick_route(ctx: SeedContext, min_km: float):
    rng = ctx.rng
    base = next(loc for loc in ctx.locations if loc.name == BASE_NAME)
    others = [loc for loc in ctx.locations if loc is not base]

    for _ in range(100):
        origin = base if rng.random() < 0.6 else rng.choice(others)
        if origin is not base and rng.random() < 0.5:
            destination = base
        else:
            destination = rng.choice([loc for loc in ctx.locations if loc is not origin])

        a, b = PLACES[origin.name], PLACES[destination.name]
        km = _haversine_km(a.lon, a.lat, b.lon, b.lat)
        if km >= min_km:
            return origin, destination, km

    raise RuntimeError("No se encontró una ruta que cumpla la distancia mínima")


def _planned_minutes(rng, straight_km: float) -> int:
    speed_kmh = rng.uniform(24, 42)
    return max(8, round(straight_km * 1.3 / speed_kmh * 60))


def _is_free(busy: dict, key: tuple, start: datetime, end: datetime) -> bool:
    return all(end <= b_start or start >= b_end for b_start, b_end in busy.get(key, []))


def _book(busy: dict, key: tuple, start: datetime, end: datetime) -> None:
    busy.setdefault(key, []).append((start, end))


# ---------- construcción de viajes y posiciones ----------

def _new_trip(vehicle, driver, origin, destination, status, departure, planned_min,
              created_at, started_at=None, finished_at=None) -> Trip:
    return Trip(
        vehicle_id=vehicle.vehicle_id,
        driver_id=driver.driver_id,
        origin_id=origin.location_id,
        destination_id=destination.location_id,
        departure_date=departure,
        arrive_date=departure + timedelta(minutes=planned_min),
        status=status,
        created_at=created_at,
        started_at=started_at,
        finished_at=finished_at,
    )


def _attach_route(ctx: SeedContext, trip: Trip, origin, destination,
                  covered_seconds: float, t_end: float, arrived: bool) -> None:
    """Genera las posiciones del viaje y calcula distance y average_speed a partir de ellas."""
    rng = ctx.rng
    start = _point_inside(rng, PLACES[origin.name])
    end = _point_inside(rng, PLACES[destination.name])

    count = max(10, min(20, round(covered_seconds / 60 / 1.5)))
    bend = rng.uniform(-0.12, 0.12)

    points, moments = [], []
    for i in range(count):
        fraction = i / (count - 1)
        interior = 0 < i and not (i == count - 1 and t_end >= 1.0)
        points.append(_route_point(rng, start, end, fraction * t_end, bend, interior))
        moments.append(trip.started_at + timedelta(seconds=fraction * covered_seconds))

    total_km = 0.0
    speeds = [rng.uniform(0, 5)]
    for i in range(1, count):
        segment_km = _haversine_km(*points[i - 1], *points[i])
        total_km += segment_km
        hours = (moments[i] - moments[i - 1]).total_seconds() / 3600
        speeds.append(segment_km / hours * rng.uniform(0.9, 1.1))
    if arrived:
        speeds[-1] = rng.uniform(0, 5)

    for (lon, lat), moment, speed in zip(points, moments, speeds):
        ctx.positions.append(
            Position(
                vehicle_id=trip.vehicle_id,
                trip_id=trip.trip_id,
                position=_wkt_point(lon, lat),
                speed=_dec(min(speed, 99.99)),
                registered_at=moment,
            )
        )

    trip.distance = _dec(total_km)
    trip.average_speed = _dec(total_km / (covered_seconds / 3600))


def _park_vehicles(ctx: SeedContext, on_route_start: datetime) -> None:
    """Posiciones de vehículos estacionados (sin viaje), con velocidad 0."""
    rng = ctx.rng
    lower = ctx.now - timedelta(hours=36)

    for vehicle in ctx.vehicles:
        place_name = INDUSTRIAL_NAME if vehicle.status == VehicleStatus.under_maintenance else BASE_NAME
        upper = ctx.now - timedelta(hours=1)
        if vehicle.status == VehicleStatus.in_use:
            upper = on_route_start - timedelta(minutes=15)

        for moment in sorted(random_between(rng, lower, upper) for _ in range(4)):
            lon, lat = _point_inside(rng, PLACES[place_name])
            ctx.positions.append(
                Position(
                    vehicle_id=vehicle.vehicle_id,
                    trip_id=None,
                    position=_wkt_point(lon, lat),
                    speed=Decimal("0.00"),
                    registered_at=moment,
                )
            )


def seed_trips(session: Session, ctx: SeedContext) -> None:
    rng = ctx.rng
    today = ctx.now.date()

    vehicles = {vehicle.status: vehicle for vehicle in ctx.vehicles}
    users_by_id = {user.user_id: user for user in ctx.users}
    panky = next(d for d in ctx.drivers if users_by_id[d.user_id].username == PANKY_USERNAME)
    # Sin conductores deshabilitados ni con licencia vencida
    eligible = [d for d in ctx.drivers if d.is_enabled and d.license_exp_date > today]
    others = [d for d in eligible if d is not panky]
    busy: dict = {}

    # 1) Viaje en curso: vehículo IN_USE con Panky
    in_use = vehicles[VehicleStatus.in_use]
    origin, destination, km = _pick_route(ctx, min_km=5)
    planned = _planned_minutes(rng, km)
    actual = planned * rng.uniform(0.9, 1.2)
    elapsed = actual * rng.uniform(0.35, 0.65)
    started_at = (ctx.now - timedelta(minutes=elapsed)).replace(microsecond=0)
    departure = started_at - timedelta(minutes=rng.randint(0, 6))

    trip = _new_trip(
        in_use, panky, origin, destination, TripStatus.on_route, departure, planned,
        created_at=departure - timedelta(hours=rng.uniform(1, 24)),
        started_at=started_at,
    )
    covered = elapsed * 60 - 30
    _attach_route(ctx, trip, origin, destination, covered, covered / (actual * 60), arrived=False)
    ctx.trips.append(trip)

    until = ctx.now + timedelta(minutes=actual - elapsed + 30)
    _book(busy, ("vehicle", in_use.vehicle_id), departure, until)
    _book(busy, ("driver", panky.driver_id), departure, until)
    in_use.updated_at = started_at
    panky.is_active = True
    panky.updated_at = started_at
    on_route_start = started_at

    # 2) Viaje retrasado: la pickup debía salir hace 15 minutos
    operative = vehicles[VehicleStatus.operative]
    origin, destination, km = _pick_route(ctx, min_km=3)
    planned = _planned_minutes(rng, km)
    departure = (ctx.now - timedelta(minutes=15)).replace(microsecond=0)
    ctx.trips.append(
        _new_trip(
            operative, rng.choice(others), origin, destination, TripStatus.delayed,
            departure, planned,
            created_at=departure - timedelta(hours=rng.uniform(3, 24)),
        )
    )

    # 3) Viaje planeado para mañana
    origin, destination, km = _pick_route(ctx, min_km=3)
    planned = _planned_minutes(rng, km)
    departure = (ctx.now + timedelta(days=1)).replace(
        hour=rng.randint(7, 12), minute=rng.choice((0, 15, 30, 45)), second=0, microsecond=0
    )
    ctx.trips.append(
        _new_trip(
            operative, rng.choice(eligible), origin, destination, TripStatus.planned,
            departure, planned,
            created_at=ctx.now - timedelta(hours=rng.uniform(1, 20)),
        )
    )

    # 4) Historial (sin traslapes por vehículo ni por conductor)
    window_start = ctx.start + timedelta(days=18)
    window_end = ctx.now - timedelta(days=3)

    for status, vehicle_status, forced_username in HISTORICAL_PLAN:
        vehicle = vehicles[vehicle_status]
        driver = panky if forced_username else rng.choice(eligible)

        # La licencia debe estar emitida antes del viaje
        issued = datetime.combine(driver.license_iss_date, time.min, tzinfo=timezone.utc)
        lower = max(window_start, issued + timedelta(days=1))
        upper = window_end - timedelta(hours=3)

        origin, destination, km = _pick_route(ctx, min_km=3)
        planned = _planned_minutes(rng, km)
        actual = planned * rng.uniform(0.9, 1.2)

        for _ in range(50):
            departure = random_between(rng, lower, upper).replace(
                hour=rng.randint(7, 18), minute=rng.randint(0, 59), second=0, microsecond=0
            )
            end = departure + timedelta(minutes=actual + 30)
            if (
                lower <= departure <= upper
                and _is_free(busy, ("vehicle", vehicle.vehicle_id), departure, end)
                and _is_free(busy, ("driver", driver.driver_id), departure, end)
            ):
                break
        else:
            raise RuntimeError("No se pudo programar un viaje histórico sin traslapes")

        _book(busy, ("vehicle", vehicle.vehicle_id), departure, end)
        _book(busy, ("driver", driver.driver_id), departure, end)

        if status == TripStatus.cancelled:
            cancelled_at = departure - timedelta(minutes=rng.randint(30, 360))
            trip = _new_trip(
                vehicle, driver, origin, destination, status, departure, planned,
                created_at=cancelled_at - timedelta(hours=rng.uniform(1, 24)),
                finished_at=cancelled_at,
            )
        else:
            started_at = departure + timedelta(minutes=rng.randint(0, 8))
            aborted = status == TripStatus.aborted
            fraction = rng.uniform(0.35, 0.6) if aborted else 1.0
            covered = actual * 60 * fraction
            trip = _new_trip(
                vehicle, driver, origin, destination, status, departure, planned,
                created_at=departure - timedelta(hours=rng.uniform(2, 48)),
                started_at=started_at,
                finished_at=started_at + timedelta(seconds=covered),
            )
            _attach_route(ctx, trip, origin, destination, covered, fraction, arrived=not aborted)

        ctx.trips.append(trip)

    session.add_all(ctx.trips)
    session.flush()

    _park_vehicles(ctx, on_route_start)
    session.add_all(ctx.positions)
    session.flush()