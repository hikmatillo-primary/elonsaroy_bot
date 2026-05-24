from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.ad import Ad, AdStatus, Category


class AdRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        user_id: int,
        category: Category,
        title: str,
        description: str,
        price: str | None,
        contact_phone: str,
        photo_file_ids: list[str] | None = None,
    ) -> Ad:
        ad = Ad(
            user_id=user_id,
            category=category,
            title=title,
            description=description,
            price=price,
            contact_phone=contact_phone,
            photo_file_ids=photo_file_ids,
            status=AdStatus.DRAFT,
        )
        self.session.add(ad)
        await self.session.commit()
        await self.session.refresh(ad)
        return ad

    async def get_by_id(self, ad_id: int) -> Ad | None:
        result = await self.session.execute(
            select(Ad).options(joinedload(Ad.user)).where(Ad.id == ad_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: int) -> list[Ad]:
        result = await self.session.execute(
            select(Ad)
            .options(joinedload(Ad.user))
            .where(Ad.user_id == user_id)
            .order_by(Ad.created_at.desc())
        )
        return list(result.scalars().all())

    async def update_status(
        self, ad_id: int, status: AdStatus, **kwargs: int | None
    ) -> Ad | None:
        ad = await self.get_by_id(ad_id)
        if ad is None:
            return None
        ad.status = status
        for key, value in kwargs.items():
            setattr(ad, key, value)
        await self.session.commit()
        await self.session.refresh(ad)
        return ad
