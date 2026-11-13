# AxoMotor API rest

**Entorno:** Backend
**Objetivo:** Acceso a la información del Sistema de Monitoreo de Vehículos en Tiempo Real
**URL base:** /api/v1/

## Cómo consultar esta información

Los métodos indican las acciones que se pueden realizar con cada modelo.

Columnas:
- Único: Verifica unicidad de valor en la tabla.
- Requerido: Se necesita en el momento de crear un nuevo registro.
- Actualizable: Permite actualizar el valor.

Referencias de emojis:

| Emoji | Descripción                                                                                                             |
| ----- | ----------------------------------------------------------------------------------------------------------------------- |
| 🔑    | Identificador autogenerado.                                                                                             |
| ✅     | Si (único o requerido o actualizable).                                                                                  |
| ❌     | No. En la columna Requerido implica que el valor es opcional.                                                           |
| ❗     | Solo permite borrar el valor.                                                                                           |
| 🚫    | Operación no válida. Solo aplica en campos de marcas de tiempo e identificadores de usuarios que modifican un registro. |

## Endpoints

### Catalogo de códigos de eventos de vehículos

**Endpoint:** `vehicle_event_codes/`
**Métodos:** `GET`

| Campo       | Tipo                          | Longitud | Único | Requerido | Actualizable | Descripción                                                         |
| ----------- | ----------------------------- | -------- | ----- | --------- | ------------ | ------------------------------------------------------------------- |
| code        | STRING                        | 12       | 🔑    | 🔑        | ❌            | Código de evento.                                                   |
| description | STRING                        | 40       | ✅     | ❌         | ❌            | Descripción del evento.                                             |
| severity    | ENUM(INFO, WARNING, CRITICAL) |          | ❌     | ❌         | ❌            | Severidad del evento. Puede ser: información, advertencia, crítico. |

### Catalogo de códigos de incidencias

**Endpoint:** `incident_codes/`
**Métodos:** `GET`

| Campo       | Tipo                          | Longitud | Único | Requerido | Actualizable | Descripción                                                               |
| ----------- | ----------------------------- | -------- | ----- | --------- | ------------ | ------------------------------------------------------------------------- |
| code        | STRING                        | 12       | 🔑    | 🔑        | ❌            | Código de la incidencia.                                                  |
| description | STRING                        | 40       | ✅     | ❌         | ❌            | Descripción de la incidencia.                                             |
| severity    | ENUM(INFO, WARNING, CRITICAL) |          | ❌     | ❌         | ❌            | Severidad de la incidencia. Puede ser: información, advertencia, crítico. |

### Usuarios

**Endpoint:** `users/`
**Métodos:** `GET, POST, PUT, PATCH`

| Campo           | Tipo                       | Longitud | Único | Requerido | Actualizable | Descripción                                                                                    |
| --------------- | -------------------------- | -------- | ----- | --------- | ------------ | ---------------------------------------------------------------------------------------------- |
| user_id         | UUID                       |          | 🔑    | 🔑        | ❌            | Identificador del usuario.                                                                     |
| first_name      | STRING                     | 2-60     | ❌     | ✅         | ✅            | Nombre de pila del usuario.                                                                    |
| last_name       | STRING                     | 2-60     | ❌     | ✅         | ✅            | Apellidos del usuario.                                                                         |
| email           | STRING                     | 120      | ✅     | ✅         | ✅            | Correo electrónico del usuario.                                                                |
| username        | STRING                     | 3-16     | ✅     | ✅         | ✅            | Nombre de usuario.                                                                             |
| phone_number    | STRING                     | 16       | ✅     | ✅         | ✅            | Número de teléfono del usuario. Se almacena en formato +XX-XXX-XXX-XXXX.                       |
| hashed_password | STRING                     |          | ❌     | ✅         | ✅            | Contraseña hasheada.                                                                           |
| role            | ENUM(ADMIN, DRIVER, AGENT) |          | ❌     | ✅         | ❌            | Rol del usuario. Puede ser alguna de las siguiente opciones: administrador, conductor, agente. |
| is_enabled      | BOOLEAN                    |          | ❌     | ❌         | ✅            | Indica si el usuario se encuentra habilitado en el sistema. Por defecto es TRUE.               |
| registered_at   | TIMESTAMP                  |          | ❌     | 🚫        | ❌            | Marca de tiempo de registro del usuario. Por defecto es la fecha y hora actual.                |
| updated_at      | TIMESTAMP                  |          | ❌     | 🚫        | ❌            | Marca de tiempo de actualización del usuario. Por defecto es la fecha y hora actual.           |
| logged_in_at    | TIMESTAMP                  |          | ❌     | 🚫        | ❌            | Marca de tiempo de último inicio de sesión del usuario.                                        |

