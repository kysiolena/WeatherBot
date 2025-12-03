from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.texts.callbacks import Callbacks
from app.texts.messages import Messages


def location(
        lat: int | float | None = None,
        lon: int | float | None = None,
        place_id: int | None = None,
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    if place_id:
        kb.add(
            InlineKeyboardButton(
                text=Messages.PLACES_RENAME_BUTTON,
                callback_data=f"{Callbacks.PLACE_RENAME}?{lat}|{lon}|{place_id}",
            )
        )
        kb.add(
            InlineKeyboardButton(
                text=Messages.PLACES_DELETE_BUTTON,
                callback_data=f"{Callbacks.PLACE_DELETE}?{lat}|{lon}|{place_id}",
            )
        )

    else:
        kb.add(
            InlineKeyboardButton(
                text=Messages.PLACES_ADD_BUTTON,
                callback_data=f"{Callbacks.PLACE_ADD}?{lat}|{lon}",
            )
        )

    return kb.adjust(1).as_markup()
