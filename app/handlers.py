from aiogram import F
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

import app.keyboards as kb
from app.callbacks import Callbacks
from app.messages import Messages
from app.services import WeatherService
from app.settings import db_s

# Router
router = Router()


# State for Place Edit
class PlaceEdit(StatesGroup):
    id = State()
    name = State()


# State for Places List
class PlacesList(StatesGroup):
    name = State()


@router.startup()
async def startup_handler() -> None:
    """
    This handler triggered when the bot is startup
    """
    await db_s.connect()
    await db_s.setup()


@router.shutdown()
async def shutdown_handler() -> None:
    """
    This handler triggered when the bot is shutdown
    """
    await db_s.close()


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """

    tg_id = message.from_user.id

    # Get User data by tg_id
    user = await db_s.get_user(tg_id)

    # Reply
    if user:
        # Authenticated User
        await message.answer(text=Messages.get_hello_text(message))
        await message.answer(text=Messages.LOCATION_SEND, reply_markup=kb.main)
    else:
        # Unauthenticated User
        await message.answer(text=Messages.PHONE_SHARE, reply_markup=kb.phone)


@router.message(F.contact)
async def phone_handler(message: Message) -> None:
    """
    This handler receives messages with contact data
    """

    tg_id = message.from_user.id
    phone = message.contact.phone_number

    # Create User
    await db_s.create_user(tg_id, phone)

    # Reply
    await message.answer(
        text=Messages.get_hello_text(message),
    )
    await message.answer(text=Messages.LOCATION_SEND, reply_markup=kb.main)


@router.message(F.text == Messages.ACCOUNT_DELETE_BUTTON)
async def account_delete_handler(message: Message) -> None:
    tg_id = message.from_user.id

    # Delete User
    await db_s.delete_user(tg_id)

    # Reply
    await message.answer(
        text=Messages.ACCOUNT_DELETED,
        reply_markup=kb.phone,
    )


@router.message(F.location)
async def location_handler(message: Message) -> None:
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
    place = await db_s.get_place_by_coordinates(user_id=tg_id, lon=lon, lat=lat)

    # Reply
    await message.reply_photo(
        photo=weather.photo,
        caption=weather.text,
        parse_mode="Markdown",
        reply_markup=kb.location(
            lat=lat, lon=lon, place_id=place.id if place else None
        ),
    )
    await message.answer(text=Messages.LOCATION_SEND, reply_markup=kb.main)


@router.callback_query(F.data.startswith(Callbacks.FAVORITE_PLACE_ADD))
async def favorite_palace_add_handler(callback: CallbackQuery) -> None:
    tg_id = callback.from_user.id
    lat, lon = list(map(float, callback.data.split("?")[1].split("|")))

    # Create Place
    place_id = await db_s.create_place(
        name="No name",
        lon=lon,
        lat=lat,
        user_id=tg_id,
    )

    await callback.answer(Messages.FAVORITE_PLACES_ADD_SUCCESS)
    await callback.message.edit_reply_markup(
        reply_markup=kb.location(lat=lat, lon=lon, place_id=place_id),
    )


@router.callback_query(F.data.startswith(Callbacks.FAVORITE_PLACE_DELETE))
async def favorite_palace_delete_handler(callback: CallbackQuery) -> None:
    place_id = float(callback.data.split("?")[1])

    # Delete Place
    await db_s.delete_place(place_id=int(place_id))

    await callback.answer(Messages.FAVORITE_PLACES_DELETE_SUCCESS)
    await callback.message.edit_reply_markup(
        reply_markup=kb.location(place_id=None),
    )


@router.callback_query(F.data.startswith(Callbacks.FAVORITE_PLACE_RENAME))
async def favorite_palace_rename_first_handler(
        callback: CallbackQuery, state: FSMContext
) -> None:
    place_id = int(callback.data.split("?")[1])

    # 1. Set current State
    await state.set_state(PlaceEdit.id)
    # Set Place ID to State
    await state.update_data(id=place_id)

    # 2. Update current State
    await state.set_state(PlaceEdit.name)

    await callback.message.answer(
        text=Messages.FAVORITE_PLACES_RENAME_ENTER_NAME, reply_markup=kb.main
    )


@router.message(PlaceEdit.name)
async def favorite_palace_rename_second_handler(
        message: Message, state: FSMContext
) -> None:
    # Set Place Name to State
    await state.update_data(name=message.text)

    # Get stored data
    data = await state.get_data()

    await state.clear()

    # Rename Place
    await db_s.update_place(place_id=data["id"], name=data["name"])

    await message.answer(Messages.FAVORITE_PLACES_RENAME_SUCCESS, reply_markup=kb.main)


@router.message(F.text == Messages.FAVORITE_PLACES_SEE_BUTTON)
async def favorite_palace_see_handler(message: Message, state: FSMContext) -> None:
    tg_id = message.from_user.id

    places = await db_s.get_user_places(user_id=tg_id)

    await state.set_state(PlacesList.name)

    await message.answer(
        Messages.FAVORITE_PLACES_SELECT, reply_markup=kb.places(places=places)
    )


@router.message(PlacesList.name, F.text != Messages.BACK_TO_MAIN_MENU_BUTTON)
async def favorite_place_select_handler(message: Message, state: FSMContext) -> None:
    # Get Place
    place = await db_s.get_place_by_name(
        name=message.text, user_id=message.from_user.id
    )

    place_id, name, lat, lon, *rest = place

    # Create instance
    w_s = WeatherService()

    # Get weather description
    weather = w_s.get_weather(lon=lon, lat=lat)

    # Reply
    await message.reply_photo(
        photo=weather.photo,
        caption=weather.text,
        parse_mode="Markdown",
        reply_markup=kb.location(lat=lat, lon=lon, place_id=place_id),
    )


@router.message(F.text == Messages.BACK_TO_MAIN_MENU_BUTTON)
async def back_to_main_menu_handler(message: Message, state: FSMContext) -> None:
    await state.clear()

    await message.answer(Messages.LOCATION_SEND, reply_markup=kb.main)
