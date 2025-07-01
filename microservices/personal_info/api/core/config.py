from pathlib import Path
import os

from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path("../../envs/.env"))


class Settings(BaseSettings):
    POSTGRES_USER: str | None = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str | None = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB: str | None = os.getenv("POSTGRES_DB")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5442"))
    POSTGRES_HOST: str | None = os.getenv("POSTGRES_HOST")

    DATABASE_URL: str = f'postgresql+async://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'

settings = Settings()