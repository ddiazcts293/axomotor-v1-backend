from enum import Enum
from pydantic import BaseModel

class TokenCreate(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenRefresh(BaseModel):
    refresh_token: str
