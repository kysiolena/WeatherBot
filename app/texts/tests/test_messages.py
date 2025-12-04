from unittest.mock import Mock

from aiogram import html  # Needed to mock aiogram.types.Message

from app.texts import Messages

# --- Mock Data ---

# Mock the aiogram Message structure needed for get_hello_text
MOCK_USER_ID = 12345
MOCK_USER_NAME = "John Doe"

MOCK_MESSAGE = Mock(
    from_user=Mock(
        full_name=MOCK_USER_NAME,
        id=MOCK_USER_ID
    )
)


# --- Pytest Test Cases for Simple String Attributes ---

def test_messages_constants_are_correct():
    """
    Test that all simple string attributes (constants) are correctly defined.
    """
    assert Messages.LOCATION_SEND == "🗺 Send the location where you want to know the weather."
    assert Messages.PHONE_SHARE == "Please share your phone number to continue."
    assert Messages.ACCOUNT_DELETED == "Your account has been deleted."
    assert Messages.PLACES_SELECT == "📍 Select Favorite Place where you want to know the weather"
    assert Messages.PLACES_EMPTY == (
        "Your list of Favorite Places is currently empty 🥡.\n"
        "But you can always send a new location and save it 😉"
    )
    assert Messages.PLACES_ADD_SUCCESS == "Place was successfully added to your favorite places!"
    assert Messages.PLACES_DELETE_SUCCESS == "Place was successfully deleted from your favorite places!"
    assert Messages.PLACES_RENAME_SUCCESS == "Favorite place was successfully renamed!"
    assert Messages.PLACES_RENAME_ENTER_NAME == "Please enter new name for this favorite place"
    assert Messages.CANCEL_SUCCESS == "You have successfully returned to the main menu!"


# --- Pytest Test Cases for get_hello_text ---

def test_get_hello_text_success():
    """
    Test that get_hello_text correctly formats the greeting with the user's name bolded.
    """
    expected_bold_name = html.bold(MOCK_USER_NAME)
    expected_text = f"👋 Hello, {expected_bold_name}!\n\n"

    result = Messages.get_hello_text(MOCK_MESSAGE)

    assert result == expected_text


# --- Pytest Test Cases for get_weather_text ---

def test_get_weather_text_full_data():
    """
    Test that get_weather_text correctly formats the output when all optional arguments are provided.
    """
    description = "clear sky"
    temperature = 25.5
    feels_like = 24.8
    pressure = 1012
    humidity = 50
    wind_speed = 1.5

    expected_text = (
        "🌤 Weather: Clear sky\n\n"
        "🌡 Temperature: 25.5 °C\n\n"
        "🌡 Feels like: 24.8 °C\n\n"
        "🏋️‍♂️ Pressure: 1012 hPa\n\n"
        "💦 Humidity: 50 %\n\n"
        "💨 Wind: 1.5 m/s"
    )

    result = Messages.get_weather_text(
        description=description,
        temperature=temperature,
        feels_like=feels_like,
        pressure=pressure,
        humidity=humidity,
        wind_speed=wind_speed,
    )

    assert result == expected_text


def test_get_weather_text_partial_data():
    """
    Test that get_weather_text correctly formats the output when only a subset of arguments is provided.
    """
    description = "light rain"
    temperature = 15
    humidity = 80

    expected_text = (
        "🌤 Weather: Light rain\n\n"
        "🌡 Temperature: 15 °C\n\n"
        "💦 Humidity: 80 %"
    )

    result = Messages.get_weather_text(
        description=description,
        temperature=temperature,
        humidity=humidity,
        # other fields are None
    )

    assert result == expected_text


def test_get_weather_text_empty_data():
    """
    Test that get_weather_text returns an empty string when no arguments are provided.
    """
    expected_text = ""

    result = Messages.get_weather_text()

    assert result == expected_text


def test_get_weather_text_description_capitalization():
    """
    Test that the description argument is correctly capitalized.
    """
    description = "broken clouds"
    temperature = 10

    expected_text = (
        "🌤 Weather: Broken clouds\n\n"
        "🌡 Temperature: 10 °C"
    )

    result = Messages.get_weather_text(
        description=description,
        temperature=temperature,
    )

    assert result == expected_text
