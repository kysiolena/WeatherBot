from unittest.mock import Mock, patch, AsyncMock

import httpx
import pytest

from app.services import WeatherService, WeatherError

# --- Additional Mocks for get_weather method ---

MOCK_WEATHER_TEXT = "Mocked formatted weather description."
MOCK_ICON_URL = "https://openweathermap.org/img/wn/01d@2x.png"


# Define a fixture for the WeatherService instance
@pytest.fixture
def weather_service():
    # It's good practice to patch the API key during tests, even if it's not strictly necessary
    # for these specific tests as we are mocking the entire request.
    with patch.dict('os.environ', {'OPENWEATHERMAP_API_KEY': 'DUMMY_KEY'}):
        return WeatherService()


# --- Mock Response Data ---

# A typical successful response from OpenWeatherMap
MOCK_SUCCESS_RESPONSE_DATA = {
    "coord": {"lon": 33.39, "lat": 44.55},
    "weather": [{"id": 800, "main": "Clear", "description": "clear sky", "icon": "01d"}],
    "base": "stations",
    "main": {"temp": 25.5, "feels_like": 24.8, "temp_min": 25.5, "temp_max": 25.5, "pressure": 1012, "humidity": 50},
    "visibility": 10000,
    "wind": {"speed": 1.5, "deg": 10},
    "clouds": {"all": 0},
    "dt": 1678886400,
    "sys": {"type": 1, "id": 9037, "country": "UA", "sunrise": 1678861200, "sunset": 1678904400},
    "timezone": 7200,
    "id": 703448,
    "name": "Kyiv",
    "cod": 200
}


# --- Mocking HTTPX Responses (AsyncClient.get) ---

# We need a mock object that simulates the httpx.Response object and can be awaited.
class MockAsyncResponse:
    def __init__(self, status_code, json_data=None):
        self.status_code = status_code
        self._json_data = json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            # Simulate httpx.HTTPStatusError
            raise httpx.HTTPStatusError(
                f"Status code {self.status_code}",
                request=Mock(),
                response=Mock(status_code=self.status_code)
            )

    def json(self):
        return self._json_data


# Define an async function that return 200-HTTPStatus
async def mock_async_get_success(*args, **kwargs):
    return MockAsyncResponse(200, MOCK_SUCCESS_RESPONSE_DATA)


# Define an async function that raises a 404-HTTPStatusError exception
async def mock_async_get_404(*args, **kwargs):
    return MockAsyncResponse(404)


# Define an async function that raises a 500-HTTPStatusError exception
async def mock_async_get_500(*args, **kwargs):
    return MockAsyncResponse(500)


# Define an async function that raises a non-HTTPStatusError exception
async def mock_async_get_raise_exception(*args, **kwargs):
    raise httpx.ConnectError("A mock connection failure.")


# --- Pytest Test Cases for _get_weather_by_coordinates ---

@pytest.mark.asyncio
async def test_get_weather_by_coordinates_success(weather_service, monkeypatch):
    """
    Test successful retrieval of weather data by coordinates.
    Mocks the entire httpx.AsyncClient.get call.
    """
    # 1. Setup the mock for AsyncClient.get
    # The `get` method is a method on the *instance* of AsyncClient,
    # but since AsyncClient is used within an `async with` block, mocking
    # the method globally on the class is the most straightforward way here.
    # The `__aenter__` method of AsyncClient returns 'self', so we mock the `get`
    # method on the class.
    monkeypatch.setattr(httpx.AsyncClient, 'get', mock_async_get_success)

    # 2. Call the method under test
    lat, lon = 44.55, 33.39
    result = await weather_service._get_weather_by_coordinates(lat, lon)

    # 3. Assert the result
    assert result == MOCK_SUCCESS_RESPONSE_DATA
    assert result['name'] == "Kyiv"
    assert result['main']['temp'] == 25.5


@pytest.mark.asyncio
async def test_get_weather_by_coordinates_404_error(weather_service, monkeypatch):
    """
    Test handling of a 404 HTTP error (e.g., coordinates not found or invalid API key).
    Should raise a WeatherError with the status code.
    """
    # 1. Setup the mock for AsyncClient.get to return a 404 response
    monkeypatch.setattr(httpx.AsyncClient, 'get', mock_async_get_404)

    # 2. Call the method and assert the exception
    with pytest.raises(WeatherError) as excinfo:
        await weather_service._get_weather_by_coordinates(lat=0.0, lon=0.0)

    # 3. Assert the exception message
    assert "HTTP error occurred: 404" in str(excinfo.value)


