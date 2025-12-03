from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
)

from app.texts import Buttons

phone = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text=Buttons.PHONE_SHARE,
                request_contact=True,
            )
        ]
    ],
    resize_keyboard=True,
)
