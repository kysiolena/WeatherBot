from aiogram import html
from aiogram.types import Message


class Messages:
    BACK_TO_MAIN_MENU_BUTTON = "Back to Main Menu ↩️"

    LOCATION_SEND = "🗺 Send the location where you want to know the weather."

    PHONE_SHARE = "Please share your phone number to continue."
    PHONE_SHARE_BUTTON = "Share the phone number"

    ACCOUNT_DELETED = "Your account has been deleted."
    ACCOUNT_DELETE_BUTTON = "❌ Delete account"

    FAVORITE_PLACES_SEE_BUTTON = "🧡 See Favorite Places"
    FAVORITE_PLACES_SELECT = (
        "📍 Select Favorite Place where you want to know the weather"
    )
    FAVORITE_PLACES_EMPTY = ("Your list of Favorite Places is currently empty 🥡.\n"
                             "But you can always send a new location and save it 😉")
    FAVORITE_PLACES_ADD_BUTTON = "➕ Add to Favorite Places"
    FAVORITE_PLACES_ADD_SUCCESS = (
        "Place was successfully added to your favorite places!"
    )
    FAVORITE_PLACES_DELETE_BUTTON = "❌ Delete from Favorite Places"
    FAVORITE_PLACES_DELETE_SUCCESS = (
        "Place was successfully deleted from your favorite places!"
    )
    FAVORITE_PLACES_RENAME_BUTTON = "✏️ Rename Favorite Place"
    FAVORITE_PLACES_RENAME_SUCCESS = "Favorite place was successfully renamed!"
    FAVORITE_PLACES_RENAME_ENTER_NAME = "Please enter new name for this favorite place"

    @staticmethod
    def get_hello_text(message: Message) -> str:
        """
        This function creates and returns the greeting text from the message if the user is already authenticated
        """
        return f"👋 Hello, {html.bold(message.from_user.full_name)}!\n\n"

    @staticmethod
    def get_weather_text(
            description: str | int | float | None = None,
            temperature: str | int | float | None = None,
            feels_like: str | int | float | None = None,
            pressure: str | int | float | None = None,
            humidity: str | int | float | None = None,
            wind_speed: str | int | float | None = None,
    ) -> str:
        text = []

        if description:
            text.append(f"🌤 Weather: {description.capitalize()}")

        if temperature:
            text.append(f"🌡 Temperature: {temperature} °C")

        if feels_like:
            text.append(f"🌡 Feels like: {feels_like} °C")

        if pressure:
            text.append(f"🏋️‍♂️ Pressure: {pressure} hPa")

        if humidity:
            text.append(f"💦 Humidity: {humidity} %")

        if wind_speed:
            text.append(f"💨 Wind: {wind_speed} m/s")

        return "\n\n".join(text)
