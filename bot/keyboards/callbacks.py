from aiogram.filters.callback_data import CallbackData


class ProductCallback(CallbackData, prefix="prod"):
    level: int
    action: str | None = None
    category_id: int | None = None
    product_id: int | None = None
    page: int = 1


class FaqCallback(CallbackData, prefix="faq"):
    id: int


class InlineProductCallback(CallbackData, prefix="inline_prod"):
    action: str
    product_id: int
