from datetime import timedelta

from sqlmodel import Session

from core.security import get_password_hash
from models import Driver, User, UserAlert
from models.enums import AlertType, LicenseClass, UserRole

from .common import SeedContext, random_between

DEFAULT_PASSWORD = "Test1234"
FIXED_USERNAMES = {"Danny", "Panky"}
EXPIRED_LICENSE_USERNAME = "saguilar"
DISABLED_DRIVER_USERNAME = "hvalenzuela"

# (username, first_name, last_name, role, password; None usa DEFAULT_PASSWORD)
USER_SPECS = [
    ("Danny", "Danny", None, UserRole.admin, "admin123"),
    ("Panky", "Panky", None, UserRole.driver, "Panky123"),
    ("lortega", "Luis", "Ortega", UserRole.agent, None),
    ("pbeltran", "Paola", "Beltrán", UserRole.agent, None),
    ("rsandoval", "Ricardo", "Sandoval", UserRole.agent, None),
    ("jmedina", "Jorge", "Medina", UserRole.driver, None),
    ("avillalobos", "Andrea", "Villalobos", UserRole.driver, None),
    ("cnunez", "Carlos", "Núñez", UserRole.driver, None),
    ("dquintero", "Daniela", "Quintero", UserRole.driver, None),
    ("marojas", "Miguel Ángel", "Rojas", UserRole.driver, None),
    ("saguilar", "Sofía", "Aguilar", UserRole.driver, None),
    ("hvalenzuela", "Héctor", "Valenzuela", UserRole.driver, None),
]

LICENSE_CLASSES = [
    LicenseClass.B, LicenseClass.B, LicenseClass.B,
    LicenseClass.C, LicenseClass.C,
    LicenseClass.D, LicenseClass.E,
]

# Alertas por usuario: las de Danny y Panky sirven para probar la app con las cuentas fijas
ALERT_COUNTS = {"Danny": 9, "Panky": 7, "lortega": 3, "pbeltran": 3, "rsandoval": 3}
EXTRA_DRIVER_ALERTS = 5

ALERT_WEIGHTS = {
    AlertType.account: 2,
    AlertType.system: 3,
    AlertType.vehicle_incident: 2,
    AlertType.trip_incident: 2,
    AlertType.incident_update: 2,
}

ALERT_TEMPLATES = {
    AlertType.account: [
        ("Inicio de sesión detectado", "Se detectó un inicio de sesión en tu cuenta desde un nuevo dispositivo."),
        ("Contraseña actualizada", "La contraseña de tu cuenta se actualizó correctamente."),
    ],
    AlertType.system: [
        ("Mantenimiento programado", "El sistema tendrá una breve ventana de mantenimiento esta noche. Podría haber intermitencias."),
        ("Sincronización completada", "Los dispositivos de tus vehículos se sincronizaron correctamente."),
    ],
    AlertType.vehicle_incident: [
        ("Posible intrusión en vehículo", "Se detectó actividad inusual en un vehículo estacionado. Revisa los detalles."),
        ("Impacto detectado en vehículo", "El módulo del vehículo registró un impacto moderado. Verifica el estado del conductor."),
    ],
    AlertType.trip_incident: [
        ("Incidente durante un viaje", "Se reportó una incidencia en un viaje en curso. Revisa los detalles."),
        ("Señal GPS perdida", "Se perdió la señal GPS de un vehículo durante su viaje."),
    ],
    AlertType.incident_update: [
        ("Incidente en revisión", "Un incidente que registraste pasó a revisión por parte de un agente."),
        ("Incidente cerrado", "Un incidente que registraste fue cerrado."),
    ],
}


def seed_users(session: Session, ctx: SeedContext) -> None:
    default_hash = get_password_hash(DEFAULT_PASSWORD)

    for index, (username, first_name, last_name, role, password) in enumerate(USER_SPECS):
        registered_at = random_between(ctx.rng, ctx.start, ctx.start + timedelta(days=7))
        if username in FIXED_USERNAMES or ctx.rng.random() < 0.8:
            logged_in_at = random_between(ctx.rng, ctx.now - timedelta(days=30), ctx.now)
        else:
            logged_in_at = None

        ctx.users.append(
            User(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=f"{username.lower()}@example.com",
                phone_number=f"+52 664-555-{index + 100:04d}",
                hashed_password=get_password_hash(password) if password else default_hash,
                role=role,
                registered_at=registered_at,
                updated_at=registered_at,
                logged_in_at=logged_in_at,
            )
        )

    session.add_all(ctx.users)
    session.flush()


def seed_drivers(session: Session, ctx: SeedContext) -> None:
    today = ctx.now.date()

    for user in (u for u in ctx.users if u.role == UserRole.driver):
        if user.username == EXPIRED_LICENSE_USERNAME:
            expires = today - timedelta(days=ctx.rng.randint(10, 60))
            issued = expires - timedelta(days=3 * 365)
        else:
            issued = today - timedelta(days=ctx.rng.randint(30, 730))
            expires = issued + timedelta(days=365 * ctx.rng.choice((3, 5)))

        registered_at = user.registered_at + timedelta(hours=ctx.rng.randint(1, 48))
        ctx.drivers.append(
            Driver(
                user_id=user.user_id,
                license_number=f"BC{ctx.rng.randint(10_000_000, 99_999_999)}",
                license_class=ctx.rng.choice(LICENSE_CLASSES),
                license_iss_date=issued,
                license_exp_date=expires,
                is_active=False,
                is_enabled=user.username != DISABLED_DRIVER_USERNAME,
                registered_at=registered_at,
                updated_at=registered_at,
            )
        )

    session.add_all(ctx.drivers)
    session.flush()


def _make_alert(ctx: SeedContext, user: User) -> UserAlert:
    alert_type = ctx.rng.choices(list(ALERT_WEIGHTS), weights=list(ALERT_WEIGHTS.values()))[0]
    title, content = ctx.rng.choice(ALERT_TEMPLATES[alert_type])
    created_at = random_between(ctx.rng, max(user.registered_at, ctx.start), ctx.now)
    age_days = (ctx.now - created_at).days
    is_read = ctx.rng.random() < (0.7 if age_days > 14 else 0.3)

    return UserAlert(
        user_id=user.user_id,
        title=title,
        content=content,
        type=alert_type,
        is_read=is_read,
        created_at=created_at,
    )


def seed_alerts(session: Session, ctx: SeedContext) -> None:
    by_username = {user.username: user for user in ctx.users}
    plan = [(by_username[name], count) for name, count in ALERT_COUNTS.items()]

    extra_pool = [
        u for u in ctx.users
        if u.role == UserRole.driver and u.username not in ALERT_COUNTS
    ]
    plan += [(ctx.rng.choice(extra_pool), 1) for _ in range(EXTRA_DRIVER_ALERTS)]

    for user, count in plan:
        ctx.alerts.extend(_make_alert(ctx, user) for _ in range(count))

    session.add_all(ctx.alerts)
    session.flush()