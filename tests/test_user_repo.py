import pytest
from sqlalchemy import select

from app.models.user import User
from app.repositories.user_repo import UserRepository


class TestUserRepository:
    @pytest.mark.asyncio
    async def test_get_by_telegram_id_returns_user(self, user_repo, mock_session, sample_user):
        mock_session.execute.return_value.scalar_one_or_none.return_value = sample_user

        user = await user_repo.get_by_telegram_id(123456789)

        assert user is sample_user
        mock_session.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_by_telegram_id_returns_none(self, user_repo, mock_session):
        mock_session.execute.return_value.scalar_one_or_none.return_value = None

        user = await user_repo.get_by_telegram_id(999999)

        assert user is None
        mock_session.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_create_user_success(self, user_repo, mock_session):
        user = await user_repo.create(
            telegram_id=123456789,
            phone_number="+998901234567",
            full_name="Test User",
        )

        mock_session.add.assert_called_once()
        added_user = mock_session.add.call_args[0][0]
        assert isinstance(added_user, User)
        assert added_user.telegram_id == 123456789
        assert added_user.phone_number == "+998901234567"
        assert added_user.full_name == "Test User"

        mock_session.commit.assert_awaited_once()
        mock_session.refresh.assert_awaited_once_with(added_user)
        assert user is not None

    @pytest.mark.asyncio
    async def test_get_by_telegram_id_uses_correct_filter(self, user_repo, mock_session):
        mock_session.execute.return_value.scalar_one_or_none.return_value = None

        await user_repo.get_by_telegram_id(555555)

        call_args = mock_session.execute.call_args[0][0]
        compiled = call_args.compile(compile_kwargs={"literal_binds": True})
        assert "telegram_id" in str(compiled)
        assert "555555" in str(compiled)
