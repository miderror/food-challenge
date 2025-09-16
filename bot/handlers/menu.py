from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from bot.keyboards.inline_keyboards import get_main_menu_kb
from bot.utils.db import get_bot_texts

router = Router()


async def show_main_menu(message: Message, text: str):
    await message.answer(text, reply_markup=await get_main_menu_kb())


@router.callback_query(F.data == "back_to_main_menu")
async def back_to_main_menu_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass
    texts = await get_bot_texts()
    await show_main_menu(callback.message, texts.menu_return_message)
    await callback.answer()


@router.message(Command("search"))
async def search_command_handler(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔍 Начать поиск продукта",
                    switch_inline_query_current_chat="",
                )
            ]
        ]
    )
    await message.answer(
        "Нажмите кнопку ниже, чтобы начать поиск продукта прямо в этом чате.",
        reply_markup=keyboard,
    )
