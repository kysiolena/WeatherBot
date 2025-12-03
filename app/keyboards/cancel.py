from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
)

from app.texts import Buttons, Callbacks

cancel = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text=Buttons.CANCEL,
                callback_data=Callbacks.CANCEL
            ),
        ]
    ],
)
