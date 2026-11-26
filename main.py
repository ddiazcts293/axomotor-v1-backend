from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from sqlmodel import SQLModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from api.v1 import (
    users_router,
    drivers_router,
    link_router,
    vehicles_router,
    locations_router,
    alerts_router,
    event_codes_router,
    vehicle_devices_router,
    vehicle_services_router,
    trips_router,
    incidents_router,
    positions_router,
    incident_media_router,
)

from core.config import settings
from db.database import engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    if not settings.USE_ALEMBIC:
        SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(users_router, prefix='/api/v1/users', tags=['Users'])
app.include_router(alerts_router, prefix='/api/v1/alerts', tags=['User alerts'])
app.include_router(drivers_router, prefix='/api/v1/drivers', tags=['Drivers'])
app.include_router(vehicles_router, prefix='/api/v1/vehicles', tags=['Vehicles'])
app.include_router(vehicle_services_router, prefix='/api/v1/vehicle_services', tags=['Vehicle services'])
app.include_router(vehicle_devices_router, prefix='/api/v1/vehicle_devices', tags=['Vehicle devices'])
app.include_router(locations_router, prefix='/api/v1/locations', tags=['Known locations'])
app.include_router(positions_router, prefix='/api/v1/tracking', tags=['Tracking'])
app.include_router(trips_router, prefix='/api/v1/trips', tags=['Trips'])
app.include_router(incidents_router, prefix='/api/v1/incidents', tags=['Incidents'])
app.include_router(incident_media_router, prefix='/api/v1/incident_media', tags=['Incident Media'])
app.include_router(event_codes_router, prefix='/api/v1/codes', tags=['Event Code catalog'])
app.include_router(link_router, prefix='/api/v1/link_bot', tags=['Link Telegram Bot'])

@app.get('/health', tags=['Health'])
def health_check() -> dict[str, str]:
    return {'status': 'healthy'}

@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=409,
        content={"detail": "The entry cannot be added (duplicated or invalid reference)"},
    )
