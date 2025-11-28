from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
)

main = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="See list of Saved Places",
            )
        ]
    ],
    resize_keyboard=True,
)

phone = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="Share the phone number",
                request_contact=True,
            )
        ]
    ],
    resize_keyboard=True,
)
