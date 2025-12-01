from aiogram import F
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

import app.keyboards as kb
from app.callbacks import Callbacks
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


@router.message(F.location)
async def location_handler(message: Message) -> None:
    """
    This handler receives messages with location data
    """
    tg_id = message.from_user.id
    lat = message.location.latitude
    lon = message.location.longitude

    print(tg_id, message)

    # Create instance
    w_s = WeatherService()

    # Get weather description
    weather = w_s.get_weather(lon=lon, lat=lat)

    # Get Place
    place = await db_s.get_place_by_coordinates(user_id=tg_id, lon=lon, lat=lat)

    # Reply
    await message.reply_photo(
        photo=weather.photo,
        caption=weather.text,
        parse_mode="Markdown",
        reply_markup=kb.location(
            lat=lat, lon=lon, place_id=place.id if place else None
        ),
    )
    await message.answer(text=Messages.LOCATION_SEND, reply_markup=kb.main)


@router.callback_query(F.data.startswith(Callbacks.FAVORITE_PLACE_ADD))
async def favorite_palace_add_handler(callback: CallbackQuery) -> None:
    tg_id = callback.from_user.id
    lat, lon = list(map(float, callback.data.split("?")[1].split("|")))

    # Create Place
    place_id = await db_s.create_place(
        name="No name",
        lon=lon,
        lat=lat,
        user_id=tg_id,
    )

    await callback.answer(Messages.FAVORITE_PLACES_ADD_SUCCESS)
    await callback.message.edit_reply_markup(
        reply_markup=kb.location(lat=lat, lon=lon, place_id=place_id),
    )


@router.callback_query(F.data.startswith(Callbacks.FAVORITE_PLACE_DELETE))
async def favorite_palace_delete_handler(callback: CallbackQuery) -> None:
    place_id = float(callback.data.split("?")[1])

    # Delete Place
    await db_s.delete_place(place_id=int(place_id))

    await callback.answer(Messages.FAVORITE_PLACES_DELETE_SUCCESS)
    await callback.message.edit_reply_markup(
        reply_markup=kb.location(place_id=None),
    )
