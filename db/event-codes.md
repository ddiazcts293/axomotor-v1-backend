# AxoMotor - Códigos de eventos e incidentes

## Categorías

**Vehiculo:**
- [Dispositivo](#dispositivo)
- [Sensor](#sensor)
- [Rastreo GPS](#rastreogps)
- [Conexión móvil](#conexiónmóvil)
- [Acceso a sistema de vehículo](#accesoasistemadevehículo)

**Incidente:**
- [Mecánico](#mecánico)
- [Accidente](#accidente)
- [Carga](#carga)
- [Seguridad](#seguridad)
- [Condiciones de ruta](#condicionesderuta)
- [Conductor](#conductor)

## Códigos de Eventos de Vehículos

### Dispositivo

| Código         | Severidad  | Descripción |
| -------------- | ---------- | ----------- |
| `VE_DEV_RESET` | `info`     | Reinicio de dispositivo |
| `VE_DEV_DISCD` | `low`      | Dispositivo desconectado |
| `VE_DEV_TAMPR` | `critical` | Manipulación detectada |
| `VE_VID_STOPD` | `info`     | Grabación de video detenida |
| `VE_VID_START` | `info`     | Grabación de video iniciada |
| `VE_CAM_ERROR` | `medium`   | Fallo de cámara |
| `VE_BAT_LEVEL` | `info`     | Actualización de nivel de batería |
| `VE_BAT_CRTCL` | `medium`   | Nivel crítico de batería |
| `VE_STOR_FULL` | `high`     | Almacenamiento lleno |
| `VE_STOR_FAIL` | `high`     | Fallo de almacenamiento |

### Sensor

| Código         | Severidad | Descripción |
| -------------- | --------- | ----------- |
| `VE_MOV_START` | `info`    | Desplazamiento del vehículo iniciado |
| `VE_MOV_STOPD` | `info`    | Desplazamiento del vehículo terminado |
| `VE_PARKG_DET` | `info`    | Vehículo estacionado |
| `VE_ACTIV_DET` | `info`    | Actividad dentro del vehículo detectada |
| `VE_IMPCT_DET` | `medium`  | Impacto detectado |
| `VE_SHOCK_DET` | `low`     | Sacudida leve detectada |
| `VE_HARSH_ACC` | `low`     | Aceleración brusca detectada |
| `VE_HARSH_BRK` | `low`     | Frenado brusco detectado |
| `VE_HARSH_COR` | `low`     | Giro brusco detectado |

### Rastreo GPS

| Código         | Severidad | Descripción |
| -------------- | --------- | ----------- |
| `VE_GPSS_LOST` | `low`     | Señal GPS perdida |
| `VE_GPSS_REST` | `low`     | Señal GPS restaurada |

### Conexión móvil

| Código         | Severidad  | Descripción |
| -------------- | ---------- | ----------- |
| `VE_DATA_LOST` | `low`      | Conexión red móvil perdida |
| `VE_DATA_REST` | `low`      | Conexión red móvil restaurada |

### Acceso a sistema de vehículo

| Código         | Severidad | Descripción |
| -------------- | --------- | ----------- |
| `VE_ADMIN_ACC` | `info`    | Acceso de administrador registrado |
| `VE_DRIVR_ACC` | `info`    | Acceso de conductor detectado |

## Códigos de incidencias

### Mecánico

| Código         | Severidad  | Descripción |
| -------------- | ---------- | ----------- |
| `IN_FLAT_TIRE` | `medium`   | Ponchadura o daño en neumático |
| `IN_ENG_ISSUE` | `high`     | Falla mecánica en motor o transmisión |
| `IN_BRK_ISSUE` | `critical` | Falla crítica en sistema de frenos |
| `IN_ELEC_FAIL` | `high`     | Falla eléctrica o descarga de batería |
| `IN_OVERHEATS` | `high`     | Sobrecalentamiento del motor |
| `IN_FUEL_LEAK` | `critical` | Fuga de combustible o fluidos |
| `IN_EMPTY_TNK` | `medium`   | Vehículo sin combustible en ruta |

### Accidente

| Código         | Severidad  | Descripción |
| -------------- | ---------- | ----------- |
| `IN_CAR_ACCNT` | `critical` | Accidente vehicular grave |
| `IN_CAR_COLLN` | `critical` | Choque o colisión vehicular |
| `IN_OVERTURNS` | `critical` | Volcadura del vehículo |
| `IN_MINOR_HIT` | `medium`   | Percance vial menor sin lesionados |

### Carga

| Código         | Severidad  | Descripción |
| -------------- | ---------- | ----------- |
| `IN_CARGO_DMG` | `high`     | Daño parcial o total en la mercancía |
| `IN_CARGO_LST` | `high`     | Extravío o faltante de mercancía |
| `IN_SEAL_BROK` | `critical` | Sello de seguridad violado |
| `IN_TEMP_EXCD` | `high`     | Temperatura fuera de rango permitido |

### Seguridad

| Código         | Severidad  | Descripción |
| -------------- | ---------- | ----------- |
| `IN_CARGO_THF` | `critical` | Robo de mercancía / carga |
| `IN_VEH_THEFT` | `critical` | Robo de la unidad vehicular |
| `IN_HIJACKING` | `critical` | Asalto o secuestro en ruta |
| `IN_SOS_PANIC` | `critical` | Alerta de pánico activada por conductor |
| `IN_VANDALISM` | `medium`   | Daños intencionales a la unidad |
| `IN_GPS_TAMPR` | `critical` | Manipulación o bloqueo de GPS / cámaras |

### Condiciones de ruta

| Código         | Severidad | Descripción |
| -------------- | --------- | ----------- |
| `IN_ROAD_BLCK` | `medium`  | Bloqueo de carretera |
| `IN_HVY_TRAFF` | `low`     | Congestión vehicular severa |
| `IN_ROUTE_DEV` | `low`     | Desvío de ruta autorizado o forzoso |
| `IN_SEV_WEATH` | `medium`  | Condiciones climáticas adversas |
| `IN_ROAD_FLOD` | `high`    | Inundación o camino intransitable |

### Conductor

| Código         | Severidad  | Descripción |
| -------------- | ---------- | ----------- |
| `IN_DRV_FATIG` | `high`     | Indisposición física del conductor |
| `IN_MED_EMERG` | `critical` | Emergencia médica del conductor |
| `IN_TRAF_TICK` | `low`      | Infracción o multa de tránsito |
| `IN_POL_CHECK` | `low`      | Retén, inspección policial o aduanal |
| `IN_DOC_ISSUE` | `medium`   | Problema con documentación del vehículo |
| `IN_CLIENT_NA` | `low`      | Cliente ausente en punto de entrega |
| `IN_DELIV_REJ` | `medium`   | Entrega rechazada por el cliente |
| `IN_DELAY_ETA` | `low`      | Retraso estimado en hora de llegada |
| `IN_OTHER_INC` | `low`      | Otra incidencia operativa no clasificada |
