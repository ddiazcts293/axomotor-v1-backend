# Datos de ejemplo de AxoMotor (`db/sample_data`)

Script de Python que puebla la base de datos de **pruebas** con información realista (Tijuana, Baja California, últimos 90 días) para probar la API, la plataforma web y la app móvil.

> ⚠️ **Úsalo solo en bases de pruebas.** La opción `--reset` borra datos y las cuentas incluidas tienen contraseñas de prueba conocidas.

---

## Requisitos

- Entorno virtual del proyecto activo y archivo `.env` configurado.
- Base de datos PostgreSQL con la extensión **PostGIS** habilitada.
- Esquema creado y al día: `alembic upgrade head` (o el mecanismo que uses con `USE_ALEMBIC`).
- Rama actualizada con `main`: el script depende de los modelos actuales, incluida la tabla unificada `event_codes`.

## Uso

Desde la **raíz del proyecto**:

```bash
# Base de pruebas vacía
python -m db.sample_data

# Borra los datos existentes (pide confirmación) y vuelve a generarlos
python -m db.sample_data --reset
```

Con `--reset` el script pide escribir `SI` antes de continuar. Vacía `users`, `vehicles` y `known_locations` junto con todo lo que depende de ellas (conductores, alertas, dispositivos, servicios, viajes, posiciones, incidentes y eventos). **No** toca el catálogo `event_codes`.

Si la tabla `users` ya contiene datos y no usas `--reset`, el script se detiene sin modificar nada.

Salida esperada (las cantidades de `positions`, `incidents` y `vehicle_events` varían un poco):

```
Listo -> users: 12, drivers: 8, user_alerts: 30, known_locations: 8, vehicles: 3,
vehicle_devices: 9, vehicle_services: 6, trips: 10, positions: ~100, incidents: ~13, vehicle_events: ~50
```

Todo se guarda en **una sola transacción**: si algo falla, no queda nada a medias.

## Relación con `db/seed.py`

El catálogo oficial de códigos (60 códigos: 25 de eventos de vehículo y 35 de incidencias) se carga con `db/seed.py`.

- `sample_data` ejecuta `seed_catalog()` automáticamente al iniciar, así que **no necesitas correr `db.seed` antes**. El proceso es un *upsert*, por lo que repetirlo es seguro.
- Antes de insertar datos, el script verifica que cada código que usa exista en `event_codes`, sea del tipo correcto (incidentes: `INCIDENT` o `BOTH`; eventos: `VEHICLE` o `BOTH`) y esté habilitado. Si algo no coincide, se detiene con un mensaje claro.
- No renombres esta carpeta a `db/seed/`: chocaría con `db/seed.py` y Python ejecutaría el paquete en lugar del archivo.

## Cuentas de prueba

| Usuario | Contraseña | Rol | Uso sugerido |
| --- | --- | --- | --- |
| `Danny` | `admin123` | Administrador | Ver y administrar todo |
| `Panky` | `Panky123` | Conductor | Tiene el viaje en curso y alertas para la app |
| `lortega`, `pbeltran`, `rsandoval` | `Test1234` | Agentes | Revisar y cerrar incidentes |
| `jmedina`, `avillalobos`, `cnunez`, `dquintero`, `marojas` | `Test1234` | Conductores | Viajes históricos |
| `saguilar` | `Test1234` | Conductor | **Licencia vencida** (caso de prueba) |
| `hvalenzuela` | `Test1234` | Conductor | **Deshabilitado** (caso de prueba) |

- El inicio de sesión distingue mayúsculas: escribe exactamente `Danny` y `Panky`.
- Correos: `<usuario en minúsculas>@example.com`. Teléfonos ficticios: `+52 664-555-01XX`.

> Si el repositorio es público, considera quitar esta sección o cambiar las contraseñas.

## Qué datos genera

