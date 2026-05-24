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


def options_keyboard(
    options: list[tuple[str, str]], *, show_skip: bool = False, show_back: bool = False
) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for i in range(0, len(options), 2):
        row = [
            InlineKeyboardButton(text=label, callback_data=f"opt:{key}")
            for key, label in options[i : i + 2]
        ]
        rows.append(row)
    nav_buttons: list[InlineKeyboardButton] = []
    if show_back:
        nav_buttons.append(
            InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_question")
        )
    if show_skip:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⏭ O'tkazib yuborish", callback_data="skip_question"
            )
        )
    if nav_buttons:
        rows.append(nav_buttons)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def skip_inline_keyboard(show_back: bool = False) -> InlineKeyboardMarkup:
    buttons = []
    if show_back:
        buttons.append(
            InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_question")
        )
    buttons.append(
        InlineKeyboardButton(
            text="⏭ O'tkazib yuborish", callback_data="skip_question"
        )
    )
    return InlineKeyboardMarkup(inline_keyboard=[buttons])


def back_inline_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_question")]
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
