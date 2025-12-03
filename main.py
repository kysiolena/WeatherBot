import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode

from app.handlers import account_router, place_router, main_router


async def main() -> None:
    # Bot token can be obtained via https://t.me/BotFather
    token = os.getenv("BOT_TOKEN")

    session = AiohttpSession(proxy="http://proxy.server:3128")

    # All handlers should be attached to the Router (or Dispatcher)
    dp = Dispatcher()

    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(
        token=token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        session=session
    )

    # Router
    dp.include_routers(account_router, place_router, main_router)

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    # Display info about Bot state
    if os.getenv("IS_DEBUG"):
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program interrupted by user. Exiting gracefully.")
