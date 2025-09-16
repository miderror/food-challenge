from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.handlers.menu import show_main_menu
from bot.keyboards.callbacks import ProductCallback
from bot.keyboards.inline_keyboards import (
    get_back_to_menu_kb,
    get_product_categories_kb,
    get_product_confirmation_kb,
    get_products_kb,
)
from bot.states.user_actions import UserActions
from bot.utils.db import (
    add_eaten_product,
    create_product_suggestion,
    get_available_product_categories,
    get_bot_texts,
    get_product_by_id,
    get_uneaten_products_by_category,
)

router = Router()
PRODUCTS_PER_PAGE = 50


@router.callback_query(ProductCallback.filter(F.level == 0))
async def show_categories(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    categories = await get_available_product_categories(user_id=callback.from_user.id)

    await callback.message.edit_text(
        "Выберите категорию:",
        reply_markup=get_product_categories_kb(categories),
    )


@router.callback_query(ProductCallback.filter(F.level == 1))
async def show_products(callback: CallbackQuery, callback_data: ProductCallback):
    all_products = await get_uneaten_products_by_category(
        user_id=callback.from_user.id, category_id=callback_data.category_id
    )

    page = callback_data.page
    total_pages = (len(all_products) + PRODUCTS_PER_PAGE - 1) // PRODUCTS_PER_PAGE

    start_index = (page - 1) * PRODUCTS_PER_PAGE
    end_index = start_index + PRODUCTS_PER_PAGE
    products_on_page = all_products[start_index:end_index]

    try:
        await callback.message.edit_text(
            "Выберите продукт:",
            reply_markup=get_products_kb(
                products=products_on_page,
                category_id=callback_data.category_id,
                current_page=page,
                total_pages=total_pages,
            ),
        )
    except TelegramBadRequest:
        pass
    await callback.answer()


@router.callback_query(ProductCallback.filter(F.level == 2))
async def confirm_add_product(callback: CallbackQuery, callback_data: ProductCallback):
    product = await get_product_by_id(callback_data.product_id)
    if not product:
        await callback.answer("Продукт не найден.", show_alert=True)
        return

    await callback.message.edit_text(
        f"Вы уверены, что съели продукт '{product.name}'?",
        reply_markup=get_product_confirmation_kb(
            product_id=callback_data.product_id,
            category_id=callback_data.category_id,
            page=callback_data.page,
        ),
    )
    await callback.answer()


@router.callback_query(ProductCallback.filter((F.level == 3) & (F.action == "confirm")))
async def process_add_product(callback: CallbackQuery, callback_data: ProductCallback):
    success, product_name = await add_eaten_product(
        user_id=callback.from_user.id, product_id=callback_data.product_id
    )
    if success:
        await callback.answer(f"Продукт '{product_name}' добавлен!", show_alert=True)
    else:
        await callback.answer(
            "Произошла ошибка или продукт уже добавлен.", show_alert=True
        )

    await show_products(callback, callback_data)


@router.callback_query(F.data == "suggest_product")
async def suggest_product_start(callback: CallbackQuery, state: FSMContext):
    texts = await get_bot_texts()
    await callback.message.edit_text(
        texts.suggest_product_prompt, reply_markup=get_back_to_menu_kb()
    )
    await state.set_state(UserActions.suggesting_product)
    await callback.answer()


@router.message(UserActions.suggesting_product, F.text)
async def suggest_product_process(message: Message, state: FSMContext):
    if len(message.text) > 100:
        await message.answer("Пожалуйста, введите более коротко.")
        return
    await create_product_suggestion(
        user_id=message.from_user.id, product_name=message.text
    )
    await state.clear()
    texts = await get_bot_texts()
    await message.answer(texts.suggest_product_success)
    await show_main_menu(message, texts.main_menu_message)
