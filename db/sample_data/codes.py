from sqlmodel import Session, select

from models import EventCode
from models.enums import EventType

# Claves que usa el generador -> código oficial del catálogo (db/seed.py).
INCIDENT_KEYS = {
    "minor_hit": "IN_MINOR_HIT",
    "collision": "IN_CAR_COLLN",
    "crash": "IN_CAR_ACCNT",
    "heavy_traffic": "IN_HVY_TRAFF",
    "route_deviation": "IN_ROUTE_DEV",
    "delay_eta": "IN_DELAY_ETA",
    "police_check": "IN_POL_CHECK",
    "flat_tire": "IN_FLAT_TIRE",
    "road_block": "IN_ROAD_BLCK",
    "severe_weather": "IN_SEV_WEATH",
}

EVENT_KEYS = {
    "movement_start": "VE_MOV_START",
    "movement_stop": "VE_MOV_STOPD",
    "parked": "VE_PARKG_DET",
    "driver_access": "VE_DRIVR_ACC",
    "activity_detected": "VE_ACTIV_DET",
    "impact": "VE_IMPCT_DET",
    "harsh_brake": "VE_HARSH_BRK",
    "gps_lost": "VE_GPSS_LOST",
    "gps_restored": "VE_GPSS_REST",
    "data_lost": "VE_DATA_LOST",
    "data_restored": "VE_DATA_REST",
    "battery_critical": "VE_BAT_CRTCL",
    "battery_level": "VE_BAT_LEVEL",
    "device_disconnected": "VE_DEV_DISCD",
    "video_start": "VE_VID_START",
    "video_stop": "VE_VID_STOPD",
}


def load_code_catalog(session: Session) -> dict:
    """Lee el catálogo oficial de la base y verifica los códigos que usa el generador."""
    catalog = {entry.code: entry for entry in session.exec(select(EventCode)).all()}

    checks = (
        (INCIDENT_KEYS, (EventType.incident, EventType.both)),
        (EVENT_KEYS, (EventType.vehicle, EventType.both)),
    )
    problems = []
    for keys, allowed_types in checks:
        for code in keys.values():
            entry = catalog.get(code)
            if entry is None:
                problems.append(f"{code}: no existe en event_codes")
            elif entry.type not in allowed_types:
                problems.append(f"{code}: es de tipo {entry.type.value}")
            elif not entry.is_enabled:
                problems.append(f"{code}: está deshabilitado")

    if problems:
        raise RuntimeError(
            "El catálogo de códigos no coincide con lo que usa el generador:\n- "
            + "\n- ".join(problems)
        )
    return catalog