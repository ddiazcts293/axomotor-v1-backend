from datetime import timedelta

from sqlmodel import Session

from models import Vehicle, VehicleDevice, VehicleService
from models.enums import (
    UserRole,
    VehicleDeviceType,
    VehicleServiceStatus,
    VehicleStatus,
    VehicleType,
)

from .common import SeedContext, random_between

PLATE_LETTERS = "ABCDEFGHJKLMNPRSTUVWXYZ"
VIN_CHARS = "ABCDEFGHJKLMNPRSTUVWXYZ0123456789"

# (marca, modelo, año, tipo, estado)
VEHICLE_SPECS = [
    ("Nissan", "NP300", 2021, VehicleType.pickup, VehicleStatus.operative),
    ("Ford", "Transit", 2020, VehicleType.van, VehicleStatus.in_use),
    ("Isuzu", "ELF 300", 2018, VehicleType.truck, VehicleStatus.under_maintenance),
]

# (tipo de dispositivo, etiqueta)
DEVICE_LAYOUT = [
    (VehicleDeviceType.hub, "HUB"),
    (VehicleDeviceType.node, "NODO-1"),
    (VehicleDeviceType.node, "NODO-2"),
]

# (índice de vehículo, nombre, descripción, estado, días respecto a hoy, próximo servicio en días)
SERVICE_SPECS = [
    (0, "Cambio de aceite y filtros",
     "Cambio de aceite sintético, filtro de aceite y filtro de aire.",
     VehicleServiceStatus.completed, -62, 180),
    (0, "Revisión de frenos",
     "Inspección y ajuste del sistema de frenos.",
     VehicleServiceStatus.pending, 8, None),
    (1, "Rotación y balanceo de llantas",
     "Rotación, balanceo y revisión de presión de las cuatro llantas.",
     VehicleServiceStatus.completed, -41, 120),
    (1, "Alineación y suspensión",
     "Servicio cancelado por reasignación del vehículo a una ruta.",
     VehicleServiceStatus.cancelled, -15, None),
    (2, "Afinación mayor",
     "Afinación completa: bujías, filtros y revisión de inyectores.",
     VehicleServiceStatus.completed, -75, 150),
    (2, "Reparación del sistema de frenos",
     "Reemplazo de balatas y rectificación de discos en taller.",
     VehicleServiceStatus.in_progress, -2, 90),
]


def _unique(generate, used: set) -> str:
    while True:
        value = generate()
        if value not in used:
            used.add(value)
            return value


def seed_vehicles(session: Session, ctx: SeedContext) -> None:
    rng = ctx.rng
    plates, registrations, vins = set(), set(), set()

    def plate() -> str:
        letters = "".join(rng.choices(PLATE_LETTERS, k=3))
        return f"{letters}-{rng.randint(0, 999):03d}-{rng.choice(PLATE_LETTERS)}"

    def registration() -> str:
        return f"BC{rng.randint(10**13, 10**14 - 1)}"

    def vin() -> str:
        return "3" + "".join(rng.choices(VIN_CHARS, k=16))

    for brand, model, year, vehicle_type, vehicle_status in VEHICLE_SPECS:
        registered_at = random_between(rng, ctx.start, ctx.start + timedelta(days=14))
        ctx.vehicles.append(
            Vehicle(
                plate_number=_unique(plate, plates),
                reg_number=_unique(registration, registrations),
                series_vin=_unique(vin, vins),
                brand=brand,
                model=model,
                year=year,
                type=vehicle_type,
                status=vehicle_status,
                registered_at=registered_at,
                updated_at=registered_at,
            )
        )

    session.add_all(ctx.vehicles)
    session.flush()


def seed_devices(session: Session, ctx: SeedContext) -> None:
    rng = ctx.rng
    serials: set = set()

    for number, vehicle in enumerate(ctx.vehicles, start=1):
        for device_type, label in DEVICE_LAYOUT:
            is_hub = device_type == VehicleDeviceType.hub
            is_new = vehicle.status == VehicleStatus.under_maintenance and label == "NODO-2"
            low_battery = vehicle.status == VehicleStatus.in_use and label == "NODO-2"

            if is_new:
                # Nodo recién instalado que todavía no transmite
                battery_level, is_active = None, False
                registered_at = ctx.now - timedelta(days=2)
                updated_at = registered_at
            else:
                battery_level = 12 if low_battery else (
                    rng.randint(90, 100) if is_hub else rng.randint(40, 100)
                )
                is_active = True
                registered_at = vehicle.registered_at + timedelta(hours=rng.randint(1, 72))
                updated_at = ctx.now - timedelta(minutes=rng.randint(1, 120))

            ctx.devices.append(
                VehicleDevice(
                    vehicle_id=vehicle.vehicle_id,
                    serial_number=_unique(
                        lambda: f"AXM{rng.randint(10**8, 10**9 - 1)}", serials
                    ),
                    tag=f"V{number}-{label}",
                    type=device_type,
                    battery_level=battery_level,
                    is_active=is_active,
                    is_enabled=True,
                    registered_at=registered_at,
                    updated_at=updated_at,
                )
            )

    session.add_all(ctx.devices)
    session.flush()


def seed_services(session: Session, ctx: SeedContext) -> None:
    rng = ctx.rng
    staff = [u for u in ctx.users if u.role in (UserRole.admin, UserRole.agent)]

    for index, name, description, status, day_offset, next_offset in SERVICE_SPECS:
        vehicle = ctx.vehicles[index]

        date = (ctx.now + timedelta(days=day_offset)).replace(
            hour=rng.randint(8, 16), minute=0, second=0
        )
        date = max(date, vehicle.registered_at + timedelta(days=3))

        if date > ctx.now:
            registered_at = ctx.now - timedelta(days=rng.randint(1, 5))
        else:
            registered_at = max(
                date - timedelta(days=rng.randint(1, 5)),
                vehicle.registered_at + timedelta(days=1),
            )

        completed = status == VehicleServiceStatus.completed
        updated_at = (
            date + timedelta(hours=3)
            if completed or status == VehicleServiceStatus.in_progress
            else registered_at
        )

        ctx.services.append(
            VehicleService(
                vehicle_id=vehicle.vehicle_id,
                name=name,
                description=description,
                status=status,
                date=date,
                next_service_date=date + timedelta(days=next_offset) if next_offset else None,
                created_by_id=rng.choice(staff).user_id,
                authorized_by_id=rng.choice(staff).user_id if completed else None,
                registered_at=registered_at,
                updated_at=updated_at,
            )
        )

    session.add_all(ctx.services)
    session.flush()