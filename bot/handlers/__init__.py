from aiogram import Dispatcher

from .about import router as about_router
from .faq import router as faq_router
from .inline_search import router as inline_search_router
from .menu import router as menu_router
from .product_actions import router as product_actions_router
from .profile import router as profile_router
from .start import router as start_router


def setup_handlers(dp: Dispatcher) -> None:
    dp.include_routers(
        inline_search_router,
        start_router,
        menu_router,
        profile_router,
        product_actions_router,
        about_router,
        faq_router,
    )
