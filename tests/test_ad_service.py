from unittest.mock import AsyncMock

import pytest

from app.models.ad import AdStatus, Category
from app.services.ad_service import AdService


class TestAdService:
    @pytest.mark.asyncio
    async def test_create_ad_delegates_to_repo(self, ad_service):
        ad_service.repo.create = AsyncMock(return_value="ad_object")

        result = await ad_service.create_ad(
            user_id=1,
            category=Category.AUTO,
            title="Test",
            description="Desc",
            price="100",
            contact_phone="+998901234567",
            photo_file_ids=["fid1"],
        )

        ad_service.repo.create.assert_awaited_once_with(
            user_id=1,
            category=Category.AUTO,
            title="Test",
            description="Desc",
            price="100",
            contact_phone="+998901234567",
            photo_file_ids=["fid1"],
        )
        assert result == "ad_object"

    @pytest.mark.asyncio
    async def test_submit_for_review_sets_pending(self, ad_service):
        ad_service.repo.update_status = AsyncMock(return_value="updated")

        result = await ad_service.submit_for_review(1, admin_message_id=500)

        ad_service.repo.update_status.assert_awaited_once_with(
            1, AdStatus.PENDING, admin_message_id=500
        )
        assert result == "updated"

    @pytest.mark.asyncio
    async def test_approve_sets_approved_with_main_channel_id(self, ad_service):
        ad_service.repo.update_status = AsyncMock(return_value="approved_ad")

        result = await ad_service.approve(1, main_message_id=999)

        ad_service.repo.update_status.assert_awaited_once_with(
            1, AdStatus.APPROVED, main_channel_message_id=999
        )
        assert result == "approved_ad"

    @pytest.mark.asyncio
    async def test_reject_sets_rejected(self, ad_service):
        ad_service.repo.update_status = AsyncMock(return_value="rejected_ad")

        result = await ad_service.reject(1)

        ad_service.repo.update_status.assert_awaited_once_with(1, AdStatus.REJECTED)
        assert result == "rejected_ad"

    @pytest.mark.asyncio
    async def test_get_ad_delegates_to_repo(self, ad_service):
        ad_service.repo.get_by_id = AsyncMock(return_value="ad_object")

        result = await ad_service.get_ad(1)

        ad_service.repo.get_by_id.assert_awaited_once_with(1)
        assert result == "ad_object"

    @pytest.mark.asyncio
    async def test_get_ad_returns_none_when_not_found(self, ad_service):
        ad_service.repo.get_by_id = AsyncMock(return_value=None)

        result = await ad_service.get_ad(999)

        assert result is None

    @pytest.mark.asyncio
    async def test_approval_flow_end_to_end(self, ad_service, sample_ad):
        ad_service.repo.get_by_id = AsyncMock(return_value=sample_ad)
        ad_service.repo.update_status = AsyncMock()

        await ad_service.submit_for_review(sample_ad.id, admin_message_id=100)
        ad_service.repo.update_status.assert_called_with(
            sample_ad.id, AdStatus.PENDING, admin_message_id=100
        )

        await ad_service.approve(sample_ad.id, main_message_id=200)
        ad_service.repo.update_status.assert_called_with(
            sample_ad.id, AdStatus.APPROVED, main_channel_message_id=200
        )

    @pytest.mark.asyncio
    async def test_get_user_ads_delegates_to_repo(self, ad_service):
        ad_service.repo.get_by_user_id = AsyncMock(return_value=["ad1", "ad2"])

        result = await ad_service.get_user_ads(1)

        ad_service.repo.get_by_user_id.assert_awaited_once_with(1)
        assert result == ["ad1", "ad2"]

    @pytest.mark.asyncio
    async def test_get_user_ads_returns_empty_list(self, ad_service):
        ad_service.repo.get_by_user_id = AsyncMock(return_value=[])

        result = await ad_service.get_user_ads(999)

        assert result == []