@pytest.mark.asyncio
async def test_get_weather_by_coordinates_500_error(weather_service, monkeypatch):
    """
    Test handling of a 500 HTTP error (e.g., internal server error).
    Should raise a WeatherError with the status code.
    """
    # 1. Setup the mock for AsyncClient.get to return a 500 response
    monkeypatch.setattr(httpx.AsyncClient, 'get', mock_async_get_500)

    # 2. Call the method and assert the exception
    with pytest.raises(WeatherError) as excinfo:
        await weather_service._get_weather_by_coordinates(lat=0.0, lon=0.0)

    # 3. Assert the exception message
    assert "HTTP error occurred: 500" in str(excinfo.value)


@pytest.mark.asyncio
async def test_get_weather_by_coordinates_connection_error(weather_service, monkeypatch):
    """
    Test handling of a general exception, such as a connection error (httpx.ConnectError).
    """

    # 1. Setup the mock for AsyncClient.get to raise a connection error
    monkeypatch.setattr(httpx.AsyncClient, 'get', mock_async_get_raise_exception)

    # 2. Call the method and assert the exception
    with pytest.raises(WeatherError) as excinfo:
        await weather_service._get_weather_by_coordinates(lat=0.0, lon=0.0)

    # 3. Assert the exception message
    assert "A mock connection failure." in str(excinfo.value)


# --- Pytest Test Cases for _get_weather_by_city ---

@pytest.mark.asyncio
async def test_get_weather_by_city_success(weather_service, monkeypatch):
    """
    Test successful retrieval of weather data by city name.
    Mocks the entire httpx.AsyncClient.get call.
    """
    # 1. Setup the mock for AsyncClient.get
    monkeypatch.setattr(httpx.AsyncClient, 'get', mock_async_get_success)

    # 2. Call the method under test
    city = "Kyiv"
    result = await weather_service._get_weather_by_city(city)

    # 3. Assert the result
    assert result == MOCK_SUCCESS_RESPONSE_DATA
    # Check that the mocked city name is present in the response
    assert result['name'] == city
    assert result['main']['temp'] == 25.5


@pytest.mark.asyncio
async def test_get_weather_by_city_404_error(weather_service, monkeypatch):
    """
    Test handling of a 404 HTTP error (e.g., city not found).
    Should raise a WeatherError with the status code.
    """
    # 1. Setup the mock for AsyncClient.get to return a 404 response
    monkeypatch.setattr(httpx.AsyncClient, 'get', mock_async_get_404)

    # 2. Call the method and assert the exception
    with pytest.raises(WeatherError) as excinfo:
        await weather_service._get_weather_by_city(city="NonExistentCity")

    # 3. Assert the exception message
    assert "HTTP error occurred: 404" in str(excinfo.value)


@pytest.mark.asyncio
async def test_get_weather_by_city_500_error(weather_service, monkeypatch):
    """
    Test handling of a 500 HTTP error (e.g., internal server error).
    Should raise a WeatherError with the status code.
    """
    # 1. Setup the mock for AsyncClient.get to return a 500 response
    monkeypatch.setattr(httpx.AsyncClient, 'get', mock_async_get_500)

    # 2. Call the method and assert the exception
    with pytest.raises(WeatherError) as excinfo:
        await weather_service._get_weather_by_city(city="ServerProblemCity")

    # 3. Assert the exception message
    assert "HTTP error occurred: 500" in str(excinfo.value)


@pytest.mark.asyncio
async def test_get_weather_by_city_connection_error(weather_service, monkeypatch):
    """
    Test handling of a general exception, such as a connection error (httpx.ConnectError).
    """
    # 1. Setup the mock for AsyncClient.get to raise a connection error
    monkeypatch.setattr(httpx.AsyncClient, 'get', mock_async_get_raise_exception)

    # 2. Call the method and assert the exception
    with pytest.raises(WeatherError) as excinfo:
        await weather_service._get_weather_by_city(city="DisconnectedCity")

    # 3. Assert the exception message
    assert "A mock connection failure." in str(excinfo.value)


# --- Pytest Test Cases for get_icon_url ---

def test_get_icon_url_success():
    """
    Test successful generation of the icon URL from valid weather data.
    """
    # 1. Setup mock data
    mock_data = {
        "weather": [
            {
                "id": 500,
                "main": "Rain",
                "description": "light rain",
                "icon": "10d"  # The icon code we expect to use
            }
        ]
    }
    expected_url = "https://openweathermap.org/img/wn/10d@2x.png"

    # 2. Call the static method
    result = WeatherService.get_icon_url(mock_data)

    # 3. Assert the result
    assert result == expected_url