### Ubicaciones conocidas

**Endpoint:** `known_locations/`
**Métodos:** `GET, POST, PUT, PATCH`

| Campo         | Tipo                    | Longitud | Único | Requerido | Actualizable | Descripción                                                               |
| ------------- | ----------------------- | -------- | ----- | --------- | ------------ | ------------------------------------------------------------------------- |
| location_id   | UUID                    |          | 🔑    | 🔑        | ❌            | Identificador de la ubicación.                                            |
| name          | STRING                  | 1-60       | ❌     | ✅         | ✅            | Nombre de la ubicación.                                                   |
| type          | STRING                  | 40       | ❌     | ❌         | ✅            | Tipo de la ubicación.                                                     |
| address       | LONG TEXT               | 240      | ✅     | ✅         | ✅            | Dirección completa de la ubicación.                                       |
| location_area | GEOMETRY(Polygon, 4326) |          | ❌     | ✅         | ✅            | Polígono de la ubicación para usarla con Geocercas.                       |
| registered_at | TIMESTAMP               |          | ❌     | 🚫        | ❌            | Fecha de registro de la ubicación. Por defecto es la fecha y hora actual. |

### Vehículos

**Endpoint:** `vehicles/`
**Métodos:** `GET, POST, PUT, PATCH`

| Campo         | Tipo                                                                                               | Longitud | Único | Requerido | Actualizable | Descripción                                                                                                                                                                   |
| ------------- | -------------------------------------------------------------------------------------------------- | -------- | ----- | --------- | ------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| vehicle_id    | UUID                                                                                               |          | 🔑    | 🔑        | ❌            | Identificador de vehículo.                                                                                                                                                    |
| plate_number  | STRING                                                                                             | 8-12     | ✅     | ✅         | ✅            | Número de placas del vehículo.                                                                                                                                                |
| reg_number    | STRING                                                                                             | 16-22    | ✅     | ✅         | ✅            | Número de registro de tarjeta de circulación del vehículo.                                                                                                                    |
| series_vin    | STRING                                                                                             | 17       | ✅     | ✅         | ❌            | Número de serie del vehículo (VIN).                                                                                                                                           |
| brand         | STRING                                                                                             | 60       | ❌     | ✅         | ❌            | Marca del vehículo.                                                                                                                                                           |
| model         | STRING                                                                                             | 60       | ❌     | ✅         | ❌            | Modelo del vehículo.                                                                                                                                                          |
| year          | INT                                                                                                |          | ❌     | ✅         | ❌            | Año del vehículo.                                                                                                                                                             |
| type          | ENUM(PASSENGER_CAR, PICKUP, PANEL, VAN, BUS, TRUCK)                                                |          | ❌     | ✅         | ❌            | Tipo de vehículo. Puede ser: vehículo de pasajeros, camioneta, panel, van, autobus, camión.                                                                                   |
| axes          | INT                                                                                                |          | ❌     | ✅         | ❌            | Número de ejes del vehículo. Por defecto: 2.                                                                                                                                  |
| status        | ENUM(OPERATIVE, IN_USE, OUT_OF_SERVICE, UNDER_MAINTENANCE, DOCUMENTS_EXPIRED, HELD_BY_AUTHORITIES) |          | ❌     | ❌         | ✅            | Estado actual del vehículo. Puede ser: operativo, en uso, fuera de servicio, en mantenimiento, documentación expirada o retenido por las autoridades. Por defecto: operativo. |
| registered_at | TIMESTAMP                                                                                          |          | ❌     | 🚫        | ❌            | Marca de tiempo de registro del vehículo. Por defecto es la fecha y hora actual.                                                                                              |
| updated_at    | TIMESTAMP                                                                                          |          | ❌     | 🚫        | ❌            | Marca de tiempo de actualización del vehículo. Por defecto es la fecha y hora actual.                                                                                         |

### Alertas de usuarios

**Endpoint:** `user_alerts/`
**Métodos:** `GET, PUT, DELETE`

