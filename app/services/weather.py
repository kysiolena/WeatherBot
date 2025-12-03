import os
from typing import TypedDict

import httpx

from app.texts import Messages


class TWeather(TypedDict):
    text: str | None
    photo: str | None
    error: str | None


class WeatherError(Exception):
    pass


class WeatherService:
    """
    Weather Service
    """

    _API_URL = "https://api.openweathermap.org/data/2.5/weather"
    _API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

    async def _get_weather_by_coordinates(self, lat: float, lon: float) -> dict | None:
        try:
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self._API_KEY,
                "units": "metric",
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(self._API_URL, params=params)

                # Raise an exception for bad status codes (4xx or 5xx)
                response.raise_for_status()

            return response.json()
        except httpx.HTTPStatusError as e:
            # Handle HTTP errors specifically
            raise WeatherError(f"HTTP error occurred: {e.response.status_code}")
        except Exception as e:
            raise WeatherError(e)

    async def _get_weather_by_city(self, city: str) -> dict | None:
        try:
            params = {
                "q": city,
                "appid": self._API_KEY,
                "units": "metric",
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(self._API_URL, params=params)

                # Raise an exception for bad status codes (4xx or 5xx)
                response.raise_for_status()

            return response.json()
        except httpx.HTTPStatusError as e:
            # Handle HTTP errors specifically
            raise WeatherError(f"HTTP error occurred: {e.response.status_code}")
        except Exception as e:
            raise WeatherError(e)

    @staticmethod
    def get_icon_url(data: dict) -> str | None:
        try:
            weather: str = data["weather"][0]["icon"]

            icon_url: str = "https://openweathermap.org/img/wn/{0}@2x.png".format(weather)

            return icon_url
        except Exception as e:
            raise WeatherError(e)

    async def get_weather(
            self,
            lat: float | None = None,
            lon: float | None = None,
            city: str | None = None,
    ) -> TWeather:
        res: TWeather = {
            "text": None,
            "photo": None,
            "error": None,
        }

        try:
            if city:
                data = await self._get_weather_by_city(city)
            else:
                data = await self._get_weather_by_coordinates(lat, lon)

            weather: dict = data["weather"][0]
            main: dict = data["main"]
            wind: dict = data["wind"]

            res["text"] = Messages.get_weather_text(
                description=weather["description"],
                temperature=main["temp"],
                feels_like=main["feels_like"],
                pressure=main["pressure"],
                humidity=main["humidity"],
                wind_speed=wind["speed"],
            )

            res["photo"] = self.get_icon_url(data)
        except Exception as e:
            res["error"] = str(e)
        finally:
            return res
