from typing import Callable, Awaitable, Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

import app.keyboards as kb
from app.messages import Messages


class AuthMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: dict[str, Any],
    ) -> Any:
        db = data.get("db")

        tg_id = event.from_user.id

        # Get User data by tg_id
        user = await db.get_user(tg_id)

        # Reply
        if user or (isinstance(event, Message) and event.contact):
            # Authenticated User
            return await handler(event, data)
        else:
            # Unauthenticated User
            if isinstance(event, Message):
                await event.answer(text=Messages.PHONE_SHARE, reply_markup=kb.phone)
            elif isinstance(event, CallbackQuery):
                await event.message.answer(text=Messages.PHONE_SHARE, reply_markup=kb.phone)

        return None
