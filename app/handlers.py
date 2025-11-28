from aiogram import F
from aiogram import html, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

import app.keyboards as kb
from app.services import WeatherService
from app.settings import db_s

router = Router()


@router.startup()
async def startup_handler():
    await db_s.connect()
    await db_s.setup()


@router.shutdown()
async def shutdown_handler():
    await db_s.close()


def get_hello_text(message: Message):
    return (
        f"Hello, {html.bold(message.from_user.full_name)}!\n\n"
        f"🗺 Send the location where you want to know the weather. "
    )


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """

    user = await db_s.get_user(message.from_user.id)

    if user:
        await message.answer(text=get_hello_text(message), reply_markup=kb.main)
    else:
        await message.answer(
            text="Please share your phone number to continue.", reply_markup=kb.phone
        )


@router.message(F.location)
async def location_handler(message: Message) -> None:
    w_s = WeatherService()

    weather = w_s.get_weather(
        lon=message.location.longitude, lat=message.location.latitude
    )

    await message.reply_photo(
        photo=weather.photo,
        caption=weather.text,
        parse_mode="Markdown",
        reply_markup=kb.main,
    )


@router.message(F.contact)
async def phone_handler(message: Message) -> None:
    tg_id = message.from_user.id
    phone = message.contact.phone_number

    await db_s.create_user(tg_id, phone)

    await message.answer(
        text=get_hello_text(message),
        reply_markup=kb.main,
    )
