import logging

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.utils.media_group import MediaGroupBuilder

from backend.content.models import MediaType
from bot.keyboards.inline_keyboards import get_back_to_menu_kb
from bot.utils.db import get_about_project_content

router = Router()


@router.callback_query(F.data == "about_project")
async def about_project_handler(callback: CallbackQuery):
    data = await get_about_project_content()
    content = data["content"]
    media_items = data["media_items"]

    keyboard = get_back_to_menu_kb()

    if not content or not content.text:
        await callback.answer(
            "Информация о проекте в данный момент не заполнена.", show_alert=True
        )
        return

    try:
        if content.media_type:
            try:
                await callback.message.delete()
            except TelegramBadRequest:
                pass

        if content.media_type == MediaType.MEDIA_GROUP:
            valid_media_files = []
            for item in media_items:
                try:
                    file = FSInputFile(item.image.path)
                    valid_media_files.append(file)
                except FileNotFoundError:
                    logging.error(f"Файл для медиагруппы не найден: {item.image.path}")

            if len(valid_media_files) >= 2:
                media_group_builder = MediaGroupBuilder()
                for file in valid_media_files[:10]:
                    media_group_builder.add_photo(media=file)

                await callback.message.answer_media_group(
                    media=media_group_builder.build()
                )
                await callback.message.answer(content.text, reply_markup=keyboard)
                return

            elif len(valid_media_files) == 1:
                await callback.message.answer_photo(
                    valid_media_files[0], caption=content.text, reply_markup=keyboard
                )
            else:
                await callback.message.answer(content.text, reply_markup=keyboard)

        elif content.media_file and content.media_type:
            file = FSInputFile(content.media_file.path)

            sender_map = {
                MediaType.PHOTO: callback.message.answer_photo,
                MediaType.VIDEO: callback.message.answer_video,
                MediaType.DOCUMENT: callback.message.answer_document,
                MediaType.AUDIO: callback.message.answer_audio,
            }
            sender = sender_map.get(content.media_type)

            if sender:
                await sender(file, caption=content.text, reply_markup=keyboard)
            else:
                logging.warning(
                    f"Неизвестный тип медиа {content.media_type} для 'О проекте'"
                )
                await callback.message.answer(content.text, reply_markup=keyboard)
        else:
            await callback.message.edit_text(content.text, reply_markup=keyboard)

    except FileNotFoundError:
        logging.error(f"Файл не найден для 'О проекте': {content.media_file.path}")
        await callback.message.answer(
            f"{content.text}\n\n(Ошибка: не удалось загрузить прикрепленный файл)"
        )
    except TelegramBadRequest as e:
        logging.error(f"Ошибка форматирования в 'О проекте': {e}")
        await callback.message.answer(
            "Произошла ошибка при отображении информации. Попробуйте позже."
        )
    finally:
        await callback.answer()
