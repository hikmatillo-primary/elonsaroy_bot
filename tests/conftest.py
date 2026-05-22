import os

os.environ.setdefault("BOT_TOKEN", "test:token")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test")
os.environ.setdefault("ADMIN_CHANNEL_ID", "-100123")
os.environ.setdefault("MAIN_CHANNEL_ID", "-100456")

from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ad import Ad, AdStatus, Category
from app.models.user import User
from app.repositories.ad_repo import AdRepository
from app.repositories.user_repo import UserRepository
from app.services.ad_service import AdService
from app.services.user_service import UserService


@pytest.fixture
def mock_session():
    session = AsyncMock(spec=AsyncSession)
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()

    mock_exec_result = MagicMock()
    mock_exec_result.scalar_one_or_none = MagicMock(return_value=None)
    session.execute = AsyncMock(return_value=mock_exec_result)

    return session


@pytest.fixture
def user_repo(mock_session):
    return UserRepository(mock_session)


@pytest.fixture
def ad_repo(mock_session):
    return AdRepository(mock_session)


@pytest.fixture
def user_service(mock_session):
    return UserService(mock_session)


@pytest.fixture
def ad_service(mock_session):
    return AdService(mock_session)


@pytest.fixture
def sample_user():
    user = User(
        id=1,
        telegram_id=123456789,
        phone_number="+998901234567",
        full_name="Test User",
    )
    return user


@pytest.fixture
def sample_ad(sample_user):
    ad = Ad(
        id=1,
        user_id=1,
        user=sample_user,
        category=Category.AUTO,
        title="Test Car",
        description="A nice car for sale",
        price="10000",
        contact_phone="+998901234567",
        photo_file_ids=["file_id_1", "file_id_2"],
        status=AdStatus.PENDING,
        admin_message_id=100,
        main_channel_message_id=None,
    )
    return ad


@pytest.fixture
def mock_bot():
    bot = AsyncMock()
    bot.send_message = AsyncMock()
    bot.send_media_group = AsyncMock()
    bot.session = AsyncMock()
    bot.session.close = AsyncMock()
    return bot


@pytest.fixture
def mock_state():
    state = AsyncMock()
    state.set_state = AsyncMock()
    state.update_data = AsyncMock()
    state.get_data = AsyncMock(return_value={})
    state.clear = AsyncMock()
    return state
