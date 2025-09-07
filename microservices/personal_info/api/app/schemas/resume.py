import datetime as dt

from pydantic import BaseModel, Field, HttpUrl, ConfigDict


class ResumeCreate(BaseModel):
    professional_title: str | None = Field(None, description="CV headline/title, e.g. Python Developer")
    summary: str | None = Field(None, description="Professional summary/about me")
    location: str = Field(..., description="City/country")
    phone: str = Field(..., description="Phone number")
    image_url: HttpUrl | None = Field(None, description="Profile image URL")


class ResumeUpdate(BaseModel):
    professional_title: str | None = None
    summary: str | None = None
    location: str | None = None
    phone: str | None = None
    image_url: HttpUrl | None = None


class ResumeOut(ResumeCreate):
    id: int
    user_id: int
    created_at: dt.datetime
    updated_at: dt.datetime

    model_config = ConfigDict(
        from_attributes=True
    )