from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
)

from app.messages import Messages

phone = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text=Messages.PHONE_SHARE_BUTTON,
                request_contact=True,
            )
        ]
    ],
    resize_keyboard=True,
)
