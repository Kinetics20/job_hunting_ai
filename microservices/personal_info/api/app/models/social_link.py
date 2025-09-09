from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey
from pydantic import HttpUrl
from app.core.database import Base


class SocialLink(Base):
    __tablename__ = "social_link"

    id: Mapped[int] = mapped_column(primary_key=True)
    resume_id: Mapped[int] = mapped_column(ForeignKey('resumes.id', ondelete="CASCADE"), nullable=False)

    url: Mapped[HttpUrl] = mapped_column(String, nullable=False)
    platform: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True, default="")
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)

    resume: Mapped['Resume'] = relationship(back_populates="social_links")