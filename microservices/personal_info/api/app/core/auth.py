from typing import Any

from fastapi import HTTPException, status, Request, Depends
from jose import jwt, JWTError, ExpiredSignatureError
from mypy.build import TypedDict
from pydantic import ValidationError

from app.core.config import settings
from app.schemas.user import AccessTokenPayload


def verify_jwt_token(token: str) -> AccessTokenPayload:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_PUBLIC_KEY_PEM,
            algorithms=[settings.JWT_ALGORITHM],
        )


        return AccessTokenPayload.model_validate(payload)

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired.",
        )
    except (JWTError, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


def get_token_payload(request: Request) -> AccessTokenPayload:
    authorization_header = request.headers.get("Authorization")
    if not authorization_header or not authorization_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
        )

    token = authorization_header.split(" ", 1)[1]
    return verify_jwt_token(token)


def get_user_id(request: Request, token=Depends(get_token_payload)) -> int:
    return token.sub
