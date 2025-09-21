from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from backend.users.models import User
from bot.states.registration import Registration

from ..utils.db import get_user_by_id


class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        user: User | None = await get_user_by_id(event.from_user.id)

        if not user:
            state: FSMContext = data.get("state")
            current_state_str = await state.get_state() if state else None

            is_registration_process = current_state_str in {
                s.state for s in Registration.__states__
            }
            if is_registration_process:
                return await handler(event, data)

            if (
                isinstance(event, Message)
                and event.text
                and event.text.startswith("/start")
            ):
                return await handler(event, data)

            text = "Вы не зарегистрированы. Пожалуйста, отправьте команду /start."

            await event.answer(text)
            return

        if user.challenge_status != User.ChallengeStatus.ACTIVE:
            message_text = "Ваш челлендж завершен. Спасибо за участие!"

            if isinstance(event, CallbackQuery):
                await event.answer(message_text, show_alert=True)
            elif isinstance(event, Message):
                await event.answer(message_text)
            return

        data["user"] = user
        return await handler(event, data)
