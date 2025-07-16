from sqlalchemy import select

from fastapi import APIRouter, Depends, HTTPException, status

from api.app.core.database import get_db
from api.app.models.social_link import SocialLink
from api.app.schemas.social_link import SocialLinkOut, SocialLinkCreate, SocialLinkUpdatePartially, SocialLinkUpdate
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(prefix="/social-links", tags=["Social Links"])


@router.post('/', response_model=list[SocialLinkOut])
async def add_social_link(
        links: list[SocialLinkCreate],
        db=Depends(get_db)
):
    user_id = 1

    created = []

    for link in links:
        item = SocialLink(user_id=user_id, **link.model_dump())
        db.add(item)
        created.append(item)

    await db.commit()

    for item in created:
        await db.refresh(item)

    return created


@router.get('/', response_model=list[SocialLinkOut])
async def get_social_links(
        db: AsyncSession = Depends(get_db),
) -> list[SocialLinkOut]:
    stmt = select(SocialLink).where(SocialLink.user_id == 1)
    results = await db.execute(stmt)
    return results.scalars().all()


@router.get('/{id}/', response_model=SocialLinkOut)
async def get_social_link(
        id: int,
        db: AsyncSession = Depends(get_db),
) -> SocialLinkOut:
    stmt = select(SocialLink).where(SocialLink.user_id == 1, SocialLink.id == id)
    result = await db.execute(stmt)
    link = result.scalar_one_or_none()

    if link is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Social Link Not Found")

    return result.scalars().all()


@router.patch('/{id}/', response_model=SocialLinkOut)
async def update_social_link(
        id: int,
        update_data: SocialLinkUpdate,
        db: AsyncSession = Depends(get_db),
) -> SocialLinkOut:
    stmt = select(SocialLink).where(SocialLink.id == id, SocialLink.user_id == 1)
    result = await db.execute(stmt)
    link = result.scalar_one_or_none()

    if link is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Social Link Not Found")

    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(link, field, value)

    await db.commit()
    await db.refresh(link)

    return link


@router.delete('/{id}/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_social_link(
        id: int,
        db: AsyncSession = Depends(get_db),
) -> None:
    stmt = select(SocialLink).where(SocialLink.id == id, SocialLink.user_id == 1)
    result = await db.execute(stmt)
    link = result.scalar_one_or_none()

    if link is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Social Link Not Found")

    await db.delete(link)
    await db.commit()
