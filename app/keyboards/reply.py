from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from app.models.ad import CATEGORY_LABELS


def category_reply_keyboard() -> ReplyKeyboardMarkup:
    items = list(CATEGORY_LABELS.items())
    rows: list[list[KeyboardButton]] = []
    for i in range(0, len(items), 2):
        row = [
            KeyboardButton(text=label)
            for cat, label in items[i : i + 2]
        ]
        rows.append(row)
    rows.append([KeyboardButton(text="❌ Bekor qilish")])
    return ReplyKeyboardMarkup(
        keyboard=rows,
        resize_keyboard=True,
    )


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
        keyboard=[
            [KeyboardButton(text="📝 E'lon berish"), KeyboardButton(text="📋 E'lonlarim")],
        ],
        resize_keyboard=True,
    )


def cancel_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Bekor qilish")]],
        resize_keyboard=True,
    )


def done_photos_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Tayyor")],
            [KeyboardButton(text="❌ Bekor qilish")],
        ],
        resize_keyboard=True,
    )
