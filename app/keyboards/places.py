from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from app.texts.messages import Messages


def places(
        places: list,
) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()

    for place in places:
        kb.add(
            KeyboardButton(
                text=place[1],
            )
        )

    kb.add(
        KeyboardButton(
            text=Messages.BACK_TO_MAIN_MENU_BUTTON,
        )
    )

    return kb.adjust(2).as_markup(resize_keyboard=True)
