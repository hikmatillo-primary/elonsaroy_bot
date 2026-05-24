import logging

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InputMediaPhoto, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.handlers.question_flow import (
    CATEGORY_QUESTIONS,
    build_description,
    get_price_from_answers,
    get_title_from_answers,
    validate_answer,
)
from app.keyboards.inline import (
    admin_review_keyboard,
    confirm_inline_keyboard,
    options_keyboard,
    skip_inline_keyboard,
    back_inline_keyboard,
)
from app.keyboards.reply import (
    cancel_keyboard,
    category_reply_keyboard,
    done_photos_keyboard,
    main_menu_keyboard,
)
from app.models.ad import AdStatus, CATEGORY_LABELS, Category
from app.services.ad_service import AdService
from app.services.user_service import UserService
from app.states.ad_states import AdCreation
from app.utils.formatting import format_ad_text

logger = logging.getLogger(__name__)

router = Router()

MAX_PHOTOS = 6


async def _send_next_question(target: Message, state: FSMContext) -> None:
    data = await state.get_data()
    category = Category(data["category"])
    questions = CATEGORY_QUESTIONS[category]
    q_index = data.get("q_index", 0)

    if q_index >= len(questions):
        await state.set_state(AdCreation.uploading_photos)
        await state.update_data(photo_file_ids=[])
        await target.answer(
            f"📸 Rasmlarni yuboring (maksimal {MAX_PHOTOS} ta).\n"
            "Tayyor bo'lganda pastdagi tugmani bosing.",
            reply_markup=done_photos_keyboard(),
        )
        return

    await state.set_state(AdCreation.answering_questions)
    question = questions[q_index]
    show_back = q_index > 0

    if question.options:
        await target.answer(
            question.prompt,
            reply_markup=options_keyboard(
                question.options, show_skip=question.optional, show_back=show_back
            ),
        )
    elif question.optional:
        await target.answer(
            question.prompt, reply_markup=skip_inline_keyboard(show_back=show_back)
        )
    else:
        if show_back:
            await target.answer(question.prompt, reply_markup=back_inline_keyboard())
        else:
            await target.answer(question.prompt)


# ── Start ad creation ──────────────────────────────────────────────────


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
    await message.answer(
        "⬇️ Kategoriyani tanlang:",
        reply_markup=category_reply_keyboard(),
    )


# ── Cancel (text button — works in any state) ─────────────────────────


