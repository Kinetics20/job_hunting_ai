import datetime as dt

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text, DateTime, func, Date, ForeignKey

from app.core.database import Base



class Experience(Base):
    __tablename__ = "experiences"

    id: Mapped[int] = mapped_column(primary_key=True)
    resume_id: Mapped[int] = mapped_column(ForeignKey('resumes.id', ondelete="CASCADE"), nullable=False)

    job_title: Mapped[str] = mapped_column(String, nullable=False)
    company: Mapped[str] = mapped_column(String, nullable=False)
    location: Mapped[str | None] = mapped_column(String, nullable=True)
    start_date: Mapped[dt.datetime] = mapped_column(Date, nullable=False)
    end_date: Mapped[dt.datetime | None] = mapped_column(Date, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    challenge: Mapped[str | None] = mapped_column(Text, nullable=True)

    resume: Mapped['Resume'] = relationship(back_populates="experiences")

