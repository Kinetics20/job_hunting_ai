import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv(dotenv_path=Path("../.envs/.env"))


class Settings(BaseSettings):
    POSTGRES_USER: str = Field(..., alias="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(..., alias="POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field(..., alias="POSTGRES_DB")
    POSTGRES_PORT: int = Field(5432, alias="POSTGRES_PORT")
    POSTGRES_HOST: str = Field(..., alias="POSTGRES_HOST")
    POSTGRES_ASYNC_DRIVER: str = "postgresql+asyncpg://"
    POSTGRES_SYNC_DRIVER: str = "postgresql+psycopg://"

    SECRET_KEY: str = Field(..., alias="SECRET_KEY")
    SALT_EMAIL: str = Field(..., alias="SALT_EMAIL")

    JWT_PRIVATE_KEY: str = Field(..., alias="JWT_PRIVATE_KEY")
    JWT_PUBLIC_KEY: str = Field(..., alias="JWT_PUBLIC_KEY")
    JWT_ALGORITHM: str = Field("RS256", alias="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(7, alias="REFRESH_TOKEN_EXPIRE_DAYS")

    REDIS_HOST: str = Field(..., alias="REDIS_HOST")
    REDIS_PORT: int = Field(6379, alias="REDIS_PORT")
    REDIS_DB: int = Field(0, alias="REDIS_DB")

    REDIS_PASSWORD_FILE: str = "../.secrets/redis_password"

    FRONTEND_URL: str = "http://localhost"
    EMAIL_VERIFICATION_ENDPOINT: str = '/verify-email/'

    MAX_LOGIN_ATTEMPTS: int = 5
    BLOCK_TIME_SECONDS: int = 15 * 60
    BLOCK_TIME_IP_SECONDS: int = 20
    MAX_LOGIN_ATTEMPTS_PER_IP: int = 30 * 60

    BLACKLIST_EXPIRES_SECONDS: int = 15 * 60


    @property
    def REDIS_PASSWORD(self) -> str:
        path = Path(self.REDIS_PASSWORD_FILE)
        if path.exists():
            return path.read_text().strip()
        return os.environ.get("REDIS_PASSWORD", "")

    @property
    def REDIS_URI(self) -> str:
        return f'redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}'

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def JWT_PRIVATE_KEY_PEM(self) -> str:
        return self.JWT_PRIVATE_KEY.replace("\\n", "\n")

    @property
    def JWT_PUBLIC_KEY_PEM(self) -> str:
        return self.JWT_PUBLIC_KEY.replace("\\n", "\n")


settings = Settings()  # type: ignore