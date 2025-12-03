from aiogram import F
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

import app.keyboards as kb
from app.middlewares import DBMiddleware, AuthMiddleware
from app.texts.messages import Messages

# Router
main_router = Router()

# Known Handlers
main_router.message.middleware(DBMiddleware())
main_router.message.middleware(AuthMiddleware())


@main_router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """

    await message.answer(text=Messages.get_hello_text(message))
    await message.answer(text=Messages.LOCATION_SEND, reply_markup=kb.main)


@main_router.message(F.text == Messages.BACK_TO_MAIN_MENU_BUTTON)
async def back_to_main_menu_handler(message: Message, state: FSMContext) -> None:
    await state.clear()

    await message.answer(Messages.LOCATION_SEND, reply_markup=kb.main)
