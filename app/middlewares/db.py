from typing import Callable, Awaitable, Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.services import DBService


class DBMiddleware(BaseMiddleware):
    def __init__(self):
        self.__db = DBService()

    async def __call__(
            self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: dict[str, Any],
    ) -> Any:
        # print("Actions before handler", event.from_user.id)

        # Connect to DB
        await self.__db.connect()

        # Create Tables if they do not exist
        await self.__db.setup()

        # Add db to data
        data["db"] = self.__db

        # Run handler
        result = await handler(event, data)

        # Disconnect with DB
        await self.__db.close()

        # print("Actions after handler")

        return result