| Entidad | Cantidad | Detalle |
| --- | --- | --- |
| `users` | 12 | 1 administrador, 3 agentes, 8 conductores |
| `drivers` | 8 | Un perfil por cada usuario conductor |
| `user_alerts` | 30 | Repartidas entre `Danny`, `Panky`, agentes y algunos conductores; ~36 % sin leer |
| `known_locations` | 8 | Puntos reales de Tijuana con polígonos pequeños (ver abajo) |
| `vehicles` | 3 | Nissan NP300 (`OPERATIVE`), Ford Transit (`IN_USE`), Isuzu ELF 300 (`UNDER_MAINTENANCE`) |
| `vehicle_devices` | 9 | 1 concentrador (`HUB`) y 2 nodos (`NODE`) por vehículo |
| `vehicle_services` | 6 | Completados, pendiente, cancelado y en progreso |
| `trips` | 10 | 5 `FINISHED`, 1 `ABORTED`, 1 `CANCELLED`, 1 `ON_ROUTE`, 1 `DELAYED`, 1 `PLANNED` |
| `positions` | ~100 | Entre 10 y 20 por viaje con recorrido (~1 cada 1.5 min) y 4 por vehículo estacionado |
| `incidents` | ~13 | 0 a 3 por viaje con recorrido |
| `vehicle_events` | ~50 | Eventos de viaje, sensores, señal, batería y evidencia en video |

Ubicaciones conocidas: Aeropuerto Internacional de Tijuana, Garita El Chaparral, Garita Otay, Plaza Río Tijuana, Centro (Avenida Revolución), Playas de Tijuana, Zona Industrial Mesa de Otay y **Base AxoMotor Tijuana** (esta última es ficticia). Las coordenadas son aproximadas (±300 m).

## Casos de prueba incluidos

- **Conductor** con licencia vencida (`saguilar`) y otro deshabilitado (`hvalenzuela`): no tienen viajes.
- **Vehículo en mantenimiento** con un servicio `IN_PROGRESS` y un nodo recién instalado, sin batería reportada y desconectado.
- **Vehículo en uso** con un viaje `ON_ROUTE` de `Panky` (queda `is_active = true`) y un nodo con batería crítica (12 %).
- **Viaje retrasado** (`DELAYED`): debía salir hace 15 minutos y aún no arranca.
- **Viaje abortado** con un par de incidentes encadenados: choque (`IN_CAR_COLLN`) y accidente grave (`IN_CAR_ACCNT`, con `related_incident_id` apuntando al primero).
- **Viaje cancelado** (sin salida real ni posiciones) y **viaje planeado** para mañana.
- **Servicios** en todos los estados: los completados traen `authorized_by`; los demás, no.
- **Intrusión nocturna** en la pickup estacionada (`VE_ACTIV_DET`).

## Reglas de coherencia

- Fechas hacia atrás desde el momento de la ejecución; ningún registro es anterior a su vehículo o conductor.
- `created_at`, `registered_at` y `updated_at` se asignan explícitamente en el pasado.
- `started_at`, `finished_at`, `reviewed_at` y `closed_at` siguen las mismas reglas que la API.
- Sin viajes traslapados por vehículo ni por conductor; solo conductores habilitados con licencia vigente y ya emitida.
- `distance` y `average_speed` se **calculan a partir de las posiciones simuladas**; la velocidad de cada posición sale del tramo recorrido. Así lo haría el consumidor MQTT.
- Las posiciones empiezan dentro del polígono de origen y, en viajes terminados, acaban dentro del de destino.
- Incidentes: se registran en el momento y lugar de una posición real del viaje; 80 % los registra el conductor del viaje y 20 % un agente. Los recientes quedan abiertos y los antiguos tienden a estar cerrados. Un 25 % de los incidentes de conductores los revisa el propio conductor.
- La prioridad del incidente se deriva de la severidad del código (`CRITICAL` y `HIGH` → alta, `MEDIUM` → media, `LOW` e `INFO` → baja).
- Los impactos generan su evento `VE_IMPCT_DET` unos segundos antes del incidente, seguido de grabación de video.
- Coordenadas siempre en orden **longitud, latitud** (`WKTElement` con `POLYGON` para ubicaciones y `POINT` para posiciones, SRID 4326).

## Reproducibilidad

El generador usa una semilla fija (`SEED` en `common.py`), así que todos obtienen el **mismo contenido**. Las fechas absolutas se desplazan según el día en que se ejecute, porque se calculan hacia atrás desde ese momento.

## Estructura

| Archivo | Responsabilidad |
| --- | --- |
| `__main__.py` | Punto de entrada: opciones, protección contra datos existentes y orden de ejecución |
| `common.py` | Semilla, contexto compartido y utilidades de fechas |
| `users.py` | Usuarios, conductores y alertas |
| `locations.py` | Ubicaciones conocidas (polígonos) |
| `vehicles.py` | Vehículos, dispositivos y servicios |
| `trips.py` | Viajes y posiciones |
| `codes.py` | Traducción de claves del generador a códigos oficiales y validación contra la base |
| `incidents.py` | Incidentes y eventos de vehículo |

## Personalización

