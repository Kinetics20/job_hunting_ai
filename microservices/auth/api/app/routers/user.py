from typing import Annotated
from redis.asyncio import Redis
import datetime as dt
from app.celery_worker import send_activation_email

from fastapi import APIRouter, status, Depends, HTTPException, Body, Query, Response, Request, Cookie
from itsdangerous import SignatureExpired, BadSignature
from jose import jwt, ExpiredSignatureError, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import get_redis, is_refresh_token_blacklisted, blacklist_refresh_token, blacklist_refresh_token
from app.core.config import settings
from app.core.database import get_db
from app.core.login_bruteforce import is_login_blocked, record_failed_login, reset_login_attempts, \
    record_failed_login_email, record_failed_login_ip, reset_login_attempts_email, reset_login_attempts_ip, \
    is_ip_blocked
from app.core.security import verify_user_email, get_email_token_serializer, verify_password, create_access_token, \
    create_refresh_token, get_remote_ip, generate_email_verification_token
from app.crud.user import get_user_by_email, create_user, get_user_by_id
from app.schemas.auth import TokenResponse, LoginRequest, TokenRefreshRequest
from app.schemas.user import UserOut, UserCreate

router = APIRouter(prefix="/auth", tags=["auth", "users"])


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED
)
async def register_user(
        user_in: Annotated[UserCreate, Body()],
        db: Annotated[AsyncSession, Depends(get_db)]
):
    existing = await get_user_by_email(db, email=user_in.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = await create_user(db, user_in)
    token = generate_email_verification_token(user.email)
    verify_url = f"{settings.FRONTEND_URL}{settings.EMAIL_VERIFICATION_ENDPOINT}?token={token}"
    send_activation_email.delay(user.email, verify_url)
    return user


@router.get('/verify-email',
            response_model=dict,
            status_code=status.HTTP_200_OK,
            summary="Verify user Email address",
            description="Verify user Email address"
            )
async def verify_email(
        token: Annotated[str, Query(..., description='Email verification token')],
        db: Annotated[AsyncSession, Depends(get_db)]
):
    serializer = get_email_token_serializer()

    try:
        email = serializer.loads(token, max_age=3600 * 24)
    except SignatureExpired:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token expired")
    except BadSignature:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")

    user = await get_user_by_email(db, email)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user.is_verified:
        return {'detail': 'User is verified'}, status.HTTP_200_OK

    user.is_verified = True
    user.is_active = True

    await db.commit()

    return {'detail': 'Email verified'}


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="User login",
    description="Authenticate user and issue access/refresh tokens."
)
async def login(
        login_in: Annotated[LoginRequest, Body()],
        db: Annotated[AsyncSession, Depends(get_db)],
        response: Response,
        redis: Annotated[Redis, Depends(get_redis)],
        request: Request
) -> TokenResponse:
    """
    Authenticates user and returns access/refresh JWT tokens.

    Args:
        login_in (LoginRequest): Login credentials.
        db (AsyncSession): Database session.
        response (Response, optional): Response object for cookies.
        redis: Redis.
        request: Request.

    Returns:
        TokenResponse: JWT tokens for the authenticated user.

    Raises:
        HTTPException: 401 if invalid credentials, inactive, or unverified.

    """

    email = login_in.email
    ip = get_remote_ip(request)

    if await is_login_blocked(redis, email) or await is_ip_blocked(redis, ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed login attempts. Please try again later.",
        )

    user = await get_user_by_email(db, login_in.email)
    if user is None or not verify_password(login_in.password, user.hashed_password):
        await record_failed_login_email(redis, email)
        await record_failed_login_ip(redis, ip)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password.")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive.")

    if not user.is_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email address not verified.")

    await reset_login_attempts_email(redis, email)
    await reset_login_attempts_ip(redis, ip)

    access_token = create_access_token(
        subject=str(user.id),
        roles=[user.role.value]
    )
    refresh_token = create_refresh_token(
        subject=str(user.id)
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=60 * 60 * 24 * settings.REFRESH_TOKEN_EXPIRE_DAYS,
        secure=True,
        samesite="lax",
        path="/",
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post(
    '/refresh',
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description='Obtain new access token using valid refresh token',
)
async def refresh_token(
        request: Request,
        response: Response,
        db: Annotated[AsyncSession, Depends(get_db)],
        refresh_token_cookie: Annotated[str | None, Cookie()] = None,
        body: TokenRefreshRequest | None = None
):
    token = (
            (body.refresh_token if body and body.refresh_token else None)
            or refresh_token_cookie
            or request.cookies.get("refresh_token")
    )
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Missing refresh token')

    if await is_refresh_token_blacklisted(token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid refresh token')

    try:
        payload = jwt.decode(
            token=token,
            key=settings.JWT_PUBLIC_KEY_PEM,
            algorithms=[settings.JWT_ALGORITHM],
        )
        token_type = payload.get('token_type')
        if token_type != 'refresh':
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token type')


    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Refresh token expired')

    except JWTError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid refresh token')

    user_id = payload.get('sub')

    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid refresh token payload')

    user = await get_user_by_id(int(user_id), db)
    if not user or not user.is_verified or not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is not active or not verified")

    exp = payload.get('exp')
    if exp:
        ttl = int(exp - dt.datetime.now(dt.timezone.utc).timestamp())
        if ttl > 0:
            await blacklist_refresh_token(token, exp=ttl)

    access_token = create_access_token(subject=str(user.id), roles=[user.role.value])
    new_refresh_token = create_refresh_token(subject=str(user.id))

    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        max_age=60 * 60 * 24 * settings.REFRESH_TOKEN_EXPIRE_DAYS,
        secure=True,
        samesite="lax",
        path="/",
    )
    return {'access_token': access_token, 'refresh_token': new_refresh_token}

@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout user (revoke refresh token)",
    description="Invalidate the current refresh token and remove it from cookies."
)
async def logout(
        request: Request,
        response: Response,
        refresh_token_cookie: Annotated[str | None, Cookie()] = None,
        body: TokenRefreshRequest | None = None,
):
    token = (
            (body.get("refresh_token") if body and "refresh_token" in body else None)
            or refresh_token_cookie
            or request.cookies.get("refresh_token")
    )

    if token:
        try:
            payload = jwt.decode(
                token,
                settings.JWT_PUBLIC_KEY_PEM,
                algorithms=[settings.JWT_ALGORITHM],
                options={"verify_aud": False},
            )
            if exp := payload.get("exp"):
                ttl = int(exp - dt.datetime.now(dt.timezone.utc).timestamp())
                if ttl > 0:
                    await blacklist_refresh_token(token, ttl)
        except (ExpiredSignatureError, JWTError):
            pass

    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=True,
        samesite="lax",
        path="/"
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)