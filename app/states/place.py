from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery


# State for Place Create
class PlaceCreate(StatesGroup):
    chat_id = State()
    callback_id = State()
    message_id = State()
    message_caption = State()
    lat = State()
    lon = State()
    name = State()


# State for Place Edit
class PlaceEdit(StatesGroup):
    chat_id = State()
    callback_id = State()
    message_id = State()
    message_caption = State()
    lat = State()
    lon = State()
    name = State()
    id = State()


# State for Places List
class PlacesList(StatesGroup):
    name = State()


async def save_callback_and_message(state: FSMContext, callback: CallbackQuery):
    """
    Set message_id, callback_id to State
    """
    await state.update_data(
        {
            "chat_id": callback.message.chat.id,
            "message_id": callback.message.message_id,
            "message_caption": callback.message.caption,
            "callback_id": callback.id,
        }
    )
