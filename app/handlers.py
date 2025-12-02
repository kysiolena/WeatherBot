from aiogram import F
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

import app.keyboards as kb
from app.callbacks import Callbacks
from app.messages import Messages
from app.middlewares import DBMiddleware
from app.services import WeatherService, DBService

# Router
router = Router()

# Known Handlers
router.message.middleware(DBMiddleware())
router.callback_query.middleware(DBMiddleware())


# All Handlers
# router.message.outer_middleware(DBMiddleware())

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


@router.message(CommandStart())
async def command_start_handler(message: Message, db: DBService) -> None:
    """
    This handler receives messages with `/start` command
    """

    tg_id = message.from_user.id

    # Get User data by tg_id
    user = await db.get_user(tg_id)

    # Reply
    if user:
        # Authenticated User
        await message.answer(text=Messages.get_hello_text(message))
        await message.answer(text=Messages.LOCATION_SEND, reply_markup=kb.main)
    else:
        # Unauthenticated User
        await message.answer(text=Messages.PHONE_SHARE, reply_markup=kb.phone)


@router.message(F.contact)
async def phone_handler(message: Message, db: DBService) -> None:
    """
    This handler receives messages with contact data
    """

    tg_id = message.from_user.id
    phone = message.contact.phone_number

    # Create User
    await db.create_user(tg_id, phone)

    # Reply
    await message.answer(
        text=Messages.get_hello_text(message),
    )
    await message.answer(text=Messages.LOCATION_SEND, reply_markup=kb.main)


@router.message(F.text == Messages.ACCOUNT_DELETE_BUTTON)
async def account_delete_handler(message: Message, db: DBService) -> None:
    tg_id = message.from_user.id

    # Delete User
    await db.delete_user(tg_id)

    # Reply
    await message.answer(
        text=Messages.ACCOUNT_DELETED,
        reply_markup=kb.phone,
    )


@router.message(F.location)
async def location_handler(message: Message, db: DBService) -> None:
    """
    This handler receives messages with location data
    """
    tg_id = message.from_user.id
    lat = message.location.latitude
    lon = message.location.longitude

    # Create instance
    w_s = WeatherService()

    # Get weather description
    weather = w_s.get_weather(lon=lon, lat=lat)

    # Get Place
    place = await db.get_place_by_coordinates(user_id=tg_id, lon=lon, lat=lat)

    # Get caption
    caption = weather.text + "\n\n" + f"*{place[0]}*" if place else weather.text

    # Reply
    await message.reply_photo(
        photo=weather.photo,
        caption=caption,
        parse_mode="Markdown",
        reply_markup=kb.location(
            lat=lat, lon=lon, place_id=place[0] if place else None
        ),
    )
    await message.answer(text=Messages.LOCATION_SEND, reply_markup=kb.main)


@router.callback_query(F.data.startswith(Callbacks.FAVORITE_PLACE_ADD))
async def favorite_palace_add_first_handler(callback: CallbackQuery, state: FSMContext, db: DBService) -> None:
    lat, lon = list(map(float, callback.data.split("?")[1].split("|")))

    # Toggle State to name
    await state.set_state(PlaceCreate.name)

    # Set lat, lon to State
    await state.update_data(lat=lat)
    await state.update_data(lon=lon)

    await callback.message.answer(
        text=Messages.FAVORITE_PLACES_RENAME_ENTER_NAME,
        reply_markup=kb.main,
    )

    # Set message_id, callback_id to State
    await state.update_data(chat_id=callback.message.chat.id)
    await state.update_data(message_id=callback.message.message_id)
    await state.update_data(message_caption=callback.message.caption)
    await state.update_data(callback_id=callback.id)


@router.message(PlaceCreate.name)
async def favorite_palace_add_second_handler(message: Message, state: FSMContext, db: DBService) -> None:
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
                                            text=Messages.FAVORITE_PLACES_ADD_SUCCESS)
    await message.bot.edit_message_caption(
        chat_id=data["chat_id"],
        message_id=data["message_id"],
        caption=caption,
        parse_mode="Markdown",
        reply_markup=kb.location(lat=data["lat"], lon=data["lon"], place_id=place_id),
    )
    await message.answer(text=Messages.LOCATION_SEND, reply_markup=kb.main)


@router.callback_query(F.data.startswith(Callbacks.FAVORITE_PLACE_DELETE))
async def favorite_palace_delete_handler(callback: CallbackQuery, db: DBService) -> None:
    lat, lon, place_id = callback.data.split("?")[1].split("|")

    # Delete Place
    await db.delete_place(place_id=int(place_id))

    # Get new caption
    caption = "\n\n".join(callback.message.caption.split("\n\n")[:-1])

    await callback.answer(Messages.FAVORITE_PLACES_DELETE_SUCCESS)
    await callback.message.edit_caption(
        caption=caption,
        reply_markup=kb.location(lat=float(lat), lon=float(lon), place_id=None),
    )
    await callback.message.answer(text=Messages.LOCATION_SEND, reply_markup=kb.main)


@router.callback_query(F.data.startswith(Callbacks.FAVORITE_PLACE_RENAME))
async def favorite_palace_rename_first_handler(
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
        text=Messages.FAVORITE_PLACES_RENAME_ENTER_NAME,
        reply_markup=kb.main
    )

    # Set message_id, callback_id to State
    await state.update_data(chat_id=callback.message.chat.id)
    await state.update_data(message_id=callback.message.message_id)
    await state.update_data(message_caption=callback.message.caption)
    await state.update_data(callback_id=callback.id)


@router.message(PlaceEdit.name)
async def favorite_palace_rename_second_handler(
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
                                            text=Messages.FAVORITE_PLACES_RENAME_SUCCESS)
    await message.bot.edit_message_caption(
        chat_id=data["chat_id"],
        message_id=data["message_id"],
        caption=caption,
        parse_mode="Markdown",
        reply_markup=kb.location(lat=data["lat"], lon=data["lon"], place_id=data["id"]),
    )


@router.message(F.text == Messages.FAVORITE_PLACES_SEE_BUTTON)
async def favorite_palace_see_handler(message: Message, state: FSMContext, db: DBService) -> None:
    tg_id = message.from_user.id

    places = await db.get_user_places(user_id=tg_id)

    await state.set_state(PlacesList.name)

    text = Messages.FAVORITE_PLACES_SELECT if len(places) else Messages.FAVORITE_PLACES_EMPTY

    await message.answer(
        text, reply_markup=kb.places(places=places)
    )


@router.message(PlacesList.name, F.text != Messages.BACK_TO_MAIN_MENU_BUTTON)
async def favorite_place_select_handler(message: Message, db: DBService) -> None:
    # Get Place
    place = await db.get_place_by_name(
        name=message.text, user_id=message.from_user.id
    )

    place_id, name, lat, lon, *rest = place

    # Create instance
    w_s = WeatherService()

    # Get weather description
    weather = w_s.get_weather(lon=lon, lat=lat)

    # Get caption
    caption = weather.text + "\n\n" + f"*{name}*"

    # Reply
    await message.reply_photo(
        photo=weather.photo,
        caption=caption,
        parse_mode="Markdown",
        reply_markup=kb.location(lat=lat, lon=lon, place_id=place_id),
    )


@router.message(F.text == Messages.BACK_TO_MAIN_MENU_BUTTON)
async def back_to_main_menu_handler(message: Message, state: FSMContext) -> None:
    await state.clear()

    await message.answer(Messages.LOCATION_SEND, reply_markup=kb.main)
