from aiogram import F
from aiogram import Router
from aiogram.types import Message

import app.keyboards as kb
from app.messages import Messages
from app.middlewares import DBMiddleware
from app.services import DBService

# Router
account_router = Router()

# Known Handlers
account_router.message.middleware(DBMiddleware())
account_router.callback_query.middleware(DBMiddleware())


@account_router.message(F.contact)
async def account_create_handler(message: Message, db: DBService) -> None:
    """
    This handler receives messages with contact data and creates new user
    """

    tg_id = message.from_user.id
    phone = message.contact.phone_number

    # Create User
    await db.create_user(tg_id, phone)

    # Reply
    await message.answer(
        text=Messages.get_hello_text(message),
    )
    await message.answer(text=Messages.LOCATION_SEND, reply_markup=kb.main)


@account_router.message(F.text == Messages.ACCOUNT_DELETE_BUTTON)
async def account_delete_handler(message: Message, db: DBService) -> None:
    tg_id = message.from_user.id

    # Delete User
    await db.delete_user(tg_id)

    # Reply
    await message.answer(
        text=Messages.ACCOUNT_DELETED,
        reply_markup=kb.phone,
    )