| Campo      | Tipo      | Longitud | Único | Requerido | Actualizable | Descripción                                                                                            |
| ---------- | --------- | -------- | ----- | --------- | ------------ | ------------------------------------------------------------------------------------------------------ |
| alert_id   | UUID      |          | 🔑    | 🔑        | ❌            | Identificador único de la alerta.                                                                      |
| user_id    | UUID      |          | ❌     | ❌         | ❌            | Identificador del usuario asociado a la alerta. Se relaciona con la columna user_id de la tabla users. |
| title      | STRING    | 80       | ❌     | ❌         | ❌            | Título de la alerta.                                                                                   |
| content    | STRING    | 240      | ❌     | ❌         | ❌            | Contenido de la alerta.                                                                                |
| type       | ENUM      |          | ❌     | ❌         | ❌            | Tipo de alerta.                                                                                        |
| is_read    | BOOLEAN   |          | ❌     | ❌         | ✅            | Indicador de lectura de la alerta.                                                                     |
| created_at | TIMESTAMP |          | ❌     | 🚫        | ❌            | Marca de tiempo de creación de la alerta. Por defecto es la fecha y hora actual.                       |

### Conductores

**Endpoint:** `drivers/`
**Métodos:** `GET, POST, PUT, PATCH`

| Campo            | Tipo                        | Longitud | Único | Requerido | Actualizable | Descripción                                                                                                                                           |
| ---------------- | --------------------------- | -------- | ----- | --------- | ------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| driver_id        | UUID                        |          | 🔑    | 🔑        | ❌            | Identificador único del conductor.                                                                                                                    |
| user_id          | UUID                        |          | ✅     | ✅         | ❌            | Identificador del usuario asociado al perfil de conductor. Se relaciona con la columna user_id de la tabla users.                                     |
| telegram_user_id | BIGINT                      |          | ❌     | ❌         | ❗            | Identificador del usuario asociado a la cuenta en Telegram. Se obtiene cuando un usuario inicia sesión a través del bot manejado por el agente de IA. |
| license_number   | STRING                      |          | ❌     | ✅         | ✅            | Número oficial de la licencia de conducir.                                                                                                            |
| license_class    | ENUM(A, A1, A2, B, C, D, E) |          | ❌     | ✅         | ✅            | Clase de la licencia de conducir. Puede ser: A, A1, A2, B, C, D, E.                                                                                   |
| license_iss_date | DATE                        |          | ❌     | ✅         | ✅            | Fecha de expedición o emisión de la licencia de conducir.                                                                                             |
| license_exp_date | DATE                        |          | ❌     | ✅         | ✅            | Fecha de vencimiento o expiración de la licencia de conducir.                                                                                         |
| is_active        | BOOLEAN                     |          | ❌     | ❌         | ❌            | Indica si el conductor se encuentra activo en el sistema.                                                                                             |
| is_enabled       | BOOLEAN                     |          | ❌     | ❌         | ✅            | Indica si el conductor se encuentra habilitado para conducir. Por defecto: TRUE.                                                                      |
| registered_at    | TIMESTAMP                   |          | ❌     | 🚫        | ❌            | Marca de tiempo de registro del conductor. Por defecto es la fecha y hora actual.                                                                     |
| updated_at       | TIMESTAMP                   |          | ❌     | 🚫        | ❌            | Marca de tiempo de actualización del conductor. Por defecto es la fecha y hora actual.                                                                |

### Servicios a vehículos

**Endpoint:** `vehicle_services/`
**Métodos:** `GET, POST, PUT, PATCH`

