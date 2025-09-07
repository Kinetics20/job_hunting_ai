from typing import Annotated

from sqlalchemy import select

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from app.core.auth import get_user_id
from app.core.database import get_db
from app.models.social_link import SocialLink
from app.schemas.social_link import SocialLinkOut, SocialLinkCreate, SocialLinkUpdate, SocialLinkUpdatePartially
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/social-links", tags=["Social Links"])


@router.post(
    "/",
    response_model=list[SocialLinkOut],
    status_code=status.HTTP_201_CREATED,
    summary="Bulk add social links for the current user",
    description="Add multiple social links to the current user",
)
async def add_social_links(
        links: Annotated[list[SocialLinkCreate], ...],
        db: Annotated[AsyncSession, Depends(get_db)],
        user_id: Annotated[int, Depends(get_user_id)]
) -> list[SocialLinkOut]:
    created_links: list[SocialLink] = []

    print("*" * 20)
    print(user_id, type(user_id))
    print("*" * 20)

    try:
        for link in links:
            item = SocialLink(user_id=user_id, **link.model_dump())
            db.add(item)
            created_links.append(item)

        await db.commit()

        for item in created_links:
            await db.refresh(item)

        return [SocialLinkOut.model_validate(item, from_attributes=True) for item in created_links]

    except SQLAlchemyError as err:
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add social links: {err.__class__.__name__}"
        )


@router.get("/", response_model=list[SocialLinkOut])
async def get_social_links(
        user_id: Annotated[int, Depends(get_user_id)],
        db: AsyncSession = Depends(get_db)
) -> list[SocialLinkOut]:
    stmt = select(SocialLink).where(SocialLink.user_id == user_id)
    results = await db.execute(stmt)
    return results.scalars().all()


@router.get("/{id}/", response_model=SocialLinkOut)
async def get_social_link(
        id: int,
        db: AsyncSession = Depends(get_db),
) -> SocialLinkOut:
    stmt = select(SocialLink).where(SocialLink.user_id == 1, SocialLink.id == id)
    result = await db.execute(stmt)
    link = result.scalar_one_or_none()

    if link is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Social Link not found.")

    return link


@router.patch("/{id}/", response_model=SocialLinkOut)
async def update_partially_social_link(
        id: int,
        update_data: SocialLinkUpdate,
        db: AsyncSession = Depends(get_db),
) -> SocialLinkOut:
    stmt = select(SocialLink).where(SocialLink.id == id, SocialLink.user_id == 1)
    result = await db.execute(stmt)
    link = result.scalar_one_or_none()

    if link is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Social Link not found.")

    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(link, field, value)

    await db.commit()
    await db.refresh(link)

    return link


@router.delete("/{id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_social_link(
        id: int,
        db: AsyncSession = Depends(get_db),
) -> None:
    stmt = select(SocialLink).where(SocialLink.id == id, SocialLink.user_id == 1)
    result = await db.execute(stmt)
    link = result.scalar_one_or_none()

    if link is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Social Link not found.")

    await db.delete(link)
    await db.commit()
