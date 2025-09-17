from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.utils.db import get_community_link

from .callbacks import FaqCallback, ProductCallback


async def get_main_menu_kb() -> InlineKeyboardMarkup:
    community_link = await get_community_link()
    buttons = [
        [InlineKeyboardButton(text="👤 Мой профиль", callback_data="my_profile")],
        [
            InlineKeyboardButton(
                text="✅ Добавить продукт",
                callback_data=ProductCallback(level=0).pack(),
            )
        ],
        [InlineKeyboardButton(text="ℹ️ О проекте", callback_data="about_project")],
        [InlineKeyboardButton(text="❓ FAQ", callback_data="show_faq_list")],
        [InlineKeyboardButton(text="👥 Группа единомышленников", url=community_link)],
        [
            InlineKeyboardButton(
                text="💡 Предложить продукт", callback_data="suggest_product"
            )
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_product_categories_kb(
    categories: list[tuple[int, str]],
) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=name,
                callback_data=ProductCallback(level=1, category_id=cat_id).pack(),
            )
        ]
        for cat_id, name in categories
    ]
    buttons.append(
        [
            InlineKeyboardButton(
                text="⬅️ В главное меню", callback_data="back_to_main_menu"
            )
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_products_kb(
    products: list[tuple[int, str]],
    category_id: int,
    current_page: int,
    total_pages: int,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for prod_id, name in products:
        builder.button(
            text=name,
            callback_data=ProductCallback(
                level=2, category_id=category_id, product_id=prod_id
            ).pack(),
        )
    builder.adjust(1)

    pagination_buttons = []
    if current_page > 1:
        pagination_buttons.append(
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=ProductCallback(
                    level=1, category_id=category_id, page=current_page - 1
                ).pack(),
            )
        )

    if total_pages > 1:
        pagination_buttons.append(
            InlineKeyboardButton(
                text=f"{current_page}/{total_pages}", callback_data="ignore"
            )
        )

    if current_page < total_pages:
        pagination_buttons.append(
            InlineKeyboardButton(
                text="Вперёд ➡️",
                callback_data=ProductCallback(
                    level=1, category_id=category_id, page=current_page + 1
                ).pack(),
            )
        )

    if pagination_buttons:
        builder.row(*pagination_buttons)

    builder.row(
        InlineKeyboardButton(
            text="⬅️ Назад к категориям", callback_data=ProductCallback(level=0).pack()
        )
    )

    return builder.as_markup()


def get_product_confirmation_kb(
    product_id: int, category_id: int, page: int
) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text="✅ Подтвердить",
                callback_data=ProductCallback(
                    level=3,
                    action="confirm",
                    category_id=category_id,
                    product_id=product_id,
                    page=page,
                ).pack(),
            )
        ],
        [
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=ProductCallback(
                    level=1, category_id=category_id, page=page
                ).pack(),
            )
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_back_to_menu_kb() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text="⬅️ В главное меню", callback_data="back_to_main_menu"
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_faq_list_kb(faq_list: list[tuple[int, str]]) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=question, callback_data=FaqCallback(id=faq_id).pack()
            )
        ]
        for faq_id, question in faq_list
    ]
    buttons.append(
        [
            InlineKeyboardButton(
                text="⬅️ В главное меню", callback_data="back_to_main_menu"
            )
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_profile_kb(show_export_button: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if show_export_button:
        builder.row(
            InlineKeyboardButton(
                text="📄 Выгрузить полный список (.txt)",
                callback_data="export_products",
            )
        )

    builder.row(
        InlineKeyboardButton(text="⬅️ В главное меню", callback_data="back_to_main_menu")
    )
    return builder.as_markup()


def get_inline_search_kb() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text="🔍 Начать поиск продукта", switch_inline_query_current_chat=""
            )
        ],
        [
            InlineKeyboardButton(
                text="⬅️ В главное меню", callback_data="back_to_main_menu"
            )
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_back_to_products_kb(category_id: int, page: int = 1) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text="⬅️ Назад к списку продуктов",
                callback_data=ProductCallback(
                    level=1,
                    category_id=category_id,
                    page=page,
                ).pack(),
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
