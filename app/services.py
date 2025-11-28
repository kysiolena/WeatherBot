import os
from collections import namedtuple

import aiosqlite
import requests

Weather = namedtuple("Weather", ["text", "photo"])


class WeatherService:
    _API_URL = "https://api.openweathermap.org/data/2.5/weather"

    def _get_weather_by_coordinates(self, lat: float, lon: float) -> dict:
        params = {
            "lat": lat,
            "lon": lon,
            "appid": os.getenv("OPENWEATHERMAP_API_KEY"),
            "units": "metric",
        }

        response = requests.get(self._API_URL, params=params)

        return response.json()

    def _get_weather_by_city(self, city: str) -> dict:
        params = {
            "city": city,
            "appid": os.getenv("OPENWEATHERMAP_API_KEY"),
            "units": "metric",
        }

        response = requests.get(self._API_URL, params=params)

        return response.json()

    @staticmethod
    def get_icon_url(data: dict) -> str:
        weather: str = data["weather"][0]["icon"]

        icon_url: str = "https://openweathermap.org/img/wn/{0}@2x.png".format(weather)

        return icon_url

    @staticmethod
    def get_markdown_text(data: dict) -> str:
        weather: dict = data["weather"][0]
        main: dict = data["main"]
        wind: dict = data["wind"]

        description = f"_Weather:_ *{weather["description"].capitalize()}*"
        temperature = f"_Temperature:_ *{main["temp"]} °C*"
        feels_like = f"_Feels like:_ *{main["feels_like"]} °C*"
        pressure = f"_Pressure:_ *{main["pressure"]} hPa*"
        humidity = f"_Humidity:_ *{main["humidity"]} %*"
        wind_speed = f"_Wind:_ *{wind["speed"]} m/s*"

        text = "\n\n".join(
            [description, temperature, feels_like, pressure, humidity, wind_speed]
        )

        return text

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

        return Weather(self.get_markdown_text(data), self.get_icon_url(data))


class DBService:
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
            "user_id REAL,"
            "FOREIGN KEY (user_ID) REFERENCES users(id)"
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
