from pydantic import BaseModel, HttpUrl, model_validator, field_serializer


class SocialLinkCreate(BaseModel):
    platform: str
    url: HttpUrl

    @field_serializer("url")
    def serialize_url(self, url: HttpUrl) -> str:
        return str(url)


class SocialLinkUpdate(SocialLinkCreate):
    pass


class SocialLinkUpdatePartially(BaseModel):
    platform: str | None = None
    url: HttpUrl | None = None

    @field_serializer("url")
    def serialize_url(self, url: HttpUrl) -> str:
        return str(url)


class SocialLinkOut(SocialLinkCreate):
    id: int

    model_config = {
        "from_attributes": True
    }
