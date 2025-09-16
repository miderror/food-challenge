import uuid

from aiogram import Bot, F, Router
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
)

from aiogram.enums import ParseMode
from bot.keyboards.callbacks import InlineProductCallback
from bot.utils.db import add_eaten_product, search_uneaten_products

router = Router()


@router.inline_query()
async def inline_search_handler(inline_query: InlineQuery):
    query = inline_query.query.strip()
    user_id = inline_query.from_user.id

    if len(query) < 2:
        return

    products = await search_uneaten_products(user_id, query)

    results = []
    for product in products:
        confirm_button = InlineKeyboardButton(
            text="✅ Подтвердить",
            callback_data=InlineProductCallback(
                action="confirm", product_id=product.id
            ).pack(),
        )
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[confirm_button]])

        input_content = InputTextMessageContent(
            message_text=f"Вы собираетесь добавить продукт: <b>{product.name}</b>",
            parse_mode=ParseMode.HTML
        )

        results.append(
            InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title=product.name,
                description=f"Категория: {product.category.name}",
                input_message_content=input_content,
                reply_markup=keyboard,
            )
        )

    await inline_query.answer(results, cache_time=5, is_personal=True)


@router.callback_query(InlineProductCallback.filter(F.action == "confirm"))
async def confirm_inline_product_handler(
    callback: CallbackQuery, callback_data: InlineProductCallback, bot: Bot
):
    if not callback.inline_message_id:
        await callback.answer("Не удалось обработать это действие.", show_alert=True)
        return

    success, product_name = await add_eaten_product(
        user_id=callback.from_user.id, product_id=callback_data.product_id
    )

    if success:
        await bot.edit_message_text(
            text=f"✅ Продукт '<b>{product_name}</b>' успешно добавлен в ваш список!",
            inline_message_id=callback.inline_message_id,
            parse_mode=ParseMode.HTML,
            reply_markup=None,
        )
        await callback.answer(f"Добавлено: {product_name}", show_alert=True)
    else:
        await bot.edit_message_text(
            text="❌ Произошла ошибка. Возможно, продукт уже был добавлен ранее.",
            inline_message_id=callback.inline_message_id,
            reply_markup=None,
        )
        await callback.answer("Ошибка", show_alert=True)