| Campo             | Tipo                                                        | Longitud | Único | Requerido | Actualizable | Descripción                                                                                                                                 |
| ----------------- | ----------------------------------------------------------- | -------- | ----- | --------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------- |
| service_id        | UUID                                                        |          | 🔑    | 🔑        | ❌            | Identificador de servicio.                                                                                                                  |
| vehicle_id        | UUID                                                        |          | ❌     | ✅         | ❌            | Identificador del vehículo. Se relaciona con la columna vehicle_id de la tabla vehicles.                                                    |
| status            | ENUM(PENDING, IN_PROGRESS, COMPLETED, CANCELLED, DISCARDED) |          | ❌     | ✅         | ✅            | Estado actual del servicio de mantenimiento. Puede ser: pendiente, en progreso, completado, cancelado, descartado. Por defecto: pendiente.  |
| date              | DATETIME                                                    |          | ❌     | ✅         | ✅            | Fecha y hora en que se realiza el servicio de mantenimiento.                                                                                |
| next_service_date | DATETIME                                                    |          | ❌     | ✅         | ✅            | Fecha y hora estimada para el siguiente servicio de mantenimiento.                                                                          |
| created_by_id     | UUID                                                        |          | ❌     | 🚫        | ❌            | Identificador del usuario que crea la realización del servicio de mantenimiento. Se relaciona con la columna user_id de la tabla users.     |
| authorized_by_id  | UUID                                                        |          | ❌     | 🚫        | ❌            | Identificador del usuario que autoriza la realización del servicio de mantenimiento. Se relaciona con la columna user_id de la tabla users. |
| registered_at     | TIMESTAMP                                                   |          | ❌     | 🚫        | ❌            | Marca de tiempo de registro del servicio. Por defecto es la fecha y hora actual.                                                            |
| updated_at        | TIMESTAMP                                                   |          | ❌     | 🚫        | ❌            | Marca de tiempo de actualización del servicio. Por defecto es la fecha y hora actual.                                                       |

### Dispositivos en vehículos

**Endpoint:** `vehicle_devices/`
**Métodos:** `GET, POST, PUT, PATCH`

| Campo         | Tipo            | Longitud | Único | Requerido | Actualizable | Descripción                                                                                                                                                                                    |
| ------------- | --------------- | -------- | ----- | --------- | ------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| device_id     | UUID            |          | 🔑    | 🔑        | ❌            | Identificador único del dispositivo telemático.                                                                                                                                                |
| vehicle_id    | UUID            |          | ❌     | ✅         | ❌            | Identificador del vehículo al que está asignado e instalado el dispositivo. Se relaciona con la columna vehicle_id de la tabla vehicles.                                                       |
| serial_number | STRING          | 12       | ❌     | ✅         | ✅            | Número de serie de fabricación del dispositivo.                                                                                                                                                |
| tag           | STRING          | 16       | ❌     | ✅         | ✅            | Etiqueta o identificador alfanumérico visible asignado al dispositivo.                                                                                                                         |
| type          | ENUM(HUB, NODE) |          | ❌     | ✅         | ✅            | Tipo de dispositivo telemático o sensor instalado en el vehículo. Puede ser: hub (concentrador que procesa los datos de los sensores), node (dispositivo equipado con sensor, cámara o ambos). |
| battery_level | INT             |          | ❌     | 🚫        | ❌            | Nivel porcentual o carga actual de la batería del dispositivo.                                                                                                                                 |
| is_active     | BOOLEAN         |          | ❌     | 🚫        | ❌            | Indica si el dispositivo se encuentra activo y transmitiendo datos.                                                                                                                            |
| is_enabled    | BOOLEAN         |          | ❌     | ❌         | ✅            | Indica si el dispositivo se encuentra habilitado. Por defecto es TRUE.                                                                                                                         |
| registered_at | TIMESTAMP       |          | ❌     | 🚫        | ❌            | Marca de tiempo de registro del dispositivo. Por defecto es la fecha y hora actual.                                                                                                            |
| updated_at    | TIMESTAMP       |          | ❌     | 🚫        | ❌            | Marca de tiempo de actualización del dispositivo. Por defecto es la fecha y hora actual.                                                                                                       |
### Eventos de vehículos

**Endpoint:** `vehicle_events/`
**Métodos:** `GET`

| Campo           | Tipo                   | Longitud | Único | Requerido | Actualizable | Descripción                                                                                                                                        |
| --------------- | ---------------------- | -------- | ----- | --------- | ------------ | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| event_id        | UUID                   |          | 🔑    | 🔑        | ❌            | Identificador de evento.                                                                                                                           |
| code            | STRING                 | 12       | ❌     | ❌         | ❌            | Código identificador del tipo de evento generado por el dispositivo. Se relaciona con la columna code de la tabla vehicle_event_codes.             |
| vehicle_id      | UUID                   |          | ❌     | ❌         | ❌            | Identificador del vehículo donde está instalado el dispositivo que produjo el evento. Se relaciona con la columna vehicle_id de la tabla vehicles. |
| position        | GEOGRAPHY(Point, 4326) |          | ❌     | ❌         | ❌            | Coordenadas geográficas donde se originó el evento del vehículo.                                                                                   |
| additional_data | JSON                   |          | ❌     | ❌         | ❌            | Datos complementarios o métricas en formato JSON asociados al evento.                                                                              |
| registered_at   | TIMESTAMP              |          | ❌     | 🚫        | ❌            | Marca de tiempo de registro del evento. Por defecto es la fecha y hora actual.                                                                     |

