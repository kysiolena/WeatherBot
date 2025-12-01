from aiogram import F
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

import app.keyboards as kb
from app.messages import Messages
from app.services import WeatherService
from app.settings import db_s

router = Router()


@router.startup()
async def startup_handler() -> None:
    """
    This handler triggered when the bot is startup
    """
    await db_s.connect()
    await db_s.setup()


@router.shutdown()
async def shutdown_handler() -> None:
    """
    This handler triggered when the bot is shutdown
    """
    await db_s.close()


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """

    tg_id = message.from_user.id

    # Get User data by tg_id
    user = await db_s.get_user(tg_id)

    # Reply
    if user:
        # Authenticated User
        await message.answer(text=Messages.get_hello_text(message))
        await message.answer(text=Messages.LOCATION_SEND, reply_markup=kb.main)
    else:
        # Unauthenticated User
        await message.answer(text=Messages.PHONE_SHARE, reply_markup=kb.phone)


@router.message(F.location)
async def location_handler(message: Message) -> None:
    """
    This handler receives messages with location data
    """

    # Create instance
    w_s = WeatherService()

    # Get weather description
    weather = w_s.get_weather(
        lon=message.location.longitude, lat=message.location.latitude
    )

    # Reply
    await message.reply_photo(
        photo=weather.photo,
        caption=weather.text,
        parse_mode="Markdown",
        reply_markup=kb.location,
    )
    await message.answer(text=Messages.LOCATION_SEND, reply_markup=kb.main)


@router.message(F.contact)
async def phone_handler(message: Message) -> None:
    """
    This handler receives messages with contact data
    """

    tg_id = message.from_user.id
    phone = message.contact.phone_number

    # Create User
    await db_s.create_user(tg_id, phone)

    # Reply
    await message.answer(
        text=Messages.get_hello_text(message),
    )
    await message.answer(text=Messages.LOCATION_SEND, reply_markup=kb.main)


@router.message(F.text == Messages.ACCOUNT_DELETE_BUTTON)
async def account_delete_handler(message: Message) -> None:
    tg_id = message.from_user.id

    # Delete User
    await db_s.delete_user(tg_id)

    # Reply
    await message.answer(
        text=Messages.ACCOUNT_DELETED,
        reply_markup=kb.phone,
    )
