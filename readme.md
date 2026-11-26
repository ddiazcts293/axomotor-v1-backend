# AxoMotor API REST

Repositorio del backend del sistema AxoMotor, implementado con FastAPI, SQLModel y
PostgreSQL/PostGIS.

## Descripción

AxoMotor es un sistema de monitoreo vehicular que protege el automóvil de robos e intrusiones y registra lo que ocurre en un percance vial. Se compone de un módulo instalado en el vehículo, un servidor en la nube, una plataforma web para consultar la información y una aplicación móvil que recibe las alertas.

## Instalación

> [!IMPORTANT]
> Para registrar los códigos de eventos e incidencias es necesario aplicar las migraciones y sincronizar el catálogo con el paso 6.

**Componentes requeridos:**

- Git
- Python y pip compatibles con las dependencias de `requirements.txt`
- Docker Compose

**Pasos:**

1. Clonar este repositorio.
```bash
git clone https://github.com/ddiazcts293/axomotor-v1-backend.git
```
2. Inicializar un nuevo entorno virtual de Python en el directorio del proyecto (usar `py` en Windows).

```bash
python -m venv .venv
```
3. Instalar dependencias.
```bash
pip install -r requirements.txt
```
4. Crear una copia de `template.env` llamada `.env` y establecer la configuración del entorno. Se puede utilizar [RandomKeygen](https://randomkeygen.com/) para generar los valores de API Keys y JWT Secrets.
5. Levantar contenedores con Docker.
```bash
docker compose up -d
```
6. Aplicar migraciones y sincronizar el catálogo inicial de códigos.
```bash
alembic upgrade head
python -m db.seed
```
7. Iniciar servidor API rest de FastAPI.
```bash
fastapi dev
```

El servidor se inicia en `http://localhost:8000`. La interfaz interactiva de la
API se publica en `/docs` y el documento OpenAPI en `/openapi.json`.

**URLs:**

- Swagger: [http://localhost:8000/docs/](http://localhost:8000/docs/)
- Salud de la API: [http://localhost:8000/health](http://localhost:8000/health)
- MinIO: [http://localhost:9001/](http://localhost:9001/)
- Adminer: [http://localhost:8080/](http://localhost:8080/)

El consumidor MQTT se ejecuta por separado con `python -m workers.mqtt.consumer`;
requiere las variables de configuración descritas en `template.env`.

## Contribuir

Para realizar cambios en este repositorio es necesario crear un fork y una nueva rama especificando la contribución que se está realizando. Usar nombres cortos y descriptivos, de preferencia en minúsculas.

**Lineamientos**:
- El código del proyecto debe estar escrito en inglés, pero los comentarios si pueden estar en español.
- Usar la convención snake_case para nombrar archivos, variables o funciones.
- Usar la convención PascalUpperCase para nombrar clases.

## Documentación

- [Modelos DB](models/readme.md)
- [Referencia de API](api/readme.md)
- [Contratos de entrada y salida (schemas)](schemas/readme.md)
- [Referencia de códigos de eventos](db/event-codes.md)
- [Generador de datos de muestra](db/sample_data/README.md)
- [Consumidor MQTT](workers/mqtt/readme.md)

Las descripciones de operaciones y campos de Swagger se mantienen en las rutas y
schemas de la aplicación. Al cambiar una ruta, modelo o contrato, actualiza en el
mismo cambio su referencia Markdown correspondiente.
