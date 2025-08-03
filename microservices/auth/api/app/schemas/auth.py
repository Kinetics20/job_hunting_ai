from typing import Literal
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr = Field(description="User email address")
    password: str = Field(min_length=8, description="User password")


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="Access token used for authentication.")
    refresh_token: str = Field(..., description="Refresh token to obtain new access tokens.")
    token_type: Literal["bearer"] = Field(default="bearer", description="Type of the issued token. Always 'bearer'.")


class TokenRefreshRequest(BaseModel):
    refresh_token: str = Field(..., description="Refresh token from cookie or body.")