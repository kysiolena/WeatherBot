from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
)

from app.texts import Buttons

main = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text=Buttons.PLACES_SEE,
            ),
            KeyboardButton(
                text=Buttons.ACCOUNT_DELETE,
            ),
        ]
    ],
    resize_keyboard=True,
)
