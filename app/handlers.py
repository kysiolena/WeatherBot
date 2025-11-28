from aiogram import F
from aiogram import html, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

import app.keyboards as kb
from app.services import WeatherService

router = Router()


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    text = (
        f"Hello, {html.bold(message.from_user.full_name)}!\n\n"
        f"🗺 Send the location where you want to know the weather. "
        f"Or click the Register button 👇 to start register process. "
        f"Once registered, you'll be able to save your favorite locations and quickly check the weather there ☺️"
    )

    await message.answer(
        text=text,
        reply_markup=kb.main,
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


@router.message(F.text)
async def message_handler(message: Message) -> None:
    print(message.text)
