from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user_repo import UserRepository


class UserService:
    def __init__(self, session: AsyncSession):
        self.repo = UserRepository(session)

    async def get_or_none(self, telegram_id: int) -> User | None:
        return await self.repo.get_by_telegram_id(telegram_id)

    async def register(
        self, telegram_id: int, phone_number: str, full_name: str
    ) -> User:
        return await self.repo.create(telegram_id, phone_number, full_name)