def test_get_icon_url_handles_missing_keys():
    """
    Test that the method raises WeatherError when the input data is missing
    the required nested keys (e.g., 'weather' or 'icon').
    """
    # Case 1: Missing 'weather' key
    malformed_data_1 = {"main": {}}
    with pytest.raises(WeatherError):
        WeatherService.get_icon_url(malformed_data_1)

    # Case 2: Missing 'icon' key inside 'weather' list
    malformed_data_2 = {
        "weather": [
            {"id": 800, "main": "Clear", "description": "clear sky"}  # 'icon' key is missing
        ]
    }
    with pytest.raises(WeatherError):
        WeatherService.get_icon_url(malformed_data_2)

    # Case 3: Empty weather list
    malformed_data_3 = {"weather": []}
    with pytest.raises(WeatherError):
        WeatherService.get_icon_url(malformed_data_3)


# --- Pytest Test Cases for get_weather ---

@pytest.mark.asyncio
@patch("app.services.WeatherService.get_icon_url", Mock(return_value=MOCK_ICON_URL))
# Mock the text formatter method, which is the other major external dependency
@patch("app.texts.Messages.get_weather_text", Mock(return_value=MOCK_WEATHER_TEXT))
async def test_get_weather_by_coordinates_full_success(weather_service, monkeypatch):
    """
    Test the full successful flow of get_weather using coordinates.
    Mocks the underlying API call and the text/icon formatter utilities.
    """
    # 1. Mock the internal coordinates API call to return success data
    mock_coordinates_call = AsyncMock(return_value=MOCK_SUCCESS_RESPONSE_DATA)
    monkeypatch.setattr(weather_service, "_get_weather_by_coordinates", mock_coordinates_call)

    # 2. Call the method under test
    lat, lon = 44.55, 33.39
    result = await weather_service.get_weather(lat=lat, lon=lon)

    # 3. Assertions
    # Check that the correct internal method was called with the right arguments
    mock_coordinates_call.assert_awaited_once_with(lat, lon)

    # Check that the result dictionary is correct
    assert result["text"] == MOCK_WEATHER_TEXT
    assert result["photo"] == MOCK_ICON_URL
    assert result["error"] is None


@pytest.mark.asyncio
@patch("app.services.WeatherService.get_icon_url", Mock(return_value=MOCK_ICON_URL))
@patch("app.texts.Messages.get_weather_text", Mock(return_value=MOCK_WEATHER_TEXT))
async def test_get_weather_by_city_full_success(weather_service, monkeypatch):
    """
    Test the full successful flow of get_weather using city name.
    Mocks the underlying API call and the text/icon formatter utilities.
    """
    # 1. Mock the internal city API call to return success data
    mock_city_call = AsyncMock(return_value=MOCK_SUCCESS_RESPONSE_DATA)
    monkeypatch.setattr(weather_service, "_get_weather_by_city", mock_city_call)

    # 2. Call the method under test (passing city should skip coordinates path)
    city = "Kyiv"
    result = await weather_service.get_weather(city=city)

    # 3. Assertions
    # Check that the city method was called
    mock_city_call.assert_awaited_once_with(city)

    # Check that the result dictionary is correct
    assert result["text"] == MOCK_WEATHER_TEXT
    assert result["photo"] == MOCK_ICON_URL
    assert result["error"] is None


@pytest.mark.asyncio
async def test_get_weather_handles_internal_weather_error(weather_service, monkeypatch):
    """
    Test that get_weather catches WeatherError raised by underlying methods and
    returns it in the 'error' field.
    """
    # 1. Mock the internal call to raise a WeatherError
    error_message = "HTTP error occurred: 401"
    mock_error_call = Mock(side_effect=WeatherError(error_message))
    monkeypatch.setattr(weather_service, "_get_weather_by_coordinates", mock_error_call)

    # 2. Call the method under test
    result = await weather_service.get_weather(lat=0.0, lon=0.0)

    # 3. Assertions
    assert result["text"] is None
    assert result["photo"] is None
    assert result["error"] == error_message


@pytest.mark.asyncio
async def test_get_weather_handles_key_error_on_malformed_data(weather_service, monkeypatch):
    """
    Test that get_weather handles KeyError (e.g., if API response is missing a required field)
    and returns a generic error message.
    """
    # 1. Mock the internal call to return data missing the 'wind' key
    malformed_data = MOCK_SUCCESS_RESPONSE_DATA.copy()
    del malformed_data["wind"]

    mock_malformed_call = AsyncMock(return_value=malformed_data)
    monkeypatch.setattr(weather_service, "_get_weather_by_coordinates", mock_malformed_call)

    # 2. Call the method under test
    result = await weather_service.get_weather(lat=0.0, lon=0.0)

    # 3. Assertions
    assert result["text"] is None
    assert result["photo"] is None
    # We expect a string representation of the KeyError, e.g., "'wind'"
    assert "KeyError" in result["error"] or "'wind'" in result["error"]
