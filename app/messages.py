from aiogram import html
from aiogram.types import Message


class Messages:
    LOCATION_SEND = "🗺 Send the location where you want to know the weather."

    PHONE_SHARE = "Please share your phone number to continue."
    PHONE_SHARE_BUTTON = "Share the phone number"

    ACCOUNT_DELETED = "Your account has been deleted."
    ACCOUNT_DELETE_BUTTON = "❌ Delete account"

    FAVORITE_PLACES_SEE_BUTTON = "🧡 See Favorite Places"
    FAVORITE_PLACES_ADD_BUTTON = "➕ Add to Favorite Places"

    @staticmethod
    def get_hello_text(message: Message) -> str:
        """
        This function creates and returns the greeting text from the message if the user is already authenticated
        """
        return f"👋 Hello, {html.bold(message.from_user.full_name)}!\n\n"

    @staticmethod
    def get_markdown_weather_text(
            description: str | int | float | None = None,
            temperature: str | int | float | None = None,
            feels_like: str | int | float | None = None,
            pressure: str | int | float | None = None,
            humidity: str | int | float | None = None,
            wind_speed: str | int | float | None = None,
    ) -> str:
        text = []

        if description:
            text.append(f"🌤 _Weather:_ *{description.capitalize()}*")

        if temperature:
            text.append(f"🌡 _Temperature:_ *{temperature} °C*")

        if feels_like:
            text.append(f"🌡 _Feels like:_ *{feels_like} °C*")

        if pressure:
            text.append(f"🏋️‍♂️ _Pressure:_ *{pressure} hPa*")

        if humidity:
            text.append(f"💦 _Humidity:_ *{humidity} %*")

        if wind_speed:
            text.append(f"💨 _Wind:_ *{wind_speed} m/s*")

        return "\n\n".join(text)
