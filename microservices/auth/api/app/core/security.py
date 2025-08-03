import datetime as dt

from fastapi import Request
from fastapi.security import OAuth2PasswordBearer
from itsdangerous import URLSafeTimedSerializer
from jose import jwt
from passlib.context import CryptContext
from pydantic import EmailStr

from app.core.config import settings

pwd_context = CryptContext(schemes=['argon2', "bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_password_hash(password: str) -> str:
    """Hash a password for storing."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a hashed password against one provided by the user."""
    return pwd_context.verify(plain_password, hashed_password)



def create_access_token(subject: str, roles: list[str]) -> str:
    """Generuje access token JWT podpisany RSA."""
    expire = dt.datetime.now() + dt.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "iat": dt.datetime.now(),
        "roles": roles
    }
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_PRIVATE_KEY_PEM,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt

def create_refresh_token(subject: str) -> str:
    """Generuje refresh token JWT podpisany RSA."""
    expire = dt.datetime.now() + dt.timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "iat": dt.datetime.now(),
        "token_type": "refresh"
    }
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_PRIVATE_KEY_PEM,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt

def decode_token(token: str) -> dict:
    """Dekoduje i weryfikuje JWT z podpisem RSA."""
    return jwt.decode(
        token,
        settings.JWT_PRIVATE_KEY_PEM,
        algorithms=[settings.JWT_ALGORITHM],
    )

def get_email_token_serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(settings.SECRET_KEY, salt=settings.SALT_EMAIL)

def generate_email_verification_token(email: EmailStr) -> str:
    serializer = get_email_token_serializer()
    return serializer.dumps(email)

def verify_user_email(token: str):
    pass

def get_remote_ip(request: Request) -> str:
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host