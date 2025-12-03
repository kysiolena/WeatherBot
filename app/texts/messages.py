from aiogram import html
from aiogram.types import Message


class Messages:
    LOCATION_SEND = "🗺 Send the location where you want to know the weather."
    PHONE_SHARE = "Please share your phone number to continue."
    ACCOUNT_DELETED = "Your account has been deleted."
    PLACES_SELECT = (
        "📍 Select Favorite Place where you want to know the weather"
    )
    PLACES_EMPTY = ("Your list of Favorite Places is currently empty 🥡.\n"
                    "But you can always send a new location and save it 😉")
    PLACES_ADD_SUCCESS = (
        "Place was successfully added to your favorite places!"
    )
    PLACES_DELETE_SUCCESS = (
        "Place was successfully deleted from your favorite places!"
    )
    PLACES_RENAME_SUCCESS = "Favorite place was successfully renamed!"
    PLACES_RENAME_ENTER_NAME = "Please enter new name for this favorite place"
    CANCEL_SUCCESS = "You have successfully returned to the main menu!"

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
