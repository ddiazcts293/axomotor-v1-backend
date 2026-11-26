# AxoMotor API REST

**Entorno:** Backend
**Objetivo:** Consultar y administrar la información del sistema de monitoreo vehicular.

La API está versionada bajo `/api/v1`. La mayoría de las rutas requieren un token
de acceso Bearer. `GET /health`, el inicio/renovación de sesión, el registro de
usuario y la vinculación de Telegram no requieren ese token. La carga de
multimedia acepta Bearer o las credenciales del bot (`X-Bot-API-Key` y
`X-Telegram-User-Id`); el registro MQTT de eventos usa
`X-MQTT-Consumer-API-Key`.

Los listados paginados aceptan `limit` (1–100, predeterminado 20) y `offset`
(predeterminado 0), y devuelven el total en la cabecera `X-Total-Count`.

Los tipos de solicitud y respuesta se describen en la
[referencia de schemas](../schemas/readme.md). Swagger UI está disponible en `/docs`
cuando se ejecuta el servidor.

## Contenido

- [Salud](#salud)
- [Autenticación](#autenticación)
- [Usuarios](#usuarios)
- [Alertas](#alertas)
- [Conductores y vinculación de Telegram](#conductores-y-vinculación-de-telegram)
- [Vehículos y eventos](#vehículos-y-eventos)
- [Servicios de vehículos](#servicios-de-vehículos)
- [Dispositivos de vehículos](#dispositivos-de-vehículos)
- [Ubicaciones conocidas](#ubicaciones-conocidas)
- [Rastreo](#rastreo)
- [Viajes](#viajes)
- [Incidentes y multimedia](#incidentes-y-multimedia)
- [Catálogo de códigos](#catálogo-de-códigos)

## Endpoints

### Salud

| Método | Ruta | Acceso | Descripción | Respuesta |
|---|---|---|---|---|
| GET | `/health` | Público | Comprueba que el servicio está disponible. | `{ "status": "healthy" }` |

### Autenticación

| Método | Ruta | Acceso | Descripción | Respuesta |
|---|---|---|---|---|
| POST | `/api/v1/auth/token` | Público | Inicia sesión con `username` (también admite correo o teléfono) y contraseña en formato OAuth2 form. | `TokenCreate` |
| POST | `/api/v1/auth/refresh` | Público | Emite un nuevo par de tokens a partir de un token de renovación válido. | `TokenCreate` |
| PUT | `/api/v1/auth/change_password` | Bearer | Cambia la contraseña del usuario autenticado; requiere contraseña actual y nueva. | `204 No Content` |

### Usuarios

| Método | Ruta | Descripción | Respuesta |
|---|---|---|---|
| GET | `/api/v1/users/me` | Devuelve el perfil del usuario autenticado. | `UserResponse` |
| POST | `/api/v1/users/` | Registra un usuario y almacena su contraseña de forma segura. | `201`, `UserResponse` |
| GET | `/api/v1/users/` | Lista usuarios; filtros opcionales: `role`, `is_enabled`. | `list[UserResponse]` |
| GET | `/api/v1/users/{user_id}` | Obtiene un usuario por UUID. | `UserResponse` |
| PUT | `/api/v1/users/{user_id}` | Actualiza los campos proporcionados del usuario. | `UserResponse` |

### Alertas

| Método | Ruta | Descripción | Respuesta |
|---|---|---|---|
| GET | `/api/v1/alerts/` | Lista las alertas propias; filtros: `is_read`, `type`, `from_date`, `to_date`. | `list[UserAlertResponse]` |
| PUT | `/api/v1/alerts/{alert_id}` | Actualiza el estado de lectura de una alerta propia. | `UserAlertResponse` |
| DELETE | `/api/v1/alerts/` | Elimina todas las alertas del usuario autenticado. | `204 No Content` |
| DELETE | `/api/v1/alerts/{alert_id}` | Elimina una alerta propia. | `204 No Content` |

### Conductores y vinculación de Telegram

| Método | Ruta | Descripción | Respuesta |
|---|---|---|---|
| POST | `/api/v1/drivers/` | Crea el perfil de conductor para un usuario con rol `DRIVER`. | `201`, `DriverResponse` |
| GET | `/api/v1/drivers/` | Lista conductores; filtros: `user_id`, `license_class`, `is_active`, `is_enabled`. | `list[DriverResponse]` |
| GET | `/api/v1/drivers/{driver_id}` | Obtiene un conductor por UUID. | `DriverResponse` |
| PUT | `/api/v1/drivers/{driver_id}` | Actualiza los datos permitidos del conductor. | `DriverResponse` |
| POST | `/api/v1/link_bot/` | Emite un token temporal para vincular el conductor autenticado con Telegram. | `201`, `LinkCreateResponse` |
| PUT | `/api/v1/link_bot/` | Canjea el token y asocia `telegram_user_id` al conductor. | `DriverResponse` |

### Vehículos y eventos

| Método | Ruta | Descripción | Respuesta |
|---|---|---|---|
| POST | `/api/v1/vehicles/` | Registra un vehículo. Placa, registro y VIN deben ser únicos. | `201`, `VehicleResponse` |
| GET | `/api/v1/vehicles/` | Lista vehículos; admite filtros por placa, registro, VIN, marca, modelo, año, tipo y estado. | `list[VehicleResponse]` |
| GET | `/api/v1/vehicles/{vehicle_id}` | Obtiene un vehículo por UUID. | `VehicleResponse` |
| PUT | `/api/v1/vehicles/{vehicle_id}` | Actualiza los campos proporcionados del vehículo. | `VehicleResponse` |
| GET | `/api/v1/vehicles/{vehicle_id}/events` | Lista eventos del vehículo; filtros: `code`, `from_date`, `to_date`. | `list[VehicleEventResponse]` |
| POST | `/api/v1/vehicles/{vehicle_id}/events` | Registra un evento enviado por el consumidor MQTT; requiere su API key de servicio. | `204 No Content` |

### Servicios de vehículos

| Método | Ruta | Descripción | Respuesta |
|---|---|---|---|
| POST | `/api/v1/vehicle_services/` | Registra un servicio de mantenimiento. | `201`, `VehicleServiceResponse` |
| GET | `/api/v1/vehicle_services/` | Lista servicios; filtros: `vehicle_id`, `service_status`, `from_date`, `to_date`. | `list[VehicleServiceResponse]` |
| GET | `/api/v1/vehicle_services/{service_id}` | Obtiene el detalle, incluido vehículo y usuarios asociados. | `VehicleServiceResponseExtended` |
| PUT | `/api/v1/vehicle_services/{service_id}` | Actualiza un servicio; al marcarlo completado se registra quién lo autorizó. | `VehicleServiceResponse` |

### Dispositivos de vehículos

| Método | Ruta | Descripción | Respuesta |
|---|---|---|---|
| POST | `/api/v1/vehicle_devices/` | Registra un dispositivo asociado a un vehículo. | `201`, `VehicleDeviceResponse` |
| GET | `/api/v1/vehicle_devices/` | Lista dispositivos; filtros: `vehicle_id`, `type`, `is_active`, `is_enabled`. | `list[VehicleDeviceResponse]` |
| GET | `/api/v1/vehicle_devices/{device_id}` | Obtiene un dispositivo por UUID. | `VehicleDeviceResponse` |
| PUT | `/api/v1/vehicle_devices/{device_id}` | Actualiza los campos proporcionados del dispositivo. | `VehicleDeviceResponse` |

### Ubicaciones conocidas

| Método | Ruta | Descripción | Respuesta |
|---|---|---|---|
| POST | `/api/v1/locations/` | Registra una ubicación con su polígono GeoJSON expresado como vértices. | `201`, `KnownLocationResponse` |
| GET | `/api/v1/locations/` | Lista las ubicaciones conocidas. | `list[KnownLocationResponse]` |
| GET | `/api/v1/locations/{location_id}` | Obtiene una ubicación por UUID. | `KnownLocationResponse` |
| PUT | `/api/v1/locations/{location_id}` | Actualiza los datos proporcionados de una ubicación. | `KnownLocationResponse` |

### Rastreo

| Método | Ruta | Descripción | Respuesta |
|---|---|---|---|
| GET | `/api/v1/tracking/positions` | Consulta posiciones GPS; filtros: `vehicle_id`, `trip_id`, `from_date`, `to_date`. | `list[PositionResponse]` |
| GET | `/api/v1/tracking/routes` | Agrupa posiciones por vehículo y viaje; admite los filtros anteriores y simplificación geométrica con `tolerance` o `auto_optimize`. Solo incluye grupos con al menos dos posiciones. | `list[RouteResponse]` |

En las rutas, `tolerance` se expresa en metros y acepta valores entre 0 y 1000.
La optimización automática aplica una tolerancia si se especifica un intervalo de
fechas mayor a un día; requiere `from_date` y `to_date`. La distancia de respuesta
se expresa en metros y la velocidad promedio en km/h.

### Viajes

| Método | Ruta | Descripción | Respuesta |
|---|---|---|---|
| POST | `/api/v1/trips/` | Programa un viaje con vehículo, conductor, origen, destino y fecha de salida. | `201`, `TripResponse` |
| GET | `/api/v1/trips/` | Lista viajes; filtros: vehículo, conductor, origen, destino, `status`, `from_date`, `to_date`. | `list[TripResponse]` |
| GET | `/api/v1/trips/{trip_id}` | Obtiene el detalle del viaje con vehículo y conductor ampliados. | `TripResponseExtended` |
| PUT | `/api/v1/trips/{trip_id}` | Actualiza los datos del viaje; la llegada no puede ser anterior a la salida. | `TripResponse` |

### Incidentes y multimedia

| Método | Ruta | Descripción | Respuesta |
|---|---|---|---|
| POST | `/api/v1/incidents/` | Registra un incidente asociado a un viaje, opcionalmente con coordenadas GPS. | `201`, `IncidentResponse` |
| GET | `/api/v1/incidents/` | Lista incidentes; filtros: viaje, código, estado, prioridad, creador, revisor e intervalo de fechas. | `list[IncidentResponse]` |
| GET | `/api/v1/incidents/{incident_id}` | Obtiene el detalle, el viaje, usuarios relacionados y archivos multimedia. | `IncidentResponseExtended` |
| PUT | `/api/v1/incidents/{incident_id}` | Actualiza un incidente; registra al usuario autenticado como revisor. | `IncidentResponse` |
| POST | `/api/v1/incident_media/` | Sube un archivo multipart asociado a `incident_id`; incluye `type`, `file` y metadatos opcionales. | `201`, `IncidentMediaResponse` |
| DELETE | `/api/v1/incident_media/{file_id}` | Elimina un archivo; un conductor solo puede eliminar los archivos que subió. | `204 No Content` |

### Catálogo de códigos

| Método | Ruta | Descripción | Respuesta |
|---|---|---|---|
| GET | `/api/v1/codes/` | Consulta códigos filtrando opcionalmente por `severity`, `category`, `type` e `is_enabled`. | `list[EventCodeResponse]` |

Los códigos iniciales se sincronizan con `python -m db.seed`. Consulta el
[catálogo documentado](../db/event-codes.md).