### Viajes

**Endpoint:** `trips/`
**Métodos:** `GET, POST, PUT, PATCH`

| Campo          | Tipo                                                                                              | Longitud | Único | Requerido | Actualizable | Descripción                                                                                                                                                                            |
| -------------- | ------------------------------------------------------------------------------------------------- | -------- | ----- | --------- | ------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| trip_id        | UUID                                                                                              |          | 🔑    | 🔑        | ❌            | Identificador único del viaje registrado.                                                                                                                                              |
| vehicle_id     | UUID                                                                                              |          | ❌     | ✅         | ❌            | Identificador del vehículo asignado para realizar el viaje. Se relaciona con la columna vehicle_id de la tabla vehicles.                                                               |
| driver_id      | UUID                                                                                              |          | ❌     | ✅         | ✅            | Identificador del conductor asignado para operar el viaje. Se relaciona con la columna driver_id de la tabla drivers.                                                                  |
| origin_id      | UUID                                                                                              |          | ❌     | ✅         | ✅            | Identificador del lugar conocido configurado como punto de origen. Se relaciona con la columna location_id de la tabla known_locations.                                                |
| destination_id | UUID                                                                                              |          | ❌     | ✅         | ✅            | Identificador del lugar conocido configurado como punto de destino. Se relaciona con la columna location_id de la tabla known_locations.                                               |
| departure_date | DATETIME                                                                                          |          | ❌     | ✅         | ✅            | Fecha y hora programada o estimada de salida del viaje.                                                                                                                                |
| arrive_date    | DATETIME                                                                                          |          | ❌     | ✅         | ✅            | Fecha y hora programada o estimada de llegada al destino.                                                                                                                              |
| status         | ENUM(PLANNED, DELAYED, ON_ROUTE, AT_BASE, STOPPED, FINISHED, CANCELLED, ABORTED, GPS_SIGNAL_LOST) |          | ❌     | ✅         | ✅            | Estado actual del viaje en el sistema. Puede ser: planeado, retrasado, en ruta, en base, detenido, finalizado, cancelado, abortado, señal GPS perdida. Valor predeterminado: planeado. |
| distance       | NUMERIC                                                                                           | 5,2      | ❌     | 🚫        | ❌            | Distancia total recorrida durante el trayecto del viaje en kilómetros.                                                                                                                 |
| average_speed  | NUMERIC                                                                                           | 5,2      | ❌     | 🚫        | ❌            | Velocidad promedio registrada durante el viaje en km/h.                                                                                                                                |
| created_at     | TIMESTAMP                                                                                         |          | ❌     | 🚫        | ❌            | Marca de tiempo de la creación del viaje. Por defecto es la fecha y hora actual.                                                                                                       |
| started_at     | TIMESTAMP                                                                                         |          | ❌     | 🚫        | ❌            | Marca de tiempo real de inicio del viaje.                                                                                                                                              |
| finished_at    | TIMESTAMP                                                                                         |          | ❌     | 🚫        | ❌            | Marca de tiempo real de finalización o cierre del viaje.                                                                                                                               |
### Posiciones en viajes

**Endpoint:** `trip_positions/`
**Métodos:** `GET, POST`

| Campo         | Tipo                   | Longitud | Único | Requerido | Actualizable | Descripción                                                                                                                 |
| ------------- | ---------------------- | -------- | ----- | --------- | ------------ | --------------------------------------------------------------------------------------------------------------------------- |
| position_id   | UUID                   |          | 🔑    | 🔑        | ❌            | Identificador único del registro de posición.                                                                               |
| trip_id       | UUID                   |          | ❌     | ✅         | ❌            | Identificador del viaje al cual corresponde el registro de posición. Se relaciona con la columna trip_id de la tabla trips. |
| position      | GEOGRAPHY(Point, 4326) |          | ❌     | ✅         | ❌            | Coordenadas geográficas registradas del vehículo en el trayecto.                                                            |
| speed         | NUMERIC                | 5,2      | ❌     | ✅         | ❌            | Velocidad instantánea registrada del vehículo en km/h.                                                                      |
| registered_at | TIMESTAMP              |          | ❌     | 🚫        | ❌            | Marca de tiempo de captura de la posición. Por defecto es la fecha y hora actual.                                           |

