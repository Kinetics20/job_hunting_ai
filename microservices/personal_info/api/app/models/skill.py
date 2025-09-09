import datetime as dt

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text, DateTime, func, Date, ForeignKey

from app.core.database import Base



class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(primary_key=True)
    resume_id: Mapped[int] = mapped_column(ForeignKey('resumes.id', ondelete="CASCADE"), nullable=False)

    name: Mapped[str] = mapped_column(String, nullable=True)
    level: Mapped[str | None] = mapped_column(String, nullable=True)


    resume: Mapped['Resume'] = relationship(back_populates="skills")

