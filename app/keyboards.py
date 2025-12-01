from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from app.messages import Messages

main = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text=Messages.FAVORITE_PLACES_SEE_BUTTON,
            ),
            KeyboardButton(
                text=Messages.ACCOUNT_DELETE_BUTTON,
            ),
        ]
    ],
    resize_keyboard=True,
)

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

location = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text=Messages.FAVORITE_PLACES_ADD_BUTTON,
                callback_data="favorite_places_add",
            )
        ]
    ],
)
