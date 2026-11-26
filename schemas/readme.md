# AxoMotor API REST — schemas

Este documento describe los contratos de entrada y salida expuestos por la API.
Swagger (`/docs`) genera sus esquemas desde los mismos modelos Pydantic/SQLModel;
si un contrato cambia, actualiza ambos recursos en el mismo cambio.

## Convenciones

- Los UUID se envían como cadenas UUID; `date` usa `YYYY-MM-DD` y `datetime` usa ISO 8601.
- En cuerpos de actualización, los campos son opcionales: se modifican solo los enviados.
  Los campos omitidos no cambian; los campos enviados como `null` no se aceptan en
  los actualizadores que usan `apply_update`.
- Los valores de enumeración se envían en mayúsculas, tal como se enumeran abajo.
- En las tablas, “Sí” indica que el campo debe estar presente al enviar ese cuerpo.
  Un campo de respuesta marcado como opcional puede aparecer con valor `null`.

## Índice

- [Autenticación](#autenticación)
- [Usuarios y alertas](#usuarios-y-alertas)
- [Conductores y vinculación](#conductores-y-vinculación)
- [Catálogo de eventos](#catálogo-de-eventos)
- [Vehículos y dispositivos](#vehículos-y-dispositivos)
- [Servicios de vehículos](#servicios-de-vehículos)
- [Ubicaciones conocidas](#ubicaciones-conocidas)
- [Viajes](#viajes)
- [Rastreo y eventos del vehículo](#rastreo-y-eventos-del-vehículo)
- [Incidentes y multimedia](#incidentes-y-multimedia)

## Autenticación

`POST /api/v1/auth/token` recibe formulario OAuth2 (`username`, `password`); el
campo `username` acepta nombre de usuario, correo electrónico o teléfono.
`POST /api/v1/auth/refresh` recibe el siguiente JSON:

| Campo | Tipo | Requerido | Descripción |
|---|---|---:|---|
| `refresh_token` | string | Sí | Token de renovación vigente. |

Las respuestas de inicio de sesión y renovación usan `TokenCreate`:

| Campo | Tipo | Descripción |
|---|---|---|
| `access_token` | string | Token Bearer para autenticar solicitudes. |
| `refresh_token` | string | Token para solicitar un nuevo par de tokens. |
| `token_type` | string | Esquema de autenticación; actualmente `bearer`. |

`PUT /api/v1/auth/change_password` recibe `current_password` (contraseña actual)
y `new_password` (8–120 caracteres). La operación no devuelve cuerpo (`204`).

## Usuarios y alertas

### User

`UserCreate` requiere los campos marcados. `UserUpdate` admite los mismos campos
editables, todos opcionales, excepto `role`, que no se modifica desde esta ruta.
La respuesta `UserResponse` no incluye contraseñas.

| Campo | Tipo | Requerido al crear | Descripción / validación |
|---|---|---:|---|
| `user_id` | UUID | — | Identificador de la cuenta en respuestas. |
| `first_name` | string | Sí | Nombre de pila, 2–60 caracteres. |
| `last_name` | string o null | No | Apellidos, hasta 60 caracteres. |
| `email` | email | Sí | Correo electrónico único, hasta 120 caracteres. |
| `username` | string | Sí | Único, 3–16 caracteres; letras, números, punto y guion bajo; se normaliza a minúsculas. |
| `phone_number` | string | Sí | Teléfono único, hasta 16 caracteres, con formato internacional como `+52 664-123-4567`. |
| `password` | string | Sí | Solo entrada de creación; 8–120 caracteres. |
| `role` | enum | Sí | `ADMIN`, `DRIVER` o `AGENT`; solo entrada de creación. |
| `is_enabled` | boolean | No | Estado habilitado; solo entrada de actualización. |
| `registered_at` | datetime | — | Fecha y hora de registro. |
| `updated_at` | datetime o null | — | Fecha y hora de la última actualización. |
| `logged_in_at` | datetime o null | — | Fecha y hora del último inicio de sesión. |

`UserUpdatePassword` se usa para cambiar la contraseña. `UserResponseShort`, usado
en respuestas anidadas, contiene `first_name`, `last_name`, `role`,
`phone_number` y `email`.

### UserAlert

`UserAlertUpdate` requiere `is_read` (boolean). `UserAlertResponse` contiene:

| Campo | Tipo | Descripción |
|---|---|---|
| `alert_id`, `user_id` | UUID | Identificadores de la alerta y su destinatario. |
| `title` | string | Título, hasta 80 caracteres. |
| `content` | string o null | Contenido opcional, hasta 240 caracteres. |
| `type` | enum | `ACCOUNT`, `SYSTEM`, `VEHICLE_INCIDENT`, `TRIP_INCIDENT` o `INCIDENT_UPDATE`. |
| `is_read` | boolean | Indica si el usuario leyó la alerta. |
| `created_at` | datetime | Fecha y hora de creación. |

## Conductores y vinculación

`DriverCreate` requiere `user_id`, `license_number`, `license_class`,
`license_iss_date` y `license_exp_date`. El usuario debe existir y tener rol
`DRIVER`; la fecha de expedición debe preceder a la de vencimiento.
`DriverUpdate` permite cambiar licencia, fechas y `is_enabled`.

| Campo | Tipo | Descripción |
|---|---|---|
| `driver_id`, `user_id` | UUID | Identificador del perfil e identificador del usuario relacionado. |
| `license_number` | string | De 8 a 20 dígitos. |
| `license_class` | enum | `A`, `A1`, `A2`, `B`, `C`, `D` o `E`. |
| `license_iss_date`, `license_exp_date` | date | Fechas de expedición y vencimiento. |
| `is_active`, `is_enabled` | boolean | Estado del perfil y habilitación del conductor. |
| `registered_at`, `updated_at` | datetime | Registro y última actualización. |
| `user` | `UserResponseShort` | Usuario asociado en la respuesta completa. |
| `has_linked_telegram_account` | boolean | Campo calculado; indica si Telegram está vinculado. |

El identificador interno `telegram_user_id` no se devuelve. La respuesta resumida
`DriverResponseShort` expone `user_id`, datos de contacto calculados desde el
usuario, `license_number`, `license_class`, `is_active` e `is_enabled`.

`POST /api/v1/link_bot/` devuelve `LinkCreateResponse`: `token`, `created_at`,
`expires_on` y `url` para abrir el bot. `PUT /api/v1/link_bot/` recibe `token` y
`telegram_user_id` (entero) para canjear el vínculo.

## Catálogo de eventos

`EventCodeResponse` contiene:

| Campo | Tipo | Descripción |
|---|---|---|
| `code` | string | Código de hasta 12 caracteres. |
| `description` | string | Descripción legible, hasta 40 caracteres. |
| `category` | enum | `DEVICE`, `SENSOR`, `TRACKING`, `NETWORK`, `ACCESS`, `MECHANICAL`, `ACCIDENT`, `CARGO`, `SECURITY`, `ROUTE`, `DRIVER` o `OTHER`. |
| `severity` | enum | `INFO`, `LOW`, `MEDIUM`, `HIGH` o `CRITICAL`. |
| `is_enabled` | boolean | Indica si el código se puede utilizar. |

El modelo de respuesta no incluye `type`; ese dato forma parte del modelo de base
de datos y se usa para clasificar el catálogo.

## Vehículos y dispositivos

### Vehicle

`VehicleCreate` requiere todos los campos salvo que `status` tiene valor
predeterminado. `VehicleUpdate` permite enviar cualquier subconjunto no nulo.

| Campo | Tipo | Descripción / validación |
|---|---|---|
| `vehicle_id` | UUID | Identificador del vehículo en la respuesta. |
| `plate_number` | string | 6–12 caracteres; letras, números, espacios y guiones. Se normaliza a mayúsculas. |
| `reg_number` | string | 12–22 dígitos. |
| `series_vin` | string | Exactamente 17 dígitos según la validación actual. |
| `brand`, `model` | string | 1–60 caracteres cada uno. |
| `year` | integer | Mayor que 1900 y hasta dos años posteriores al año actual. |
| `type` | enum | `PASSENGER_CAR`, `PICKUP`, `PANEL`, `VAN`, `BUS` o `TRUCK`. |
| `status` | enum | `OPERATIVE`, `IN_USE`, `OUT_OF_SERVICE`, `UNDER_MAINTENANCE`, `DOCUMENTS_EXPIRED` o `HELD_BY_AUTHORITIES`; al crear, predeterminado `OPERATIVE`. |
| `registered_at`, `updated_at` | datetime | Registro y última actualización. |

La respuesta resumida `VehicleResponseShort` contiene placas, marca, modelo,
año, tipo y estado.

### VehicleDevice

`VehicleDeviceCreate` requiere `vehicle_id`, `serial_number`, `tag` y `type`;
`is_enabled` es opcional y predeterminado `true`. En actualización todos son
opcionales.

| Campo | Tipo | Descripción |
|---|---|---|
| `device_id`, `vehicle_id` | UUID | Identificadores del dispositivo y del vehículo asociado. |
| `serial_number` | string | Exactamente 12 caracteres; debe ser único. |
| `tag` | string | Etiqueta visible de hasta 16 caracteres. |
| `type` | enum | `HUB` o `NODE`. |
| `battery_level` | integer o null | Nivel de batería, si está disponible. |
| `is_active`, `is_enabled` | boolean | Estado de actividad y habilitación. Los dispositivos nuevos se crean inactivos. |
| `registered_at`, `updated_at` | datetime | Registro y última actualización. |

## Servicios de vehículos

`VehicleServiceCreate` requiere `vehicle_id`, `name` y `date`; los demás campos
son opcionales salvo que `status` se predetermina a `PENDING`.
`VehicleServiceUpdate` permite actualizar nombre, descripción, estado y fechas.

| Campo | Tipo | Descripción |
|---|---|---|
| `service_id`, `vehicle_id` | UUID | Identificadores del servicio y del vehículo. |
| `name` | string | Nombre del servicio, hasta 60 caracteres. |
| `description` | string o null | Detalle del trabajo, hasta 500 caracteres. |
| `status` | enum | `PENDING`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED` o `DISCARDED`. |
| `date`, `next_service_date` | datetime | Fecha de realización y fecha recomendada siguiente. |
| `created_by_id`, `authorized_by_id` | UUID o null | Usuario que registró y, al completar, autorizó el servicio. |
| `registered_at`, `updated_at` | datetime | Registro y última actualización. |
| `created_by`, `authorized_by` | `UserResponseShort` | Se incluyen en `VehicleServiceResponseExtended`. |
| `vehicle` | `VehicleResponseShort` | Se incluye en `VehicleServiceResponseExtended`. |

## Ubicaciones conocidas

`KnownLocationCreate` requiere `name`, `address` y `location_area`; `type` es
opcional. La actualización acepta los mismos campos opcionales.
`location_area` es una lista de al menos cuatro pares `[longitud, latitud]`:
cada coordenada debe estar dentro de WGS 84, el primer y último vértice deben
coincidir, el polígono debe ser válido y tener área distinta de cero.

| Campo | Tipo | Descripción |
|---|---|---|
| `location_id` | UUID | Identificador único de la ubicación. |
| `name` | string | Nombre único, 1–60 caracteres. |
| `type` | string o null | Clasificación opcional, hasta 40 caracteres. |
| `address` | string | Dirección, hasta 240 caracteres. |
| `geojson` | GeoJSON Polygon | Polígono del área; las coordenadas de entrada se transforman a esta propiedad de respuesta. |
| `registered_at` | datetime | Fecha y hora de registro. |

`KnownLocationResponseShort` (usado dentro de viajes) contiene `name`, `type` y
`address`.

## Viajes

`TripCreate` requiere vehículo, conductor, origen, destino y `departure_date`.
`arrive_date` es opcional, pero no puede ser anterior a la salida. El estado
inicial predeterminado es `PLANNED`. `TripUpdate` permite cambios parciales.

| Campo | Tipo | Descripción |
|---|---|---|
| `trip_id` | UUID | Identificador único del viaje. |
| `vehicle_id`, `driver_id` | UUID | Vehículo y conductor asignados. |
| `origin_id`, `destination_id` | UUID | Ubicaciones conocidas de origen y destino. |
| `departure_date`, `arrive_date` | datetime | Salida programada y llegada estimada. |
| `status` | enum | `PLANNED`, `DELAYED`, `ON_ROUTE`, `AT_BASE`, `STOPPED`, `FINISHED`, `CANCELLED`, `ABORTED` o `GPS_SIGNAL_LOST`. |
| `distance`, `average_speed` | decimal o null | Distancia en km y velocidad promedio en km/h, si hay mediciones. |
| `created_at`, `started_at`, `finished_at` | datetime | Creación y marcas de inicio/finalización real; estas últimas pueden ser nulas. |
| `vehicle`, `driver`, `origin`, `destination` | objetos | Resúmenes relacionados en `TripResponse`; vehículo y conductor ampliados en `TripResponseExtended`. |

## Rastreo y eventos del vehículo

`PositionResponse` representa una posición devuelta por
`GET /api/v1/tracking/positions`.

| Campo | Tipo | Descripción |
|---|---|---|
| `position_id`, `vehicle_id` | UUID | Identificadores de la posición y del vehículo. |
| `trip_id` | UUID o null | Viaje asociado, si existe. |
| `geojson` | GeoJSON Point | Punto WGS 84 con coordenadas `[longitud, latitud]`. |
| `speed` | número | Velocidad instantánea en km/h. |
| `registered_at` | datetime | Fecha y hora de captura. |

`RouteResponse`, devuelto por `GET /api/v1/tracking/routes`, incluye `vehicle_id`,
`trip_id`, `geojson` (GeoJSON LineString), `point_count` (posiciones originales),
`render_point_count` (vértices devueltos), `distance` en metros, `average_speed`
en km/h y las fechas `started_at` y `finished_at`.

`VehicleEventCreate` requiere `code` (hasta 12 caracteres) y admite datos
complementarios JSON y coordenadas opcionales. Si se envían coordenadas,
`latitude` y `longitude` deben incluirse juntas, en rango WGS 84; se rechaza el
punto `(0, 0)`.

`VehicleEventResponse` devuelve `event_id`, `vehicle_id`, `info` (el
`EventCodeResponse` asociado), `geojson` (Point o null), `additional_data` y
`registered_at`. Los campos internos `code` y `position` no se exponen.

## Incidentes y multimedia

`IncidentCreate` requiere `trip_id`, `code` y `description`; el estado es
opcional y predeterminado `OPEN`. También admite prioridad solo a través de
`IncidentUpdate`, comentarios, un UUID de incidente relacionado y coordenadas
GPS bajo las reglas descritas arriba. La actualización no admite relacionar el
incidente consigo mismo.

| Campo de `IncidentResponse` | Tipo | Descripción |
|---|---|---|
| `incident_id`, `trip_id` | UUID | Identificadores del incidente y del viaje. |
| `info` | `EventCodeResponse` | Código y descripción del incidente; `code` interno se omite. |
| `priority` | enum | `LOW`, `MEDIUM` o `HIGH`; predeterminada `MEDIUM` en el modelo. |
| `status` | enum | `OPEN`, `IN_REVISION`, `CLOSED` o `DISCARDED`. |
| `description`, `comments` | string o null | Descripción y observaciones, hasta 500 caracteres. |
| `related_incident_id` | UUID o null | Incidente relacionado, si existe. |
| `geojson` | GeoJSON Point o null | Ubicación del incidente; la geometría interna no se expone. |
| `registered_at`, `reviewed_at`, `closed_at` | datetime | Registro, revisión y cierre; revisión y cierre pueden ser nulos. |
| `created_by_id`, `reviewed_by_id` | UUID o null | Identificadores de creador y revisor. |

`IncidentResponseExtended` añade `trip`, `created_by`, `reviewed_by` y
`media_files`.

La carga de multimedia (`POST /api/v1/incident_media/`) usa
`multipart/form-data`: `incident_id` (UUID), `type` (`IMAGE` o `VIDEO`), `file`
y `file_metadata` opcional. `IncidentMediaResponse` contiene `file_id`,
`incident_id`, `type`, `file_metadata`, `uploaded_at`, `uploaded_by_id`,
`uploaded_by` (resumen del usuario) y `file_url` generado para descargar el
archivo. La clave interna de almacenamiento no se expone; no se registra una
fecha `captured_at` en este modelo.
