from enum import Enum
from pydantic import BaseModel, Field

class TokenCreate(BaseModel):
    access_token: str = Field(description="Token Bearer de corta duración para autenticar solicitudes.")
    refresh_token: str = Field(description="Token de renovación para obtener un nuevo par de tokens.")
    token_type: str = Field(default="bearer", description="Esquema de autenticación; actualmente siempre es bearer.")

class TokenRefresh(BaseModel):
    refresh_token: str = Field(description="Token de renovación vigente recibido al iniciar sesión.")
