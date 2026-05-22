from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def admin_review_keyboard(ad_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Tasdiqlash", callback_data=f"approve:{ad_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Rad etish", callback_data=f"reject:{ad_id}"
                ),
            ]
        ]
    )
