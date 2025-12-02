from aiogram import F
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

import app.keyboards as kb
from app.messages import Messages
from app.middlewares import DBMiddleware
from app.services import DBService

# Router
main_router = Router()

# Known Handlers
main_router.message.middleware(DBMiddleware())


@main_router.message(CommandStart())
async def command_start_handler(message: Message, db: DBService) -> None:
    """
    This handler receives messages with `/start` command
    """

    tg_id = message.from_user.id

    # Get User data by tg_id
    user = await db.get_user(tg_id)

    # Reply
    if user:
        # Authenticated User
        await message.answer(text=Messages.get_hello_text(message))
        await message.answer(text=Messages.LOCATION_SEND, reply_markup=kb.main)
    else:
        # Unauthenticated User
        await message.answer(text=Messages.PHONE_SHARE, reply_markup=kb.phone)


@main_router.message(F.text == Messages.BACK_TO_MAIN_MENU_BUTTON)
async def back_to_main_menu_handler(message: Message, state: FSMContext) -> None:
    await state.clear()

    await message.answer(Messages.LOCATION_SEND, reply_markup=kb.main)
