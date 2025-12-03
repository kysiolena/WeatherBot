from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
)

from app.texts.messages import Messages

main = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text=Messages.PLACES_SEE_BUTTON,
            ),
            KeyboardButton(
                text=Messages.ACCOUNT_DELETE_BUTTON,
            ),
        ]
    ],
    resize_keyboard=True,
)
