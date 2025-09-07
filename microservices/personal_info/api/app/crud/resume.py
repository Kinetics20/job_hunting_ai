from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Resume


async def get_resume_by_user_id(user_id: int, db: AsyncSession) -> Resume | None:
    resume = await db.execute(select(Resume).where(Resume.user_id == user_id))
    return resume.scalars().first()
