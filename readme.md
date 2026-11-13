# AxoMotor API rest

Este es el repositorio para el proyecto del servidor API rest usando FastAPI.

## Descripción

AxoMotor es un sistema de monitoreo vehicular que protege el automóvil de robos e intrusiones y registra lo que ocurre en un percance vial. Se compone de un módulo instalado en el vehículo, un servidor en la nube, una plataforma web para consultar la información y una aplicación móvil que recibe las alertas.

## Instalación

**Componentes requieridos:**

- Git
- Python 3.14 & pip
- Docker Compose

**Pasos:**

1. Clonar este repositorio `git clone https://github.com/ddiazcts293/axomotor-v1-backend.git`.
2. Inicializar un nuevo entorno virtual de Python en el directorio del proyecto `python -m venv .venv` (usar `py` en Windows).
3. Instalar dependencias `pip install -r requirements.txt`.
4. Crear una copia de `template.env` llamada `.env` y establecer la configuración del entorno.
5. Levantar contendores con Docker `docker compose up -d`.
6. Aplicar migraciones con `alembic upgrade head`.
7. Iniciar servidor API rest con `fastapi dev`.

El sitio es accesible a través del localhost en el puerto 8000.

**URLs:**

- Swagger: `http://localhost:8000/docs/`
- MinIO: `http://localhost:9001/`
- Adminer: `http://localhost:8080/`

## Contribuir

Para realizar cambios en este repositorio es necesario crear un fork y una nueva rama especificando la contribución que se está realizando. Usar nombres cortos y descriptivos, de preferencia en minúsculas.

**Lineamientos**:
- El código del proyecto debe estar escrito en inglés, pero los comentarios si pueden estar en español.
- Usar la convención snake_case para nombrar archivos, variables o funciones.
- Usar la convención PascalUpperCase para nombrar clases.

## Documentación

- [Referencia de API](api/readme.md)
