from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.callbacks import Callbacks
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


# location = InlineKeyboardMarkup(
#     inline_keyboard=[
#         [
#             InlineKeyboardButton(
#                 text=Messages.FAVORITE_PLACES_ADD_BUTTON,
#                 callback_data=Callbacks.FAVORITE_PLACE_ADD,
#             )
#         ]
#     ],
# )


def location(
        lat: int | float | None = None,
        lon: int | float | None = None,
        place_id: int | None = None,
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    if place_id:
        kb.add(
            InlineKeyboardButton(
                text=Messages.FAVORITE_PLACES_RENAME_BUTTON,
                callback_data=f"{Callbacks.FAVORITE_PLACE_RENAME}?{place_id}",
            )
        )
        kb.add(
            InlineKeyboardButton(
                text=Messages.FAVORITE_PLACES_DELETE_BUTTON,
                callback_data=f"{Callbacks.FAVORITE_PLACE_DELETE}?{place_id}",
            )
        )

    elif lat and lon:
        kb.add(
            InlineKeyboardButton(
                text=Messages.FAVORITE_PLACES_ADD_BUTTON,
                callback_data=f"{Callbacks.FAVORITE_PLACE_ADD}?{lat}|{lon}",
            )
        )

    return kb.adjust(1).as_markup()
