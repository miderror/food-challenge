import re

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from backend.users.models import User
from bot.handlers.menu import show_main_menu
from bot.keyboards.reply_keyboards import request_contact_kb
from bot.states.registration import Registration
from bot.utils.db import get_bot_texts, register_user

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext, user: User | None = None):
    await state.clear()
    texts = await get_bot_texts()
    if user:
        await show_main_menu(message, texts.welcome_message)
    else:
        await message.answer(
            texts.request_contact_message,
            reply_markup=request_contact_kb,
        )
        await state.set_state(Registration.waiting_for_contact)


@router.message(Registration.waiting_for_contact, F.contact)
async def contact_handler(
    message: Message, state: FSMContext, user: User | None = None
):
    if message.chat.id != message.contact.user_id:
        await message.answer("Пожалуйста, используйте кнопку для отправки своего контакта.")
        return

    texts = await get_bot_texts()

    if user:
        await show_main_menu(message, texts.already_authorized_message)
        return

    await state.update_data(
        phone_number="{0:+.0f}".format(int(message.contact.phone_number)),
        telegram_id=message.contact.user_id,
        username=message.from_user.username,
    )

    await message.answer("Контакт получен!", reply_markup=ReplyKeyboardRemove())

    texts = await get_bot_texts()
    await message.answer(texts.request_fio_message)
    await state.set_state(Registration.waiting_for_fio)


@router.message(Registration.waiting_for_fio, F.text)
async def fio_handler(message: Message, state: FSMContext):
    if len(message.text) > 100:
        await message.answer("Пожалуйста, введите более коротко.")
        return
    await state.update_data(full_name=message.text)

    texts = await get_bot_texts()
    await message.answer(texts.request_hw_message)
    await state.set_state(Registration.waiting_for_hw)


@router.message(Registration.waiting_for_hw, F.text)
async def hw_handler(message: Message, state: FSMContext):
    match = re.match(r"^(\d{2,3})\s+(\d{2,3})$", message.text.strip())
    if not match:
        await message.answer(
            "Неверный формат. Пожалуйста, введите рост (см) и вес (кг) целыми числами через пробел, например: 180 75"
        )
        return

    height = int(match.group(1))
    weight = int(match.group(2))

    user_data = await state.get_data()

    await register_user(
        telegram_id=user_data["telegram_id"],
        username=user_data["username"],
        phone_number_str=user_data["phone_number"],
        full_name=user_data["full_name"],
        height=height,
        weight=weight,
    )

    await state.clear()

    texts = await get_bot_texts()
    await message.answer(texts.registration_success_message)
    await show_main_menu(message, texts.main_menu_message)
