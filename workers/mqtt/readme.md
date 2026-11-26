# Consumidor MQTT de AxoMotor

El consumidor escucha mensajes publicados por los dispositivos del vehículo y
registra posiciones directamente en la base de datos. Los eventos e incidentes se
envían al backend mediante HTTP usando la API key configurada para el servicio.

## Tópicos recibidos

El prefijo de los tópicos es `axomotor/v1/vehicles/{vehicle_id}`. El identificador
debe ser un UUID de vehículo.

| Tópico | Mensaje esperado | Procesamiento |
|---|---|---|
| `.../{vehicle_id}/position` | JSON de posición | Valida coordenadas, viaje opcional, velocidad y fecha; inserta una posición. |
| `.../{vehicle_id}/event` | Evento de vehículo | Reenvía el JSON a `POST /api/v1/vehicles/{vehicle_id}/events`. |
| `.../{vehicle_id}/incident` | Incidente | Reenvía el JSON a `POST /api/v1/incidents/`. |
| `.../{vehicle_id}/ack` | Acuse de recibo | Actualmente no se procesa ni se suscribe el consumidor. |

## Forma de los mensajes

Los mensajes de posición aceptan `latitude` y `longitude` juntos (coordenadas
WGS 84, latitud entre -90 y 90 y longitud entre -180 y 180), `registered_at`
(fecha y hora), `trip_id` (campo requerido que acepta UUID o `null`) y `speed`
en km/h (0–300, predeterminado 0).
Se rechazan coordenadas incompletas o el punto `(0, 0)`.

Los mensajes de evento admiten `code` (máximo 12 caracteres), `registered_at`,
coordenadas opcionales como par y `additional_data` opcional en formato JSON.
Los incidentes requieren `trip_id`, `code` y `description` (2–500 caracteres);
también admiten fecha y coordenadas bajo las mismas reglas.

## Tópicos salientes

La documentación del protocolo reserva
`axomotor/v1/vehicles/{vehicle_id}/command` para comandos del sistema al vehículo.
El consumidor descrito aquí no publica comandos.

## Configuración

El proceso obtiene del entorno `MQTT_CONSUMER_HOST`, `MQTT_CONSUMER_USER`,
`MQTT_CONSUMER_PASSWORD`, `X_MQTT_CONSUMER_HOST` y
`X_MQTT_CONSUMER_API_KEY`. Los dos valores `X_MQTT_CONSUMER_*` configuran la
conexión HTTP al backend. Consulta `workers/mqtt/config.py` y `template.env`;
no almacenes credenciales en este documento.
