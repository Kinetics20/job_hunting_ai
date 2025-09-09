from enum import Enum

from pydantic import BaseModel, Field


class UserRole(str, Enum):
    user = "user"
    admin = "admin"


class AccessTokenPayload(BaseModel):
    sub: int = Field(..., description="Subject: user ID (string).")
    exp: int = Field(..., description="Expiration time (integer).")
    iat: int = Field(..., description="Issued-at time (integer).")
    roles: list[UserRole] = Field(..., description="List of user's roles.")