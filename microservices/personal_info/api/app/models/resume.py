import datetime as dt

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text, DateTime, func

from app.core.database import Base



class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)

    professional_title: Mapped[str | None] = mapped_column(String, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    location: Mapped[str] = mapped_column(String)
    phone: Mapped[str] = mapped_column(String)
    image_url: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[dt.datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    experiences: Mapped[list['Experience']] = relationship(back_populates="resume", cascade="all, delete")
    education: Mapped[list['Education']] = relationship(back_populates="resume", cascade="all, delete")
    skills: Mapped[list['Skill']] = relationship(back_populates="resume", cascade="all, delete")
    projects: Mapped[list['Project']] = relationship(back_populates="resume", cascade="all, delete")
    certificates: Mapped[list['Certificate']] = relationship(back_populates="resume", cascade="all, delete")
    social_links: Mapped[list['SocialLink']] = relationship(back_populates="resume", cascade="all, delete")
    languages: Mapped[list['Language']] = relationship(back_populates="resume", cascade="all, delete")
