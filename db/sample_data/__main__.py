import sys

from sqlalchemy import text
from sqlmodel import Session, func, select

from db.database import engine
from db.seed import seed_catalog  # catálogo oficial de códigos (upsert)
from models import User

from .codes import load_code_catalog
from .common import new_context
from .incidents import seed_incidents_and_events
from .locations import seed_locations
from .trips import seed_trips
from .users import seed_alerts, seed_drivers, seed_users
from .vehicles import seed_devices, seed_services, seed_vehicles

# TRUNCATE ... CASCADE también vacía las tablas que dependen de estas
# (conductores, alertas, dispositivos, servicios, viajes, posiciones, incidentes, eventos).
# El catálogo event_codes no se toca.
RESET_TABLES = "users, vehicles, known_locations"


def reset_database() -> None:
    answer = input(
        f"Esto BORRARÁ los datos de: {RESET_TABLES} y todo lo relacionado. "
        "Escribe SI para continuar: "
    )
    if answer.strip() != "SI":
        print("Operación cancelada.")
        sys.exit(1)

    with engine.begin() as connection:
        connection.execute(text(f"TRUNCATE TABLE {RESET_TABLES} CASCADE"))


def main() -> None:
    if "--reset" in sys.argv:
        reset_database()

    seed_catalog()  # asegura que los códigos oficiales estén cargados

    with Session(engine) as session:
        existing_users = session.exec(select(func.count()).select_from(User)).one()
        if existing_users:
            print(
                "Seed cancelado: la tabla 'users' ya contiene datos. "
                "Usa una base de pruebas vacía o ejecuta con --reset."
            )
            sys.exit(1)

        catalog = load_code_catalog(session)  # falla antes de insertar nada si algo no coincide

        ctx = new_context()
        seed_users(session, ctx)
        seed_drivers(session, ctx)
        seed_alerts(session, ctx)
        seed_locations(session, ctx)
        seed_vehicles(session, ctx)
        seed_devices(session, ctx)
        seed_services(session, ctx)
        seed_trips(session, ctx)
        incident_count, event_count = seed_incidents_and_events(session, ctx, catalog)
        session.commit()

        print(
            f"Listo -> users: {len(ctx.users)}, drivers: {len(ctx.drivers)}, "
            f"user_alerts: {len(ctx.alerts)}, known_locations: {len(ctx.locations)}, "
            f"vehicles: {len(ctx.vehicles)}, vehicle_devices: {len(ctx.devices)}, "
            f"vehicle_services: {len(ctx.services)}, trips: {len(ctx.trips)}, "
            f"positions: {len(ctx.positions)}, incidents: {incident_count}, "
            f"vehicle_events: {event_count}"
        )


if __name__ == "__main__":
    main()