from typing import Annotated

from fastapi import APIRouter, status, Body, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_user_id
from app.core.database import get_db
from app.core.permissions import is_owner
from app.crud.resume import get_resume_by_user_id
from app.models import Resume
from app.schemas.resume import ResumeOut, ResumeCreate

router = APIRouter(prefix="/resumes", tags=["Resume"])


@router.post(
    "/",
    response_model=ResumeOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create resume",
    description="Create resume but longer",
)
async def create_resume(
        resume_in: Annotated[ResumeCreate, Body()],
        db: Annotated[AsyncSession, Depends(get_db)],
        user_id: Annotated[int, Depends(get_user_id)]
):
    resume = await get_resume_by_user_id(user_id, db)

    if resume:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Resume already exists for this user."
        )

    obj = Resume(**resume_in.model_dump(), user_id=user_id)

    db.add(obj)
    await db.commit()
    await db.refresh(obj)

    return obj

# @router.get('/')
# async def get_resume(
#         user_id: Annotated[int, Depends(get_user_id)],
#         perm: Annotated[dict, Depends(is_owner)]
# ):
#     pass
