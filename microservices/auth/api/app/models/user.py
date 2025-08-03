import datetime as dt
import enum

from pydantic import EmailStr
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean, Enum, DateTime, func

from app.core.database import Base

class UserRole(enum.Enum):
    user = "user"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[EmailStr] = mapped_column(String(255), nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.user, nullable=False)

    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)


    def __repr__(self) -> str:
        return (
            f'User(email={self.email!r}, full_name={self.full_name}, role={self.role!r}), '
            f'is_active={self.is_active!r}, is_verified={self.is_verified!r})'
        )

    def __str__(self) -> str:
        return f'User {self.id}: {self.email} ({self.role.value})'

