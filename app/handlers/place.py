import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message

import app.keyboards as kb
from app.middlewares import DBMiddleware, AuthMiddleware
from app.services import WeatherService, DBService
from app.texts import Errors
from app.texts.callbacks import Callbacks
from app.texts.messages import Messages

# Router
place_router = Router()

# Known Handlers
place_router.message.middleware(DBMiddleware())
place_router.callback_query.middleware(DBMiddleware())
place_router.message.middleware(AuthMiddleware())
place_router.callback_query.middleware(AuthMiddleware())


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


@place_router.callback_query(F.data.startswith(Callbacks.PLACE_ADD))
async def place_add_first_handler(callback: CallbackQuery, state: FSMContext) -> None:
    lat, lon = list(map(float, callback.data.split("?")[1].split("|")))

    # Toggle State to name
    await state.set_state(PlaceCreate.name)

    # Set lat, lon to State
    await state.update_data(lat=lat)
    await state.update_data(lon=lon)

    await callback.message.answer(
        text=Messages.PLACES_RENAME_ENTER_NAME,
        reply_markup=kb.main,
    )

    # Set message_id, callback_id to State
    await state.update_data(chat_id=callback.message.chat.id)
    await state.update_data(message_id=callback.message.message_id)
    await state.update_data(message_caption=callback.message.caption)
    await state.update_data(callback_id=callback.id)


@place_router.message(PlaceCreate.name)
async def place_add_second_handler(message: Message, state: FSMContext, db: DBService) -> None:
    tg_id = message.from_user.id

    data = await state.get_data()

    await state.clear()

    name = message.text

    # Create Place
    place_id = await db.create_place(
        name=name,
        lon=data["lon"],
        lat=data["lat"],
        user_id=tg_id,
    )

    # Get new caption
    caption = data["message_caption"] + "\n\n" + f"*{name}*"

    await message.bot.answer_callback_query(callback_query_id=data["callback_id"],
                                            text=Messages.PLACES_ADD_SUCCESS)
    await message.bot.edit_message_caption(
        chat_id=data["chat_id"],
        message_id=data["message_id"],
        caption=caption,
        parse_mode="Markdown",
        reply_markup=kb.location(lat=data["lat"], lon=data["lon"], place_id=place_id),
    )
    await message.answer(text=Messages.LOCATION_SEND, reply_markup=kb.main)


@place_router.callback_query(F.data.startswith(Callbacks.PLACE_DELETE))
async def place_delete_handler(callback: CallbackQuery, db: DBService) -> None:
    lat, lon, place_id = callback.data.split("?")[1].split("|")

    # Delete Place
    await db.delete_place(place_id=int(place_id))

    # Get new caption
    caption = "\n\n".join(callback.message.caption.split("\n\n")[:-1])

    await callback.answer(Messages.PLACES_DELETE_SUCCESS)
    await callback.message.edit_caption(
        caption=caption,
        reply_markup=kb.location(lat=float(lat), lon=float(lon), place_id=None),
    )
    await callback.message.answer(text=Messages.LOCATION_SEND, reply_markup=kb.main)


@place_router.callback_query(F.data.startswith(Callbacks.PLACE_RENAME))
async def place_rename_first_handler(
        callback: CallbackQuery, state: FSMContext
) -> None:
    lat, lon, place_id = callback.data.split("?")[1].split("|")

    # Toggle State to name
    await state.set_state(PlaceEdit.name)

    # Set id, lat, lon to State
    await state.update_data(id=int(place_id))
    await state.update_data(lat=lat)
    await state.update_data(lon=lon)

    await callback.message.answer(
        text=Messages.PLACES_RENAME_ENTER_NAME,
        reply_markup=kb.main
    )

    # Set message_id, callback_id to State
    await state.update_data(chat_id=callback.message.chat.id)
    await state.update_data(message_id=callback.message.message_id)
    await state.update_data(message_caption=callback.message.caption)
    await state.update_data(callback_id=callback.id)


@place_router.message(PlaceEdit.name)
async def place_rename_second_handler(
        message: Message, state: FSMContext, db: DBService
) -> None:
    name = message.text

    # Get stored data
    data = await state.get_data()

    await state.clear()

    # Rename Place
    await db.update_place(place_id=data["id"], name=name)

    # Get new caption
    caption = data["message_caption"].split("\n\n")[:-1]
    caption.append(f"*{name}*")
    caption = "\n\n".join(caption)

    await message.bot.answer_callback_query(callback_query_id=data["callback_id"],
                                            text=Messages.PLACES_RENAME_SUCCESS)
    await message.bot.edit_message_caption(
        chat_id=data["chat_id"],
        message_id=data["message_id"],
        caption=caption,
        parse_mode="Markdown",
        reply_markup=kb.location(lat=data["lat"], lon=data["lon"], place_id=data["id"]),
    )


@place_router.message(F.text == Messages.PLACES_SEE_BUTTON)
async def place_see_handler(message: Message, state: FSMContext, db: DBService) -> None:
    tg_id = message.from_user.id

    places = await db.get_user_places(user_id=tg_id)

    await state.set_state(PlacesList.name)

    text = Messages.PLACES_SELECT if len(places) else Messages.PLACES_EMPTY

    await message.answer(
        text, reply_markup=kb.places(places=places)
    )


@place_router.message(PlacesList.name, F.text != Messages.BACK_TO_MAIN_MENU_BUTTON)
async def place_select_handler(message: Message, db: DBService) -> None:
    # Get Place
    place = await db.get_place_by_name(
        name=message.text, user_id=message.from_user.id
    )

    place_id, name, lat, lon, *rest = place or [None, None, None, None, None]

    # Create instance
    w_s = WeatherService()

    # Get weather description
    weather = await w_s.get_weather(lon=lon, lat=lat)

    if weather["error"]:
        logging.error(weather["error"])
        await message.answer(Errors.PLACE_SELECT)
    else:
        # Get caption
        caption = weather["text"] + "\n\n" + f"*{name}*"

        # Reply
        await message.reply_photo(
            photo=weather["photo"],
            caption=caption,
            parse_mode="Markdown",
            reply_markup=kb.location(lat=lat, lon=lon, place_id=place_id),
        )


@place_router.message(F.location)
async def place_location_handler(message: Message, db: DBService) -> None:
    """
    This handler receives messages with location data
    """
    tg_id = message.from_user.id
    lat = message.location.latitude
    lon = message.location.longitude

    # Create instance
    w_s = WeatherService()

    # Get weather description
    weather = await w_s.get_weather(lon=lon, lat=lat)

    if weather["error"]:
        logging.error(weather["error"])
        await message.answer(Errors.PLACE_SELECT)
    else:
        # Get Place
        place = await db.get_place_by_coordinates(user_id=tg_id, lon=lon, lat=lat)

        place_id, name, *rest = place or [None, None, None]

        # Get caption
        caption = weather["text"] + "\n\n" + f"*{name}*" if name else weather["text"]

        # Reply
        await message.reply_photo(
            photo=weather["photo"],
            caption=caption,
            parse_mode="Markdown",
            reply_markup=kb.location(
                lat=lat, lon=lon, place_id=place_id
            ),
        )
        await message.answer(text=Messages.LOCATION_SEND, reply_markup=kb.main)
