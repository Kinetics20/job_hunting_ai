from datetime import datetime
import enum
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, constr, ConfigDict, field_serializer


class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"


class UserBase(BaseModel):
    email: Annotated[EmailStr, Field(description="User email address.")]
    full_name: Annotated[str | None, Field(default=None, description="Full name of the user.")]

    @field_serializer('email')
    def serialize_email(self, email: EmailStr) -> str:
        return str(email)


class UserCreate(UserBase):
    password: Annotated[
        constr(min_length=8),
        Field(description="User password, minimum 8 characters long."),
    ]

    model_config = ConfigDict(
        from_attributes=True
    )


class UserOut(UserBase):
    id: int = Field(description="User ID.")
    is_active: bool = Field(description="Is user active?")
    is_verified: bool = Field(description="Is user verified?")
    role: UserRole = Field(description="User role")
    created_at: datetime = Field(description="Account creation timestamp.")

    model_config = ConfigDict(
        from_attributes=True
    )


class UserInDB(UserOut):
    hashed_password: str = Field(description="Password hash (only for internal use).")

