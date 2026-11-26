import math

from geoalchemy2.elements import WKTElement
from sqlmodel import Session

from models import KnownLocation

from .common import SeedContext, random_between
from datetime import timedelta

# (nombre, tipo, dirección, longitud, latitud, mitad del lado del polígono en metros)
# Coordenadas aproximadas (±300 m); la base AxoMotor es una ubicación ficticia.
LOCATION_SPECS = [
    ("Aeropuerto Internacional de Tijuana", "Aeropuerto",
     "Zona del Aeropuerto, Mesa de Otay, Tijuana, Baja California", -116.9700, 32.5411, 400),
    ("Garita El Chaparral", "Cruce fronterizo",
     "Garita El Chaparral, Zona Centro, Tijuana, Baja California", -117.0300, 32.5400, 150),
    ("Garita Otay", "Cruce fronterizo",
     "Garita Otay, Mesa de Otay, Tijuana, Baja California", -116.9390, 32.5495, 200),
    ("Plaza Río Tijuana", "Centro comercial",
     "Paseo de los Héroes, Zona Río, Tijuana, Baja California", -117.0222, 32.5278, 200),
    ("Centro - Avenida Revolución", "Zona turística",
     "Avenida Revolución, Zona Centro, Tijuana, Baja California", -117.0378, 32.5330, 200),
    ("Playas de Tijuana", "Zona turística",
     "Playas de Tijuana, Tijuana, Baja California", -117.1190, 32.5320, 250),
    ("Zona Industrial Mesa de Otay", "Zona industrial",
     "Parque industrial, Mesa de Otay, Tijuana, Baja California", -116.9550, 32.5480, 400),
    ("Base AxoMotor Tijuana", "Base operativa",
     "Zona Río, Tijuana, Baja California (ubicación ficticia)", -117.0150, 32.5320, 150),
]


def _square_wkt(longitude: float, latitude: float, half_size_m: float) -> str:
    d_lat = half_size_m / 111_320
    d_lon = half_size_m / (111_320 * math.cos(math.radians(latitude)))
    ring = [
        (longitude - d_lon, latitude - d_lat),
        (longitude + d_lon, latitude - d_lat),
        (longitude + d_lon, latitude + d_lat),
        (longitude - d_lon, latitude + d_lat),
        (longitude - d_lon, latitude - d_lat),
    ]
    coordinates = ", ".join(f"{x:.6f} {y:.6f}" for x, y in ring)
    return f"POLYGON(({coordinates}))"


def seed_locations(session: Session, ctx: SeedContext) -> None:
    for name, location_type, address, longitude, latitude, half_size in LOCATION_SPECS:
        ctx.locations.append(
            KnownLocation(
                name=name,
                type=location_type,
                address=address,
                location_area=WKTElement(
                    _square_wkt(longitude, latitude, half_size), srid=4326
                ),
                registered_at=random_between(
                    ctx.rng, ctx.start, ctx.start + timedelta(days=3)
                ),
            )
        )

    session.add_all(ctx.locations)
    session.flush()