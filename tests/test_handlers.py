from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.types import Message

from app.handlers.admin import approve_ad, reject_ad
from app.handlers.start import cmd_start, process_contact
from app.models.ad import AdStatus
from app.states.ad_states import Registration


class TestStartHandler:
    @pytest.mark.asyncio
    async def test_cmd_start_new_user_starts_registration(self, mock_session, mock_state):
        message = AsyncMock(spec=Message)
        message.from_user = MagicMock()
        message.from_user.id = 12345
        message.from_user.full_name = "New User"
        message.answer = AsyncMock()

        mock_session.execute.return_value.scalar_one_or_none.return_value = None

        await cmd_start(message, mock_state, mock_session)

        mock_state.set_state.assert_awaited_once_with(Registration.waiting_contact)
        message.answer.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_cmd_start_existing_user_shows_menu(self, mock_session, mock_state, sample_user):
        message = AsyncMock(spec=Message)
        message.from_user = MagicMock()
        message.from_user.id = sample_user.telegram_id
        message.from_user.full_name = sample_user.full_name
        message.answer = AsyncMock()

        mock_session.execute.return_value.scalar_one_or_none.return_value = sample_user

        await cmd_start(message, mock_state, mock_session)

        mock_state.set_state.assert_not_called()
        message.answer.assert_awaited_once()
        assert sample_user.full_name in message.answer.call_args[0][0]

    @pytest.mark.asyncio
    async def test_process_contact_registers_user(self, mock_session, mock_state):
        message = AsyncMock(spec=Message)
        message.from_user = MagicMock()
        message.from_user.id = 12345
        message.from_user.full_name = "Test User"
        message.contact = MagicMock()
        message.contact.user_id = 12345
        message.contact.phone_number = "+998901234567"
        message.answer = AsyncMock()

        mock_session.execute.return_value.scalar_one_or_none.return_value = None

        await process_contact(message, mock_state, mock_session)

        mock_state.clear.assert_awaited_once()
        message.answer.assert_awaited_once()
        mock_session.add.assert_called_once()
        mock_session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_process_contact_wrong_user_rejected(self, mock_session, mock_state):
        message = AsyncMock(spec=Message)
        message.from_user = MagicMock()
        message.from_user.id = 12345
        message.contact = MagicMock()
        message.contact.user_id = 99999
        message.answer = AsyncMock()

        await process_contact(message, mock_state, mock_session)

        mock_state.clear.assert_not_called()
        mock_session.add.assert_not_called()


class TestAdminHandler:
    @pytest.mark.asyncio
    async def test_approve_ad_by_admin(self, mock_session, mock_bot, sample_ad):
        callback = AsyncMock()
        callback.from_user = MagicMock()
        callback.from_user.id = 1
        callback.data = "approve:1"
        callback.message = AsyncMock()
        callback.message.edit_text = AsyncMock()
        callback.answer = AsyncMock()

        sample_ad.status = AdStatus.PENDING
        mock_session.execute.return_value.scalar_one_or_none.return_value = sample_ad

        sent_message = MagicMock()
        sent_message.message_id = 200
        mock_bot.send_message.return_value = sent_message
        mock_bot.send_media_group.return_value = [sent_message]

        with patch("app.handlers.admin.settings") as mock_settings:
            mock_settings.admin_user_ids = [1]
            mock_settings.main_channel_id = -100123

            await approve_ad(callback, mock_session, mock_bot)

        callback.answer.assert_awaited_once()
        assert "Tasdiqlandi" in callback.answer.call_args[0][0]

    @pytest.mark.asyncio
    async def test_approve_ad_by_non_admin_rejected(self, mock_session, mock_bot):
        callback = AsyncMock()
        callback.from_user = MagicMock()
        callback.from_user.id = 999
        callback.data = "approve:1"
        callback.answer = AsyncMock()

        with patch("app.handlers.admin.settings") as mock_settings:
            mock_settings.admin_user_ids = [1]

            await approve_ad(callback, mock_session, mock_bot)

        callback.answer.assert_awaited_once_with("Sizda ruxsat yo'q.", show_alert=True)
        mock_bot.send_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_reject_ad_by_admin(self, mock_session, mock_bot, sample_ad):
        callback = AsyncMock()
        callback.from_user = MagicMock()
        callback.from_user.id = 1
        callback.data = "reject:1"
        callback.message = AsyncMock()
        callback.message.edit_text = AsyncMock()
        callback.answer = AsyncMock()

        sample_ad.status = AdStatus.PENDING
        mock_session.execute.return_value.scalar_one_or_none.return_value = sample_ad

        with patch("app.handlers.admin.settings") as mock_settings:
            mock_settings.admin_user_ids = [1]

            await reject_ad(callback, mock_session, mock_bot)

        callback.answer.assert_awaited_once()
        assert "Rad etildi" in callback.answer.call_args[0][0]

    @pytest.mark.asyncio
    async def test_approve_ad_not_found(self, mock_session, mock_bot):
        callback = AsyncMock()
        callback.from_user = MagicMock()
        callback.from_user.id = 1
        callback.data = "approve:999"
        callback.answer = AsyncMock()

        mock_session.execute.return_value.scalar_one_or_none.return_value = None

        with patch("app.handlers.admin.settings") as mock_settings:
            mock_settings.admin_user_ids = [1]

            await approve_ad(callback, mock_session, mock_bot)

        callback.answer.assert_awaited_once_with("E'lon topilmadi.", show_alert=True)

    @pytest.mark.asyncio
    async def test_approve_ad_already_processed(self, mock_session, mock_bot, sample_ad):
        callback = AsyncMock()
        callback.from_user = MagicMock()
        callback.from_user.id = 1
        callback.data = "approve:1"
        callback.answer = AsyncMock()

        sample_ad.status = AdStatus.APPROVED
        mock_session.execute.return_value.scalar_one_or_none.return_value = sample_ad

        with patch("app.handlers.admin.settings") as mock_settings:
            mock_settings.admin_user_ids = [1]

            await approve_ad(callback, mock_session, mock_bot)

        callback.answer.assert_awaited_once_with(
            "Bu e'lon allaqachon ko'rib chiqilgan.", show_alert=True
        )
