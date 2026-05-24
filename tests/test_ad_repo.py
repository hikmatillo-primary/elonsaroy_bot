import pytest

from app.models.ad import Ad, AdStatus, Category
from app.repositories.ad_repo import AdRepository


class TestAdRepository:
    @pytest.mark.asyncio
    async def test_create_ad_with_all_fields(self, ad_repo, mock_session):
        ad = await ad_repo.create(
            user_id=1,
            category=Category.AUTO,
            title="Test Car",
            description="A nice car",
            price="10000",
            contact_phone="+998901234567",
            photo_file_ids=["fid1", "fid2"],
        )

        mock_session.add.assert_called_once()
        added = mock_session.add.call_args[0][0]
        assert isinstance(added, Ad)
        assert added.user_id == 1
        assert added.category == Category.AUTO
        assert added.title == "Test Car"
        assert added.photo_file_ids == ["fid1", "fid2"]
        assert added.status == AdStatus.DRAFT

        mock_session.commit.assert_awaited_once()
        mock_session.refresh.assert_awaited_once_with(added)
        assert ad is not None

    @pytest.mark.asyncio
    async def test_create_ad_without_photos(self, ad_repo, mock_session):
        await ad_repo.create(
            user_id=2,
            category=Category.JOBS,
            title="Job Opening",
            description="We need a developer",
            price=None,
            contact_phone="+998901234567",
            photo_file_ids=None,
        )

        added = mock_session.add.call_args[0][0]
        assert added.photo_file_ids is None
        assert added.price is None

    @pytest.mark.asyncio
    async def test_get_by_id_returns_ad_with_user(self, ad_repo, mock_session, sample_ad):
        mock_session.execute.return_value.scalar_one_or_none.return_value = sample_ad

        ad = await ad_repo.get_by_id(1)

        assert ad is sample_ad
        assert ad.user is not None
        assert ad.user.telegram_id == 123456789
        mock_session.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_by_id_returns_none(self, ad_repo, mock_session):
        mock_session.execute.return_value.scalar_one_or_none.return_value = None

        ad = await ad_repo.get_by_id(999)

        assert ad is None

    @pytest.mark.asyncio
    async def test_update_status_to_approved(self, ad_repo, mock_session, sample_ad):
        mock_result = mock_session.execute.return_value
        mock_result.scalar_one_or_none.return_value = sample_ad

        updated = await ad_repo.update_status(
            1, AdStatus.APPROVED, main_channel_message_id=200
        )

        assert updated is sample_ad
        assert sample_ad.status == AdStatus.APPROVED
        assert sample_ad.main_channel_message_id == 200
        mock_session.commit.assert_awaited_once()
        mock_session.refresh.assert_awaited_once_with(sample_ad)

    @pytest.mark.asyncio
    async def test_update_status_to_rejected(self, ad_repo, mock_session, sample_ad):
        sample_ad.status = AdStatus.PENDING
        mock_result = mock_session.execute.return_value
        mock_result.scalar_one_or_none.return_value = sample_ad

        updated = await ad_repo.update_status(1, AdStatus.REJECTED)

        assert updated is sample_ad
        assert sample_ad.status == AdStatus.REJECTED
        assert sample_ad.main_channel_message_id is None

    @pytest.mark.asyncio
    async def test_update_status_returns_none_when_not_found(self, ad_repo, mock_session):
        mock_result = mock_session.execute.return_value
        mock_result.scalar_one_or_none.return_value = None

        updated = await ad_repo.update_status(999, AdStatus.APPROVED)

        assert updated is None
        mock_session.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_ad_all_categories(self, ad_repo, mock_session):
        for cat in Category:
            await ad_repo.create(
                user_id=1,
                category=cat,
                title=f"Test {cat.value}",
                description="Description",
                price="100",
                contact_phone="+998901234567",
            )
            added = mock_session.add.call_args[0][0]
            assert added.category == cat

    @pytest.mark.asyncio
    async def test_get_by_user_id_returns_ads(self, ad_repo, mock_session, sample_ad):
        mock_result = mock_session.execute.return_value
        mock_result.scalars.return_value.all.return_value = [sample_ad]

        ads = await ad_repo.get_by_user_id(1)

        assert len(ads) == 1
        assert ads[0] is sample_ad

    @pytest.mark.asyncio
    async def test_get_by_user_id_returns_empty_list(self, ad_repo, mock_session):
        mock_result = mock_session.execute.return_value
        mock_result.scalars.return_value.all.return_value = []

        ads = await ad_repo.get_by_user_id(999)

        assert ads == []
