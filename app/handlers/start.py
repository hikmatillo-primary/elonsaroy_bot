from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboards.reply import contact_keyboard, main_menu_keyboard
from app.services.user_service import UserService
from app.states.ad_states import Registration

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, session: AsyncSession) -> None:
    user_service = UserService(session)
    user = await user_service.get_or_none(message.from_user.id)

    if user:
        await message.answer(
            f"Assalomu alaykum, {user.full_name}! 👋\n"
            "E'lon berish uchun pastdagi tugmani bosing.",
            reply_markup=main_menu_keyboard(),
        )
        return

    await state.set_state(Registration.waiting_contact)
    await message.answer(
        "Assalomu alaykum! 👋\n"
        "E'lon berish uchun avval ro'yxatdan o'ting.\n"
        "Telefon raqamingizni yuboring:",
        reply_markup=contact_keyboard(),
    )


@router.message(Registration.waiting_contact, F.contact)
async def process_contact(
    message: Message, state: FSMContext, session: AsyncSession
) -> None:
    contact = message.contact
    if contact.user_id != message.from_user.id:
        await message.answer(
            "Iltimos, o'zingizning telefon raqamingizni yuboring.",
            reply_markup=contact_keyboard(),
        )
        return

    user_service = UserService(session)
    full_name = message.from_user.full_name or "Foydalanuvchi"
    await user_service.register(
        telegram_id=message.from_user.id,
        phone_number=contact.phone_number,
        full_name=full_name,
    )
    await state.clear()
    await message.answer(
        f"Ro'yxatdan o'tdingiz, {full_name}! ✅\n"
        "E'lon berish uchun pastdagi tugmani bosing.",
        reply_markup=main_menu_keyboard(),
    )


@router.message(Registration.waiting_contact)
async def invalid_contact(message: Message) -> None:
    await message.answer(
        "Iltimos, pastdagi tugmani bosib telefon raqamingizni yuboring.",
        reply_markup=contact_keyboard(),
    )
