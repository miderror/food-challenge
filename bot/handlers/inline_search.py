import html
import logging
import uuid

from aiogram import Bot, F, Router
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import (
    CallbackQuery,
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from django.conf import settings

from backend.products.models import Product
from bot.keyboards.callbacks import InlineProductCallback
from bot.keyboards.inline_keyboards import get_back_to_menu_kb
from bot.utils.db import (
    add_eaten_product,
    get_product_by_id,
    search_uneaten_products,
)

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
        safe_name_for_input = html.escape(product.name)
        input_content = InputTextMessageContent(
            message_text=f"Выбран продукт: <b>{safe_name_for_input}</b>",
            parse_mode=ParseMode.HTML,
        )

        article_args = {
            "id": str(uuid.uuid4()),
            "title": product.name,
            "description": product.fact if product.fact else "Нажмите, чтобы добавить.",
            "reply_markup": keyboard,
            "input_message_content": input_content,
        }

        if product.icon_photo and product.icon_photo.url:
            thumb_url = f"{settings.CSRF_TRUSTED_ORIGINS[0]}{product.icon_photo.url}"
            article_args["thumbnail_url"] = thumb_url
            article_args["thumbnail_width"] = 48
            article_args["thumbnail_height"] = 48

        results.append(InlineQueryResultArticle(**article_args))

    await inline_query.answer(results, cache_time=5, is_personal=True)


async def send_fact_as_new_message(bot: Bot, chat_id: int, product: Product):
    safe_name = html.escape(product.name)
    safe_fact = html.escape(product.fact or "") if product.fact else ""
    text = f"<b>{safe_name}</b>\n\n{safe_fact}"
    keboard = get_back_to_menu_kb()

    try:
        if product.main_photo:
            photo = FSInputFile(product.main_photo.path)
            await bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=text,
                parse_mode=ParseMode.HTML,
                reply_markup=keboard,
            )
        else:
            await bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=keboard,
            )

    except (FileNotFoundError, TelegramBadRequest) as e:
        logging.error(f"Не удалось отправить факт/фото для продукта {product.id}: {e}")


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

    if not success:
        await bot.edit_message_text(
            text="❌ Произошла ошибка. Возможно, продукт уже был добавлен ранее.",
            inline_message_id=callback.inline_message_id,
            reply_markup=None,
        )
        await callback.answer("Ошибка", show_alert=True)
        return

    product = await get_product_by_id(callback_data.product_id)
    safe_name = html.escape(product.name if product else product_name)
    final_text = f"✅ Продукт '<b>{safe_name}</b>' успешно добавлен в ваш список!"

    await bot.edit_message_text(
        text=final_text,
        inline_message_id=callback.inline_message_id,
        parse_mode=ParseMode.HTML,
        reply_markup=None,
    )

    await callback.answer(f"Добавлено: {product_name}", show_alert=True)

    if product and (product.fact or product.main_photo):
        await send_fact_as_new_message(bot, callback.from_user.id, product)
