from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from app.models.ad import CATEGORY_LABELS, Category


def contact_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📞 Telefon raqamni yuborish", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📝 E'lon berish")]],
        resize_keyboard=True,
    )


def category_keyboard() -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text=label)] for label in CATEGORY_LABELS.values()
    ]
    buttons.append([KeyboardButton(text="❌ Bekor qilish")])
    return ReplyKeyboardMarkup(
        keyboard=buttons, resize_keyboard=True, one_time_keyboard=True
    )


def skip_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="⏭ O'tkazib yuborish")]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def done_photos_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Tayyor")],
            [KeyboardButton(text="❌ Bekor qilish")],
        ],
        resize_keyboard=True,
    )


def confirm_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Tasdiqlash")],
            [KeyboardButton(text="❌ Bekor qilish")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def label_to_category(label: str) -> Category | None:
    for cat, cat_label in CATEGORY_LABELS.items():
        if cat_label == label:
            return cat
    return None