@router.message(AdCreation.choosing_category, F.text == "❌ Bekor qilish")
@router.message(AdCreation.answering_questions, F.text == "❌ Bekor qilish")
@router.message(AdCreation.uploading_photos, F.text == "❌ Bekor qilish")
@router.message(AdCreation.confirming, F.text == "❌ Bekor qilish")
async def cancel_ad_text(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("E'lon bekor qilindi.", reply_markup=main_menu_keyboard())


# ── Cancel (inline callback) ──────────────────────────────────────────


@router.callback_query(AdCreation.choosing_category, F.data == "cancel_ad")
@router.callback_query(AdCreation.answering_questions, F.data == "cancel_ad")
@router.callback_query(AdCreation.uploading_photos, F.data == "cancel_ad")
@router.callback_query(AdCreation.confirming, F.data == "cancel_ad")
async def cancel_ad_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text("E'lon bekor qilindi.")
    await callback.message.answer(
        "Asosiy menyu:", reply_markup=main_menu_keyboard()
    )
    await callback.answer()


# ── Category selection (reply keyboard) ───────────────────────────────


@router.message(AdCreation.choosing_category, F.text.in_([label for label in CATEGORY_LABELS.values()]))
async def process_category_reply(message: Message, state: FSMContext) -> None:
    text = message.text
    category = None
    for cat, label in CATEGORY_LABELS.items():
        if label == text:
            category = cat
            break
    
    if not category:
        await message.answer(
            "Iltimos, kategoriyani quyidagi tugmalar orqali tanlang:",
            reply_markup=category_reply_keyboard(),
        )
        return

    await state.update_data(category=category.value, q_index=0, answers={})
    await _send_next_question(message, state)


# ── Dynamic question flow: text answer ────────────────────────────────


@router.message(AdCreation.answering_questions, F.text)
async def process_text_answer(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    category = Category(data["category"])
    questions = CATEGORY_QUESTIONS[category]
    q_index = data.get("q_index", 0)

    if q_index >= len(questions):
        return

    question = questions[q_index]

    if question.options:
        await message.answer(
            "Iltimos, yuqoridagi tugmalardan birini tanlang:",
            reply_markup=options_keyboard(
                question.options, show_skip=question.optional
            ),
        )
        return

    text = message.text.strip()

    if question.is_title and len(text) > 255:
        await message.answer("Sarlavha 255 belgidan oshmasligi kerak.")
        return

    error = validate_answer(question, text)
    if error:
        await message.answer(error)
        return

    answers: dict = data.get("answers", {})
    answers[question.key] = text
    await state.update_data(answers=answers, q_index=q_index + 1)
    await _send_next_question(message, state)


@router.message(AdCreation.answering_questions)
async def invalid_question_input(message: Message, state: FSMContext) -> None:
    await message.answer("Iltimos, matnli javob kiriting.")


# ── Dynamic question flow: option / skip callback ─────────────────────


@router.callback_query(AdCreation.answering_questions, F.data.startswith("opt:"))
async def process_option_answer(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    category = Category(data["category"])
    questions = CATEGORY_QUESTIONS[category]
    q_index = data.get("q_index", 0)

    if q_index >= len(questions):
        await callback.answer()
        return

    opt_key = callback.data.split(":", 1)[1]
    question = questions[q_index]
    label = opt_key
    if question.options:
        for k, lbl in question.options:
            if k == opt_key:
                label = lbl
                break

    answers: dict = data.get("answers", {})
    answers[question.key] = label
    await callback.message.edit_text(
        f"{question.prompt} {label}"
    )
    await state.update_data(answers=answers, q_index=q_index + 1)
    await _send_next_question(callback.message, state)
    await callback.answer()


@router.callback_query(AdCreation.answering_questions, F.data == "skip_question")
async def skip_question(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    category = Category(data["category"])
    questions = CATEGORY_QUESTIONS[category]
    q_index = data.get("q_index", 0)

    if q_index < len(questions) and not questions[q_index].optional:
        await callback.answer("Bu savolni o'tkazib bo'lmaydi.", show_alert=True)
        return

    await callback.message.edit_text("⏭ O'tkazib yuborildi")
    await state.update_data(q_index=q_index + 1)
    await _send_next_question(callback.message, state)
    await callback.answer()


@router.callback_query(AdCreation.answering_questions, F.data == "back_question")
async def back_question(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    q_index = data.get("q_index", 0)

    if q_index == 0:
        await callback.answer()
        return

    await callback.message.edit_text("⬅️ Orqaga qaytdingiz")
    await state.update_data(q_index=q_index - 1)
    await _send_next_question(callback.message, state)
    await callback.answer()


# ── Photo upload ───────────────────────────────────────────────────────


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

    category = Category(data["category"])
    answers: dict = data.get("answers", {})
    title = get_title_from_answers(category, answers)
    description = build_description(category, answers)
    price = get_price_from_answers(category, answers)

    preview = (
        f"<b>📋 E'lon ko'rinishi:</b>\n\n"
        f"<b>Kategoriya:</b> {CATEGORY_LABELS[category]}\n"
        f"<b>Sarlavha:</b> {title}\n"
        f"<b>Tavsif:</b>\n{description}\n"
    )
    if price:
        preview += f"<b>Narx:</b> {price}\n"
    preview += f"<b>Aloqa:</b> {data['contact_phone']}\n"
    preview += f"<b>Rasmlar:</b> {len(photos)} ta\n"

    await state.set_state(AdCreation.confirming)
    
    try:
        if len(photos) == 1:
            await message.answer_photo(
                photo=photos[0], caption=preview, parse_mode="HTML"
            )
        else:
            media = [
                InputMediaPhoto(
                    media=fid,
                    caption=preview if i == 0 else None,
                    parse_mode="HTML" if i == 0 else None,
                )
                for i, fid in enumerate(photos)
            ]
            await message.answer_media_group(media=media)
        await message.answer(
            "Yuqoridagi e'lonni tasdiqlaysizmi?",
            reply_markup=confirm_inline_keyboard(),
        )
    except TelegramAPIError as e:
        logger.error("Failed to send preview: %s", e)
        await message.answer(
            preview,
            parse_mode="HTML",
            reply_markup=confirm_inline_keyboard(),
        )


@router.message(AdCreation.uploading_photos)
async def invalid_photo(message: Message) -> None:
    await message.answer(
        "Iltimos, rasm yuboring yoki '✅ Tayyor' tugmasini bosing.",
        reply_markup=done_photos_keyboard(),
    )


# ── Confirmation (inline callback) ────────────────────────────────────


@router.callback_query(AdCreation.confirming, F.data == "confirm_ad")
async def confirm_ad(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession, bot: Bot
) -> None:
    data = await state.get_data()

    if data.get("submitting"):
        await callback.answer("E'lon allaqachon yuborilmoqda...", show_alert=True)
        return

    await state.update_data(submitting=True)

    category = Category(data["category"])
    answers: dict = data.get("answers", {})

    title = get_title_from_answers(category, answers)
    description = build_description(category, answers)
    price = get_price_from_answers(category, answers)

    ad_service = AdService(session)
    ad = await ad_service.create_ad(
        user_id=data["user_db_id"],
        category=category,
        title=title,
        description=description,
        price=price,
        contact_phone=data["contact_phone"],
        photo_file_ids=data.get("photo_file_ids") or None,
    )

    ad_text = format_ad_text(ad)
    admin_text = f"📋 <b>Yangi e'lon #{ad.id}</b>\n\n{ad_text}"

    photos = data.get("photo_file_ids", [])
    try:
        if len(photos) == 1:
            sent_photo = await bot.send_photo(
                chat_id=settings.admin_channel_id,
                photo=photos[0],
                caption=admin_text,
                parse_mode="HTML",
            )
            admin_msg = await bot.send_message(
                chat_id=settings.admin_channel_id,
                text=f"E'lon #{ad.id} uchun qaror:",
                reply_markup=admin_review_keyboard(ad.id),
                reply_to_message_id=sent_photo.message_id,
            )
        elif len(photos) > 1:
            media = [
                InputMediaPhoto(
                    media=fid,
                    caption=admin_text if i == 0 else None,
                    parse_mode="HTML" if i == 0 else None,
                )
                for i, fid in enumerate(photos)
            ]
            group_messages = await bot.send_media_group(
                chat_id=settings.admin_channel_id, media=media
            )
            admin_msg = await bot.send_message(
                chat_id=settings.admin_channel_id,
                text=f"E'lon #{ad.id} uchun qaror:",
                reply_markup=admin_review_keyboard(ad.id),
                reply_to_message_id=group_messages[0].message_id,
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
        await callback.message.edit_text("E'loningiz yuborildi ✅")
        await callback.message.answer(
            "E'loningiz adminlarga ko'rib chiqish uchun yuborildi ✅\n"
            "Natija haqida xabar beriladi.",
            reply_markup=main_menu_keyboard(),
        )
        await callback.answer()
    except TelegramAPIError as e:
        logger.error("Failed to send ad #%d to admin channel: %s", ad.id, e)
        await state.update_data(submitting=False)
        await callback.message.answer(
            "E'loningizni yuborishda xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.",
            reply_markup=main_menu_keyboard(),
        )
        await callback.answer("Xatolik yuz berdi", show_alert=True)


STATUS_LABELS = {
    AdStatus.DRAFT: "📝 Qoralama",
    AdStatus.PENDING: "🕐 Ko'rib chiqilmoqda",
    AdStatus.APPROVED: "✅ Tasdiqlangan",
    AdStatus.REJECTED: "❌ Rad etilgan",
}


# ── Edit ad (go back to questions) ────────────────────────────────────


@router.callback_query(AdCreation.confirming, F.data == "edit_ad")
async def edit_ad(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(submitting=False, q_index=0, photo_file_ids=[])
    await state.set_state(AdCreation.answering_questions)
    await callback.message.edit_text("E'lonni qayta to'ldiring:")
    await _send_next_question(callback.message, state)
    await callback.answer()


# ── My ads ──────────────────────────────────────────────────────────────


@router.message(F.text == "📋 E'lonlarim")
async def my_ads(
    message: Message, state: FSMContext, session: AsyncSession
) -> None:
    user_service = UserService(session)
    user = await user_service.get_or_none(message.from_user.id)
    if not user:
        await message.answer("Avval /start buyrug'ini yuboring va ro'yxatdan o'ting.")
        return

    ad_service = AdService(session)
    ads = await ad_service.get_user_ads(user.id)

    if not ads:
        await message.answer(
            "Sizda hali e'lonlar yo'q.\nE'lon berish uchun 📝 E'lon berish tugmasini bosing.",
            reply_markup=main_menu_keyboard(),
        )
        return

    lines = ["<b>📋 Mening e'lonlarim:</b>\n"]
    for ad in ads:
        status_label = STATUS_LABELS.get(ad.status, ad.status.value)
        lines.append(
            f"#{ad.id} — {CATEGORY_LABELS.get(ad.category, ad.category.value)} — {status_label}"
        )
    lines.append("\nE'lon berish uchun 📝 E'lon berish tugmasini bosing.")

    await message.answer(
        "\n".join(lines),
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(),
    )
