import logging
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlmodel import Session, SQLModel

from .database import engine
import models  # Registra todos los modelos en SQLModel.metadata
from models import (
    EventCode,
    EventCategory,
    EventType,
    SeverityLevel
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)

INITIAL_CATALOG: list[dict] = [
    # Evento de vehículos
    {"code": "VE_DEV_RESET", "type": EventType.vehicle, "category": EventCategory.device, "severity": SeverityLevel.info, "description": "Reinicio de dispositivo"},
    {"code": "VE_DEV_DISCD", "type": EventType.vehicle, "category": EventCategory.device, "severity": SeverityLevel.low, "description": "Dispositivo desconectado"},
    {"code": "VE_DEV_TAMPR", "type": EventType.vehicle, "category": EventCategory.device, "severity": SeverityLevel.critical, "description": "Manipulación detectada"},
    {"code": "VE_VID_STOPD", "type": EventType.vehicle, "category": EventCategory.device, "severity": SeverityLevel.info, "description": "Grabación de video detenida"},
    {"code": "VE_VID_START", "type": EventType.vehicle, "category": EventCategory.device, "severity": SeverityLevel.info, "description": "Grabación de video iniciada"},
    {"code": "VE_CAM_ERROR", "type": EventType.vehicle, "category": EventCategory.device, "severity": SeverityLevel.medium, "description": "Fallo de cámara"},
    {"code": "VE_BAT_LEVEL", "type": EventType.vehicle, "category": EventCategory.device, "severity": SeverityLevel.info, "description": "Actualización de nivel de batería"},
    {"code": "VE_BAT_CRTCL", "type": EventType.vehicle, "category": EventCategory.device, "severity": SeverityLevel.medium, "description": "Nivel crítico de batería"},
    {"code": "VE_STOR_FULL", "type": EventType.vehicle, "category": EventCategory.device, "severity": SeverityLevel.high, "description": "Almacenamiento lleno"},
    {"code": "VE_STOR_FAIL", "type": EventType.vehicle, "category": EventCategory.device, "severity": SeverityLevel.high, "description": "Fallo de almacenamiento"},
    {"code": "VE_MOV_START", "type": EventType.vehicle, "category": EventCategory.sensor, "severity": SeverityLevel.info, "description": "Desplazamiento del vehículo iniciado"},
    {"code": "VE_MOV_STOPD", "type": EventType.vehicle, "category": EventCategory.sensor, "severity": SeverityLevel.info, "description": "Desplazamiento del vehículo terminado"},
    {"code": "VE_PARKG_DET", "type": EventType.vehicle, "category": EventCategory.sensor, "severity": SeverityLevel.info, "description": "Vehículo estacionado"},
    {"code": "VE_ACTIV_DET", "type": EventType.vehicle, "category": EventCategory.sensor, "severity": SeverityLevel.info, "description": "Actividad dentro del vehículo detectada"},
    {"code": "VE_IMPCT_DET", "type": EventType.vehicle, "category": EventCategory.sensor, "severity": SeverityLevel.medium, "description": "Impacto detectado"},
    {"code": "VE_SHOCK_DET", "type": EventType.vehicle, "category": EventCategory.sensor, "severity": SeverityLevel.low, "description": "Sacudida leve detectada"},
    {"code": "VE_HARSH_ACC", "type": EventType.vehicle, "category": EventCategory.sensor, "severity": SeverityLevel.low, "description": "Aceleración brusca detectada"},
    {"code": "VE_HARSH_BRK", "type": EventType.vehicle, "category": EventCategory.sensor, "severity": SeverityLevel.low, "description": "Frenado brusco detectado"},
    {"code": "VE_HARSH_COR", "type": EventType.vehicle, "category": EventCategory.sensor, "severity": SeverityLevel.low, "description": "Giro brusco detectado"},
    {"code": "VE_GPSS_LOST", "type": EventType.vehicle, "category": EventCategory.tracking, "severity": SeverityLevel.low, "description": "Señal GPS perdida"},
    {"code": "VE_GPSS_REST", "type": EventType.vehicle, "category": EventCategory.tracking, "severity": SeverityLevel.low, "description": "Señal GPS restaurada"},
    {"code": "VE_DATA_LOST", "type": EventType.vehicle, "category": EventCategory.network, "severity": SeverityLevel.low, "description": "Conexión red móvil perdida"},
    {"code": "VE_DATA_REST", "type": EventType.vehicle, "category": EventCategory.network, "severity": SeverityLevel.low, "description": "Conexión red móvil restaurada"},
    {"code": "VE_ADMIN_ACC", "type": EventType.vehicle, "category": EventCategory.access, "severity": SeverityLevel.info, "description": "Acceso de administrador registrado"},
    {"code": "VE_DRIVR_ACC", "type": EventType.vehicle, "category": EventCategory.access, "severity": SeverityLevel.info, "description": "Acceso de conductor detectado"},
    # Incidencias
    {"code": "IN_FLAT_TIRE", "type": EventType.incident, "category": EventCategory.mechanical, "severity": SeverityLevel.medium, "description": "Ponchadura o daño en neumático"},
    {"code": "IN_ENG_ISSUE", "type": EventType.incident, "category": EventCategory.mechanical, "severity": SeverityLevel.high, "description": "Falla mecánica en motor o transmisión"},
    {"code": "IN_BRK_ISSUE", "type": EventType.incident, "category": EventCategory.mechanical, "severity": SeverityLevel.critical, "description": "Falla crítica en sistema de frenos"},
    {"code": "IN_ELEC_FAIL", "type": EventType.incident, "category": EventCategory.mechanical, "severity": SeverityLevel.high, "description": "Falla eléctrica o descarga de batería"},
    {"code": "IN_OVERHEATS", "type": EventType.incident, "category": EventCategory.mechanical, "severity": SeverityLevel.high, "description": "Sobrecalentamiento del motor"},
    {"code": "IN_FUEL_LEAK", "type": EventType.incident, "category": EventCategory.mechanical, "severity": SeverityLevel.critical, "description": "Fuga de combustible o fluidos"},
    {"code": "IN_EMPTY_TNK", "type": EventType.incident, "category": EventCategory.mechanical, "severity": SeverityLevel.medium, "description": "Vehículo sin combustible en ruta"},
    {"code": "IN_CAR_ACCNT", "type": EventType.incident, "category": EventCategory.accident, "severity": SeverityLevel.critical, "description": "Accidente vehicular grave"},
    {"code": "IN_CAR_COLLN", "type": EventType.incident, "category": EventCategory.accident, "severity": SeverityLevel.critical, "description": "Choque o colisión vehicular"},
    {"code": "IN_OVERTURNS", "type": EventType.incident, "category": EventCategory.accident, "severity": SeverityLevel.critical, "description": "Volcadura del vehículo"},
    {"code": "IN_MINOR_HIT", "type": EventType.incident, "category": EventCategory.accident, "severity": SeverityLevel.medium, "description": "Percance vial menor sin lesionados"},
    {"code": "IN_CARGO_DMG", "type": EventType.incident, "category": EventCategory.cargo, "severity": SeverityLevel.high, "description": "Daño parcial o total en la mercancía"},
    {"code": "IN_CARGO_LST", "type": EventType.incident, "category": EventCategory.cargo, "severity": SeverityLevel.high, "description": "Extravío o faltante de mercancía"},
    {"code": "IN_SEAL_BROK", "type": EventType.incident, "category": EventCategory.cargo, "severity": SeverityLevel.critical, "description": "Sello de seguridad violado"},
    {"code": "IN_TEMP_EXCD", "type": EventType.incident, "category": EventCategory.cargo, "severity": SeverityLevel.high, "description": "Temperatura fuera de rango permitido"},
    {"code": "IN_CARGO_THF", "type": EventType.incident, "category": EventCategory.security, "severity": SeverityLevel.critical, "description": "Robo de mercancía / carga"},
    {"code": "IN_VEH_THEFT", "type": EventType.incident, "category": EventCategory.security, "severity": SeverityLevel.critical, "description": "Robo de la unidad vehicular"},
    {"code": "IN_HIJACKING", "type": EventType.incident, "category": EventCategory.security, "severity": SeverityLevel.critical, "description": "Asalto o secuestro en ruta"},
    {"code": "IN_SOS_PANIC", "type": EventType.incident, "category": EventCategory.security, "severity": SeverityLevel.critical, "description": "Alerta de pánico activada por conductor"},
    {"code": "IN_VANDALISM", "type": EventType.incident, "category": EventCategory.security, "severity": SeverityLevel.medium, "description": "Daños intencionales a la unidad"},
    {"code": "IN_GPS_TAMPR", "type": EventType.incident, "category": EventCategory.security, "severity": SeverityLevel.critical, "description": "Manipulación o bloqueo de GPS / cámaras"},
    {"code": "IN_ROAD_BLCK", "type": EventType.incident, "category": EventCategory.route, "severity": SeverityLevel.medium, "description": "Bloqueo de carretera"},
    {"code": "IN_HVY_TRAFF", "type": EventType.incident, "category": EventCategory.route, "severity": SeverityLevel.low, "description": "Congestión vehicular severa"},
    {"code": "IN_ROUTE_DEV", "type": EventType.incident, "category": EventCategory.route, "severity": SeverityLevel.low, "description": "Desvío de ruta autorizado o forzoso"},
    {"code": "IN_SEV_WEATH", "type": EventType.incident, "category": EventCategory.route, "severity": SeverityLevel.medium, "description": "Condiciones climáticas adversas"},
    {"code": "IN_ROAD_FLOD", "type": EventType.incident, "category": EventCategory.route, "severity": SeverityLevel.high, "description": "Inundación o camino intransitable"},
    {"code": "IN_DRV_FATIG", "type": EventType.incident, "category": EventCategory.driver, "severity": SeverityLevel.high, "description": "Indisposición física del conductor"},
    {"code": "IN_MED_EMERG", "type": EventType.incident, "category": EventCategory.driver, "severity": SeverityLevel.critical, "description": "Emergencia médica del conductor"},
    {"code": "IN_TRAF_TICK", "type": EventType.incident, "category": EventCategory.driver, "severity": SeverityLevel.low, "description": "Infracción o multa de tránsito"},
    {"code": "IN_POL_CHECK", "type": EventType.incident, "category": EventCategory.driver, "severity": SeverityLevel.low, "description": "Retén, inspección policial o aduanal"},
    {"code": "IN_DOC_ISSUE", "type": EventType.incident, "category": EventCategory.driver, "severity": SeverityLevel.medium, "description": "Problema con documentación del vehículo"},
    {"code": "IN_CLIENT_NA", "type": EventType.incident, "category": EventCategory.driver, "severity": SeverityLevel.low, "description": "Cliente ausente en punto de entrega"},
    {"code": "IN_DELIV_REJ", "type": EventType.incident, "category": EventCategory.driver, "severity": SeverityLevel.medium, "description": "Entrega rechazada por el cliente"},
    {"code": "IN_DELAY_ETA", "type": EventType.incident, "category": EventCategory.driver, "severity": SeverityLevel.low, "description": "Retraso estimado en hora de llegada"},
    {"code": "IN_OTHER_INC", "type": EventType.incident, "category": EventCategory.other, "severity": SeverityLevel.low, "description": "Otra incidencia operativa no clasificada"},
]


def seed_catalog():
    # 1. Validación preventiva de longitud fija (12 caracteres) antes de tocar la BD
    for item in INITIAL_CATALOG:
        if len(item["code"]) != 12:
            raise ValueError(f"El código '{item['code']}' debe medir exactamente 12 caracteres.")
        item.setdefault("is_enabled", True)

    # 2. Asegura que las tablas existan si es un contenedor recién creado
    SQLModel.metadata.create_all(engine)

    # 3. Upsert masivo: inserta nuevos y actualiza descripción/severidad si ya existían
    with Session(engine) as session:
        stmt = pg_insert(EventCode).values(INITIAL_CATALOG)
        stmt = stmt.on_conflict_do_update(
            index_elements=["code"],
            set_={
                "type": stmt.excluded.type,
                "category": stmt.excluded.category,
                "severity": stmt.excluded.severity,
                "description": stmt.excluded.description,
            },
        )
        session.exec(stmt)
        session.commit()
        logger.info("Catálogo sincronizado correctamente (%d registros).", len(INITIAL_CATALOG))


if __name__ == "__main__":
    seed_catalog()
