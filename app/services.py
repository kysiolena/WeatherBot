import os
from collections import namedtuple

import aiosqlite
import requests

from app.messages import Messages

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
            Messages.get_markdown_weather_text(
                description=weather["description"],
                temperature=main["temp"],
                feels_like=main["feels_like"],
                pressure=main["pressure"],
                humidity=main["humidity"],
                wind_speed=wind["speed"],
            ),
            self.get_icon_url(data),
        )


class DBService:
    """
    Database Service
    """

    _connection: aiosqlite.Connection | None = None
    _cursor: aiosqlite.Cursor | None = None

    async def _create_users_table(self):
        await self._cursor.execute(
            "CREATE TABLE IF NOT EXISTS users ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "phone TEXT,"
            "tg_id INTEGER"
            ")"
        )

    async def _create_places_table(self):
        await self._cursor.execute(
            "CREATE TABLE IF NOT EXISTS places ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "name TEXT,"
            "lat REAL,"
            "long REAL,"
            "user_id INTEGER,"
            "FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE"
            ")"
        )

    async def _create_tables(self):
        await self._create_users_table()
        await self._create_places_table()

    async def create_user(self, tg_id: int, phone: str):
        await self._cursor.execute(
            "INSERT INTO users (tg_id, phone) VALUES (?, ?)", (tg_id, phone)
        )
        await self._connection.commit()

    async def delete_user(self, tg_id: int):
        await self._cursor.execute("DELETE FROM users WHERE tg_id = (?)", (tg_id,))
        await self._connection.commit()

    async def get_user(self, tg_id: int):
        await self._cursor.execute("SELECT * FROM users WHERE tg_id = (?)", (tg_id,))
        user = await self._cursor.fetchone()

        return user

    async def connect(self):
        self._connection = await aiosqlite.connect(os.path.join("database.db"))
        self._cursor = await self._connection.cursor()

    async def close(self):
        await self._cursor.close()
        await self._connection.close()

    async def setup(self):
        await self._create_tables()
