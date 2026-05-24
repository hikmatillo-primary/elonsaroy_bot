import logging

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.types import CallbackQuery, InputMediaPhoto
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.services.ad_service import AdService
from app.utils.formatting import format_ad_text

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data.startswith("approve:"))
async def approve_ad(
    callback: CallbackQuery, session: AsyncSession, bot: Bot
) -> None:
    if callback.from_user.id not in settings.admin_user_ids:
        await callback.answer("Sizda ruxsat yo'q.", show_alert=True)
        return

    ad_id = int(callback.data.split(":")[1])
    ad_service = AdService(session)
    ad = await ad_service.get_ad(ad_id)

    if ad is None:
        await callback.answer("E'lon topilmadi.", show_alert=True)
        return

    if ad.status.value != "pending":
        await callback.answer("Bu e'lon allaqachon ko'rib chiqilgan.", show_alert=True)
        return

    ad_text = format_ad_text(ad)
    channel_text = ad_text

    try:
        if len(ad.photo_file_ids) == 1:
            sent_photo = await bot.send_photo(
                chat_id=settings.main_channel_id,
                photo=ad.photo_file_ids[0],
                caption=channel_text,
                parse_mode="HTML",
            )
            main_msg_id = sent_photo.message_id
        elif len(ad.photo_file_ids) > 1:
            media = [
                InputMediaPhoto(
                    media=fid,
                    caption=channel_text if i == 0 else None,
                    parse_mode="HTML" if i == 0 else None,
                )
                for i, fid in enumerate(ad.photo_file_ids)
            ]
            sent = await bot.send_media_group(
                chat_id=settings.main_channel_id, media=media
            )
            main_msg_id = sent[0].message_id
        else:
            sent = await bot.send_message(
                chat_id=settings.main_channel_id,
                text=channel_text,
                parse_mode="HTML",
            )
            main_msg_id = sent.message_id

        await ad_service.approve(ad_id, main_msg_id)

        await callback.message.edit_text(
            f"✅ E'lon #{ad_id} tasdiqlandi va kanalga yuborildi.",
        )

        await bot.send_message(
            chat_id=ad.user.telegram_id,
            text=f"Sizning e'loningiz (#{ad_id}) tasdiqlandi va kanalga joylandi ✅",
        )

        await callback.answer("Tasdiqlandi ✅")
    except TelegramAPIError as e:
        logger.error("Failed to send approved ad #%d to main channel: %s", ad_id, e)
        await callback.answer(
            "E'lonni kanalga yuborishda xatolik. Iltimos, qaytadan urinib ko'ring.",
            show_alert=True,
        )


@router.callback_query(F.data.startswith("reject:"))
async def reject_ad(
    callback: CallbackQuery, session: AsyncSession, bot: Bot
) -> None:
    if callback.from_user.id not in settings.admin_user_ids:
        await callback.answer("Sizda ruxsat yo'q.", show_alert=True)
        return

    ad_id = int(callback.data.split(":")[1])
    ad_service = AdService(session)
    ad = await ad_service.get_ad(ad_id)

    if ad is None:
        await callback.answer("E'lon topilmadi.", show_alert=True)
        return

    if ad.status.value != "pending":
        await callback.answer("Bu e'lon allaqachon ko'rib chiqilgan.", show_alert=True)
        return

    await ad_service.reject(ad_id)

    await callback.message.edit_text(
        f"❌ E'lon #{ad_id} rad etildi.",
    )

    await bot.send_message(
        chat_id=ad.user.telegram_id,
        text=f"Afsuski, sizning e'loningiz (#{ad_id}) rad etildi ❌",
    )

    await callback.answer("Rad etildi ❌")
