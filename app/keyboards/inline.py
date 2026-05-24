from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.models.ad import CATEGORY_LABELS


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


def category_inline_keyboard() -> InlineKeyboardMarkup:
    items = list(CATEGORY_LABELS.items())
    rows: list[list[InlineKeyboardButton]] = []
    for i in range(0, len(items), 2):
        row = [
            InlineKeyboardButton(text=label, callback_data=f"cat:{cat.value}")
            for cat, label in items[i : i + 2]
        ]
        rows.append(row)
    rows.append(
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_ad")]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def options_keyboard(
    options: list[tuple[str, str]], *, show_skip: bool = False
) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for i in range(0, len(options), 2):
        row = [
            InlineKeyboardButton(text=label, callback_data=f"opt:{key}")
            for key, label in options[i : i + 2]
        ]
        rows.append(row)
    if show_skip:
        rows.append(
            [
                InlineKeyboardButton(
                    text="⏭ O'tkazib yuborish", callback_data="skip_question"
                )
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def skip_inline_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⏭ O'tkazib yuborish", callback_data="skip_question"
                )
            ]
        ]
    )


def confirm_inline_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✏️ Tahrirlash", callback_data="edit_ad"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="✅ Tasdiqlash", callback_data="confirm_ad"
                ),
                InlineKeyboardButton(
                    text="❌ Bekor qilish", callback_data="cancel_ad"
                ),
            ],
        ]
    )
