import io

from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.types import BufferedInputFile, CallbackQuery

from bot.keyboards.inline_keyboards import get_profile_kb
from bot.utils.db import get_user_profile_info

router = Router()

PRODUCTS_DISPLAY_LIMIT = 35


@router.callback_query(F.data == "my_profile")
async def my_profile_handler(callback: CallbackQuery):
    profile_data = await get_user_profile_info(callback.from_user.id)
    if not profile_data:
        await callback.answer("Не удалось загрузить профиль.", show_alert=True)
        return

    days = profile_data["days"]
    eaten_count = profile_data["eaten_count"]
    eaten_list = profile_data["eaten_list"]

    if not eaten_list:
        eaten_list_str = "Вы еще не добавили ни одного продукта."
        keyboard = get_profile_kb(show_export_button=False)
    elif eaten_count > PRODUCTS_DISPLAY_LIMIT:
        display_list = eaten_list[:PRODUCTS_DISPLAY_LIMIT]
        eaten_list_str = "\n".join([f"• {name}" for name in display_list])

        remaining_count = eaten_count - PRODUCTS_DISPLAY_LIMIT
        eaten_list_str += f"\n\n<b>...еще {remaining_count} продуктов.</b>"

        keyboard = get_profile_kb(show_export_button=True)
    else:
        eaten_list_str = "\n".join([f"• {name}" for name in eaten_list])
        keyboard = get_profile_kb(show_export_button=False)

    text = (
        f"<b>👤 Ваш профиль</b>\n\n"
        f"<b>Прогресс:</b> {eaten_count} из 400 продуктов.\n"
        f"<b>Дней в челлендже:</b> {days} из 365.\n\n"
        f"<b>Съеденные продукты:</b>\n{eaten_list_str}"
    )

    await callback.message.edit_text(
        text, reply_markup=keyboard, parse_mode=ParseMode.HTML
    )
    await callback.answer()


@router.callback_query(F.data == "export_products")
async def export_products_handler(callback: CallbackQuery):
    await callback.answer("Готовлю файл...", show_alert=False)

    profile_data = await get_user_profile_info(callback.from_user.id)
    if not profile_data or not profile_data["eaten_list"]:
        await callback.message.answer(
            "Не удалось получить список продуктов для выгрузки."
        )
        return

    header = f"Ваш список съеденных продуктов ({profile_data['eaten_count']} шт.):\n\n"
    file_content = header + "\n".join(profile_data["eaten_list"])

    file_io = io.BytesIO(file_content.encode("utf-8"))

    input_file = BufferedInputFile(
        file=file_io.getvalue(), filename=f"eaten_products_{callback.from_user.id}.txt"
    )

    await callback.message.answer_document(input_file)
