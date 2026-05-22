from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import InputMediaPhoto, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.keyboards.inline import admin_review_keyboard
from app.keyboards.reply import (
    category_keyboard,
    confirm_keyboard,
    done_photos_keyboard,
    label_to_category,
    main_menu_keyboard,
    skip_keyboard,
)
from app.models.ad import CATEGORY_LABELS, Category
from app.services.ad_service import AdService
from app.services.user_service import UserService
from app.states.ad_states import AdCreation
from app.utils.formatting import format_ad_text

router = Router()

MAX_PHOTOS = 6


@router.message(F.text == "📝 E'lon berish")
async def start_ad_creation(
    message: Message, state: FSMContext, session: AsyncSession
) -> None:
    user_service = UserService(session)
    user = await user_service.get_or_none(message.from_user.id)
    if not user:
        await message.answer("Avval /start buyrug'ini yuboring va ro'yxatdan o'ting.")
        return

    await state.update_data(user_db_id=user.id, contact_phone=user.phone_number)
    await state.set_state(AdCreation.choosing_category)
    await message.answer("Kategoriyani tanlang:", reply_markup=category_keyboard())


@router.message(AdCreation.choosing_category, F.text == "❌ Bekor qilish")
@router.message(AdCreation.entering_title, F.text == "❌ Bekor qilish")
@router.message(AdCreation.entering_description, F.text == "❌ Bekor qilish")
@router.message(AdCreation.entering_price, F.text == "❌ Bekor qilish")
@router.message(AdCreation.uploading_photos, F.text == "❌ Bekor qilish")
@router.message(AdCreation.confirming, F.text == "❌ Bekor qilish")
async def cancel_ad(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("E'lon bekor qilindi.", reply_markup=main_menu_keyboard())


@router.message(AdCreation.choosing_category, F.text)
async def process_category(message: Message, state: FSMContext) -> None:
    category = label_to_category(message.text)
    if category is None:
        await message.answer(
            "Iltimos, quyidagi kategoriyalardan birini tanlang:",
            reply_markup=category_keyboard(),
        )
        return

    await state.update_data(category=category.value)
    await state.set_state(AdCreation.entering_title)
    await message.answer(
        f"Kategoriya: {CATEGORY_LABELS[category]}\n\nE'lon sarlavhasini kiriting:"
    )


@router.message(AdCreation.choosing_category)
async def invalid_category_input(message: Message) -> None:
    await message.answer(
        "Iltimos, kategoriyani quyidagi tugmalar orqali tanlang:",
        reply_markup=category_keyboard(),
    )


@router.message(AdCreation.entering_title)
async def process_title(message: Message, state: FSMContext) -> None:
    if not message.text or len(message.text) > 255:
        await message.answer("Sarlavha 1-255 belgi oralig'ida bo'lishi kerak.")
        return

    await state.update_data(title=message.text)
    await state.set_state(AdCreation.entering_description)
    await message.answer("E'lon tavsifini kiriting:")


@router.message(AdCreation.entering_description)
async def process_description(message: Message, state: FSMContext) -> None:
    if not message.text:
        await message.answer("Iltimos, matnli tavsif kiriting.")
        return

    await state.update_data(description=message.text)
    await state.set_state(AdCreation.entering_price)
    await message.answer(
        "Narxni kiriting (yoki o'tkazib yuboring):", reply_markup=skip_keyboard()
    )


@router.message(AdCreation.entering_price, F.text)
async def process_price(message: Message, state: FSMContext) -> None:
    price = None if message.text == "⏭ O'tkazib yuborish" else message.text
    await state.update_data(price=price, photo_file_ids=[])
    await state.set_state(AdCreation.uploading_photos)
    await message.answer(
        f"Rasmlarni yuboring (maksimal {MAX_PHOTOS} ta).\n"
        "Tayyor bo'lganda pastdagi tugmani bosing.",
        reply_markup=done_photos_keyboard(),
    )


@router.message(AdCreation.entering_price)
async def invalid_price_input(message: Message) -> None:
    await message.answer(
        "Iltimos, narxni matn orqali kiriting yoki o'tkazib yuboring.",
        reply_markup=skip_keyboard(),
    )


@router.message(AdCreation.uploading_photos, F.photo)
async def process_photo(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    photos: list[str] = data.get("photo_file_ids", [])

    if len(photos) >= MAX_PHOTOS:
        await message.answer(f"Maksimal {MAX_PHOTOS} ta rasm yuborilishi mumkin.")
        return

    file_id = message.photo[-1].file_id
    photos.append(file_id)
    await state.update_data(photo_file_ids=photos)

    remaining = MAX_PHOTOS - len(photos)
    if remaining > 0:
        await message.answer(
            f"Rasm qabul qilindi ✅ (yana {remaining} ta yuborishingiz mumkin).",
            reply_markup=done_photos_keyboard(),
        )
    else:
        await message.answer(
            f"Maksimal {MAX_PHOTOS} ta rasm qabul qilindi ✅",
            reply_markup=done_photos_keyboard(),
        )


@router.message(AdCreation.uploading_photos, F.text == "✅ Tayyor")
async def photos_done(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    photos = data.get("photo_file_ids", [])

    if not photos:
        await message.answer(
            "Kamida bitta rasm yuborishingiz kerak.",
            reply_markup=done_photos_keyboard(),
        )
        return

    preview = (
        f"<b>Kategoriya:</b> {CATEGORY_LABELS[Category(data['category'])]}\n"
        f"<b>Sarlavha:</b> {data['title']}\n"
        f"<b>Tavsif:</b> {data['description']}\n"
    )
    if data.get("price"):
        preview += f"<b>Narx:</b> {data['price']}\n"
    preview += f"<b>Aloqa:</b> {data['contact_phone']}\n"
    preview += f"<b>Rasmlar:</b> {len(photos)} ta\n"
    preview += "\nTasdiqlaysizmi?"

    await state.set_state(AdCreation.confirming)
    await message.answer(preview, parse_mode="HTML", reply_markup=confirm_keyboard())


@router.message(AdCreation.uploading_photos)
async def invalid_photo(message: Message) -> None:
    await message.answer(
        "Iltimos, rasm yuboring yoki '✅ Tayyor' tugmasini bosing.",
        reply_markup=done_photos_keyboard(),
    )


@router.message(AdCreation.confirming, F.text == "✅ Tasdiqlash")
async def confirm_ad(
    message: Message, state: FSMContext, session: AsyncSession, bot: Bot
) -> None:
    data = await state.get_data()

    ad_service = AdService(session)
    ad = await ad_service.create_ad(
        user_id=data["user_db_id"],
        category=Category(data["category"]),
        title=data["title"],
        description=data["description"],
        price=data.get("price"),
        contact_phone=data["contact_phone"],
        photo_file_ids=data.get("photo_file_ids") or None,
    )

    ad = await ad_service.get_ad(ad.id)
    ad_text = format_ad_text(ad)
    admin_text = f"📋 <b>Yangi e'lon #{ad.id}</b>\n\n{ad_text}"

    photos = data.get("photo_file_ids", [])
    if photos:
        media = [
            InputMediaPhoto(
                media=fid, caption=admin_text if i == 0 else None,
                parse_mode="HTML" if i == 0 else None,
            )
            for i, fid in enumerate(photos)
        ]
        sent = await bot.send_media_group(
            chat_id=settings.admin_channel_id, media=media
        )
        admin_msg = await bot.send_message(
            chat_id=settings.admin_channel_id,
            text=f"E'lon #{ad.id} uchun qaror:",
            reply_markup=admin_review_keyboard(ad.id),
        )
    else:
        admin_msg = await bot.send_message(
            chat_id=settings.admin_channel_id,
            text=admin_text,
            parse_mode="HTML",
            reply_markup=admin_review_keyboard(ad.id),
        )

    await ad_service.submit_for_review(ad.id, admin_msg.message_id)
    await state.clear()
    await message.answer(
        "E'loningiz adminlarga ko'rib chiqish uchun yuborildi ✅\n"
        "Natija haqida xabar beriladi.",
        reply_markup=main_menu_keyboard(),
    )
