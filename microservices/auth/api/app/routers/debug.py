from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr

from app.core.config import settings
from app.core.database import get_db
from app.core.security import generate_email_verification_token
from app.crud.user import get_user_by_email

router = APIRouter(prefix="/debug", tags=["debug"])

@router.post('/generate-verification-link')
async def debug_generating_email_link(email: Annotated[EmailStr, Body()], db: Annotated[AsyncSession, Depends(get_db)]):
    user = await get_user_by_email(db, email)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    token = generate_email_verification_token(user.email)
    url = f"{settings.FRONTEND_URL}{settings.EMAIL_VERIFICATION_ENDPOINT}?token={token}"
    return {'url': url}