| Quieres cambiar... | Dónde |
| --- | --- |
| Rango de fechas (por defecto 90 días) | `HISTORY_DAYS` en `common.py` |
| Contenido generado | `SEED` en `common.py` |
| Cuentas y roles | `USER_SPECS` en `users.py` |
| Cantidad de alertas | `ALERT_COUNTS` y `EXTRA_DRIVER_ALERTS` en `users.py` |
| Vehículos (agregar uno genera sus dispositivos solo) | `VEHICLE_SPECS` en `vehicles.py` |
| Servicios | `SERVICE_SPECS` en `vehicles.py` |
| Ubicaciones | `LOCATION_SPECS` en `locations.py` |
| Viajes históricos | `HISTORICAL_PLAN` en `trips.py` |
| Tipos y probabilidad de incidentes | `GENERIC_KEYS` y `DESCRIPTIONS` en `incidents.py` |

Al agregar vehículos o viajes, recuerda que cada viaje histórico necesita un vehículo del estado indicado en el plan.

## Si cambia el catálogo de códigos

El generador no usa códigos escritos a mano en el código de datos, sino **claves** (`crash`, `gps_lost`...) que `codes.py` traduce:

1. Si cambia o se elimina un código oficial, actualiza `INCIDENT_KEYS` o `EVENT_KEYS` en `codes.py`.
2. Si agregas un tipo de incidente nuevo, añade su clave a `INCIDENT_KEYS`, sus textos a `DESCRIPTIONS` y su peso a `GENERIC_KEYS`.
3. Ejecuta `python -m db.sample_data --reset`. Si falta algún código o no coincide el tipo, el script lo indica antes de insertar nada.

## Problemas frecuentes

| Síntoma | Causa probable | Solución |
| --- | --- | --- |
| `Seed cancelado: la tabla 'users' ya contiene datos` | La base ya tiene datos | Usa `--reset` |
| `El catálogo de códigos no coincide con lo que usa el generador` | Falta un código, es de otro tipo o está deshabilitado | Revisa `db/seed.py` y las claves de `codes.py` |
| `relation "..." does not exist` | Esquema sin migrar | `alembic upgrade head` |
| `type "geography" does not exist` | PostGIS no está habilitado | Habilita la extensión en la base |
| La migración de `event_codes` falla con valores nulos | Se agregan columnas `NOT NULL` sobre una tabla con filas | Vacía `event_codes` o recrea la base de pruebas y vuelve a migrar |
| `python -m db.seed` ejecuta este script en lugar del catálogo | Quedó una carpeta antigua `db/seed/` | Bórrala por completo, incluido su `__pycache__` |
| 401 al iniciar sesión | El usuario distingue mayúsculas | Escribe `Danny` o `Panky` exactamente |
| Errores de enums o columnas inexistentes | La rama no está al día con `main` | Actualiza tu rama y migra |

## Verificación rápida

Con la API en marcha e iniciando sesión como `Danny`:

- El endpoint de códigos lista 60 códigos.
- `GET /api/v1/trips?status=ON_ROUTE` devuelve un viaje, el de `Panky`.
- `GET /api/v1/incidents?code=IN_CAR_ACCNT` devuelve uno, relacionado con un `IN_CAR_COLLN`.

Y con SQL:

```sql
SELECT type, count(*) FROM event_codes GROUP BY type;
SELECT status, count(*) FROM trips GROUP BY status;
SELECT code, count(*) FROM vehicle_events GROUP BY code ORDER BY 2 DESC;
SELECT t.status, count(p.position_id) AS posiciones, t.distance, t.average_speed
FROM trips t LEFT JOIN positions p ON p.trip_id = t.trip_id
GROUP BY t.trip_id, t.status, t.distance, t.average_speed
ORDER BY t.departure_date;
```

## Limitaciones

- Las rutas son líneas con curvatura suave y algo de ruido, **no siguen calles reales**; en un mapa se verán casi rectas.
- No hay viajes en estado `GPS_SIGNAL_LOST`, `STOPPED` ni `AT_BASE`, porque requieren más de un vehículo en uso al mismo tiempo. Agregar un segundo vehículo `IN_USE` en `VEHICLE_SPECS` abre esa posibilidad, pero habría que definir sus viajes en `trips.py`.
- No se generan archivos multimedia de incidentes (`IncidentMedia`).
- Los vehículos con documentos expirados o retenidos por autoridades no se incluyen; pueden agregarse en `VEHICLE_SPECS`.
- Las direcciones son descriptivas, sin números exteriores.
