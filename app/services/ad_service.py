from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ad import Ad, AdStatus, Category
from app.repositories.ad_repo import AdRepository


class AdService:
    def __init__(self, session: AsyncSession):
        self.repo = AdRepository(session)

    async def create_ad(
        self,
        user_id: int,
        category: Category,
        title: str,
        description: str,
        price: str | None,
        contact_phone: str,
        photo_file_ids: list[str] | None = None,
    ) -> Ad:
        return await self.repo.create(
            user_id=user_id,
            category=category,
            title=title,
            description=description,
            price=price,
            contact_phone=contact_phone,
            photo_file_ids=photo_file_ids,
        )

    async def submit_for_review(self, ad_id: int, admin_message_id: int) -> Ad | None:
        return await self.repo.update_status(
            ad_id, AdStatus.PENDING, admin_message_id=admin_message_id
        )

    async def approve(self, ad_id: int, main_message_id: int) -> Ad | None:
        return await self.repo.update_status(
            ad_id, AdStatus.APPROVED, main_channel_message_id=main_message_id
        )

    async def reject(self, ad_id: int) -> Ad | None:
        return await self.repo.update_status(ad_id, AdStatus.REJECTED)

    async def get_ad(self, ad_id: int) -> Ad | None:
        return await self.repo.get_by_id(ad_id)
