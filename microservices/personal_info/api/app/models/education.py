import datetime as dt

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text, DateTime, func, Date, ForeignKey

from app.core.database import Base



class Education(Base):
    __tablename__ = "education"

    id: Mapped[int] = mapped_column(primary_key=True)
    resume_id: Mapped[int] = mapped_column(ForeignKey('resumes.id', ondelete="CASCADE"), nullable=False)

    school: Mapped[str] = mapped_column(String, nullable=False)
    degree: Mapped[str | None] = mapped_column(String, nullable=True)
    field_of_study: Mapped[str] = mapped_column(String, nullable=True)

    location: Mapped[str | None] = mapped_column(String, nullable=True)
    start_date: Mapped[dt.datetime] = mapped_column(Date, nullable=False)
    end_date: Mapped[dt.datetime | None] = mapped_column(Date, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)


    resume: Mapped['Resume'] = relationship(back_populates="education")

