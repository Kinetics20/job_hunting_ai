import datetime as dt

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text, DateTime, func, Date, ForeignKey
from pydantic import HttpUrl
from app.core.database import Base



class Certificate(Base):
    __tablename__ = "certificates"

    id: Mapped[int] = mapped_column(primary_key=True)
    resume_id: Mapped[int] = mapped_column(ForeignKey('resumes.id', ondelete="CASCADE"), nullable=False)

    issuer: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str | None] = mapped_column(String, nullable=False)
    date: Mapped[dt.date] = mapped_column(Date, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    link: Mapped[HttpUrl] = mapped_column(String, nullable=False)


    resume: Mapped['Resume'] = relationship(back_populates="certificates")

