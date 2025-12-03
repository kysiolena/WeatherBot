import os
from collections import namedtuple

import requests

from app.texts.messages import Messages


Weather = namedtuple("Weather", ["text", "photo"])


class WeatherService:
    """
    Weather Service
    """

    _API_URL = "https://api.openweathermap.org/data/2.5/weather"
    _API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

    def _get_weather_by_coordinates(self, lat: float, lon: float) -> dict:
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self._API_KEY,
            "units": "metric",
        }

        response = requests.get(self._API_URL, params=params)

        return response.json()

    def _get_weather_by_city(self, city: str) -> dict:
        params = {
            "city": city,
            "appid": self._API_KEY,
            "units": "metric",
        }

        response = requests.get(self._API_URL, params=params)

        return response.json()

    @staticmethod
    def get_icon_url(data: dict) -> str:
        weather: str = data["weather"][0]["icon"]

        icon_url: str = "https://openweathermap.org/img/wn/{0}@2x.png".format(weather)

        return icon_url

    def get_weather(
            self,
            lat: float | None = None,
            lon: float | None = None,
            city: str | None = None,
    ) -> Weather:
        if city:
            data = self._get_weather_by_city(city)
        else:
            data = self._get_weather_by_coordinates(lat, lon)

        weather: dict = data["weather"][0]
        main: dict = data["main"]
        wind: dict = data["wind"]

        return Weather(
            Messages.get_weather_text(
                description=weather["description"],
                temperature=main["temp"],
                feels_like=main["feels_like"],
                pressure=main["pressure"],
                humidity=main["humidity"],
                wind_speed=wind["speed"],
            ),
            self.get_icon_url(data),
        )