### Incidentes

**Endpoint:** `incidents/`
**Métodos:** `GET, POST, PUT, PATCH`

| Campo               | Tipo                                       | Longitud | Único | Requerido | Actualizable | Descripción                                                                                                                                                              |
| ------------------- | ------------------------------------------ | -------- | ----- | --------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| incident_id         | UUID                                       |          | 🔑    | 🔑        | ❌            | Identificador único de la incidencia reportada.                                                                                                                          |
| related_incident_id | UUID                                       |          | ❌     | ❌         | ✅            | Identificador de la incidencia vinculada o relacionada para dar seguimiento. Se relaciona con la columna incident_id de la misma tabla.                                  |
| created_by_id       | UUID                                       |          | ❌     | 🚫        | ❌            | Identificador del usuario que registró la incidencia. Se relaciona con la columna user_id de la tabla users. Si es nulo, se asume que el sistema registró la incidencia. |
| reviewed_by_id      | UUID                                       |          | ❌     | 🚫        | ❌            | Identificador del agente asignado para atender la incidencia. Se relaciona con la columna user_id de la tabla users.                                                     |
| trip_id             | UUID                                       |          | ❌     | ✅         | ❌            | Identificador del viaje durante el cual ocurrió la incidencia. Se relaciona con la columna trip_id de la tabla trips.                                                    |
| code                | STRING                                     | 12       | ❌     | ✅         | ✅            | Código de referencia del catálogo de tipos de incidencia. Se relaciona con la columna code de la tabla incident_codes.                                                   |
| status              | ENUM(OPEN, IN_REVISION, CLOSED, DISCARDED) |          | ❌     | ❌         | ✅            | Estado actual de atención o resolución de la incidencia. Puede ser: abierto, en revisión, cerrado, descartado. Por defecto: abierto.                                     |
| position            | GEOGRAPHY(Point, 4326)                     |          | ❌     | ✅         | ❌            | Coordenadas geográficas donde ocurrió la incidencia.                                                                                                                     |
| description         | LONGTEXT                                   | 2-500    | ❌     | ✅         | ✅            | Descripción detallada de los hechos ocurridos en la incidencia.                                                                                                          |
| comments            | LONGTEXT                                   | 2-500    | ❌     | 🚫        | ✅            | Comentarios u observaciones de seguimiento por parte del agente.                                                                                                         |
| registered_at       | TIMESTAMP                                  |          | ❌     | 🚫        | ❌            | Marca de tiempo de registro de la incidencia. Por defecto es la fecha y hora actual.                                                                                     |
| reviewed_at         | TIMESTAMP                                  |          | ❌     | 🚫        | ❌            | Marca de tiempo en que la incidencia fue revisada por el agente.                                                                                                         |
| closed_at           | TIMESTAMP                                  |          | ❌     | 🚫        | ❌            | Marca de tiempo en que la incidencia fue cerrada o resuelta.                                                                                                             |
### Archivos multimedia de incidentes

**Endpoint:** `incident_media/`
**Métodos:** `GET, POST, DELETE`

| Campo         | Tipo               | Longitud | Único | Requerido | Actualizable | Descripción                                                                                                                    |
| ------------- | ------------------ | -------- | ----- | --------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------ |
| media_id      | UUID               |          | 🔑    | 🔑        | ❌            | Identificador único de la evidencia multimedia.                                                                                |
| incident_id   | UUID               |          | ❌     | ✅         | ❌            | Identificador de la incidencia vinculada al archivo multimedia. Se relaciona con la columna incident_id de la tabla incidents. |
| file_url      | STRING             | 240      | ❌     | 🚫        | ❌            | Identificador o ruta del archivo en el repositorio de almacenamiento.                                                          |
| type          | ENUM(IMAGE, VIDEO) |          | ❌     | ✅         | ❌            | Tipo de evidencia multimedia capturada. Puede ser de tipo imagen o vídeo.                                                      |
| file_metadata | JSON               |          | ❌     | ✅         | ❌            | Metadatos del archivo de evidencia multimedia.                                                                                 |
| captured_at   | TIMESTAMP          |          | ❌     | ✅         | ❌            | Marca de tiempo en la que fue capturada la evidencia multimedia.                                                               |
| uploaded_at   | TIMESTAMP          |          | ❌     | 🚫        | ❌            | Marca de tiempo en la que se completó la subida del archivo al servidor.                                                       |
