import logging

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, FSInputFile

from backend.content.models import MediaType
from bot.keyboards.inline_keyboards import FaqCallback, get_faq_list_kb
from bot.utils.db import get_bot_texts, get_faq_item, get_faq_list

router = Router()


@router.callback_query(F.data == "show_faq_list")
async def show_faq_list_handler(callback: CallbackQuery):
    faq_list = await get_faq_list()
    if not faq_list:
        await callback.answer("Раздел FAQ пока пуст.", show_alert=True)
        return

    texts = await get_bot_texts()

    await callback.message.edit_text(
        texts.faq_list_title, reply_markup=get_faq_list_kb(faq_list)
    )
    await callback.answer()


@router.callback_query(FaqCallback.filter())
async def show_faq_answer_handler(callback: CallbackQuery, callback_data: FaqCallback):
    faq_item = await get_faq_item(callback_data.id)
    if not faq_item:
        await callback.answer(
            "Извините, этот вопрос больше не актуален.", show_alert=True
        )
        return

    full_text = f"*{faq_item.question}*\n\n{faq_item.answer}"

    try:
        if faq_item.media_file and faq_item.media_type:
            file = FSInputFile(faq_item.media_file.path)

            sender_map = {
                MediaType.PHOTO: callback.message.answer_photo,
                MediaType.VIDEO: callback.message.answer_video,
                MediaType.DOCUMENT: callback.message.answer_document,
                MediaType.AUDIO: callback.message.answer_audio,
            }
            sender = sender_map.get(faq_item.media_type)
            if sender:
                await sender(file, caption=full_text)
        else:
            await callback.message.answer(full_text)
    except TelegramBadRequest as e:
        logging.error(f"Error FAQ ID {faq_item.id}: {e}")
        await callback.message.answer(
            "⚠️ [Системное сообщение]\nПроизошла ошибка при отправке ответа. (FAQ ID: {faq_item.id})."
        )
    except FileNotFoundError:
        raw_text = f"*{faq_item.question}*\n\n{faq_item.answer}"
        await callback.message.answer(
            f"{raw_text}\n\n(Не удалось загрузить прикрепленный файл)",
        )
    finally:
        await callback.answer()
