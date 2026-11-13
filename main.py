from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import SQLModel
from fastapi.middleware.cors import CORSMiddleware

# from models import user
# from api.v1.user_api import router as users_router
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

# app.include_router(users_router, prefix='/api/v1/users', tags=['Users'])

@app.get('/health', tags=['Health'])
def health_check() -> dict[str, str]:
    return {'status': 'healthy'}
