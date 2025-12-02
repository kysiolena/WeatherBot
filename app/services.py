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


class DBService:
    """
    Database Service
    """

    _connection: aiosqlite.Connection | None = None
    _cursor: aiosqlite.Cursor | None = None

    async def _create_trigger(self, table_name: str):
        await self._cursor.execute(
            f"CREATE TRIGGER IF NOT EXISTS update_{table_name}_updated_at "
            f"BEFORE UPDATE ON {table_name} "
            "FOR EACH ROW "
            "BEGIN "
            f"UPDATE {table_name} SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id; "
            "END"
        )

    async def _create_users_table(self):
        await self._cursor.execute(
            "CREATE TABLE IF NOT EXISTS users ("
            "id INTEGER PRIMARY KEY,"
            "phone TEXT,"
            "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
            "updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
            ")"
        )

        await self._create_trigger("users")

    async def _create_places_table(self):
        await self._cursor.execute(
            "CREATE TABLE IF NOT EXISTS places ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "name TEXT NOT NULL,"
            "lat REAL NOT NULL,"
            "lon REAL NOT NULL,"
            "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
            "updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
            "user_id INTEGER,"
            "UNIQUE (name, user_id),"
            "FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE"
            ")"
        )

        await self._create_trigger("places")

    async def _create_tables(self):
        await self._create_users_table()
        await self._create_places_table()

    async def create_user(self, user_id: int, phone: str):
        await self._cursor.execute(
            "INSERT INTO users (id, phone) VALUES (?, ?)", (user_id, phone)
        )

        await self._connection.commit()

    async def delete_user(self, user_id: int):
        await self._cursor.execute("DELETE FROM users WHERE id = (?)", (user_id,))
        await self._connection.commit()

    async def get_user(self, user_id: int):
        await self._cursor.execute("SELECT * FROM users WHERE id = (?)", (user_id,))
        user = await self._cursor.fetchone()

        return user

    async def get_user_places(self, user_id: int):
        await self._cursor.execute(
            "SELECT * FROM places WHERE user_id = (?)", (user_id,)
        )
        places = await self._cursor.fetchall()

        return places

    async def create_place(
            self, name: str, lat: int | float, lon: int | float, user_id: int
    ):
        await self._cursor.execute(
            "INSERT INTO places (name, lat, lon, user_id) VALUES (?, ?, ?, ?)",
            (name, lat, lon, user_id),
        )

        place_id = self._cursor.lastrowid

        await self._connection.commit()

        return place_id

    async def update_place(self, name: str, place_id: int):
        await self._cursor.execute(
            "UPDATE places SET name = (?) WHERE id = (?)",
            (name, place_id),
        )

        await self._connection.commit()

    async def delete_place(self, place_id: int):
        await self._cursor.execute("DELETE FROM places WHERE id = (?)", (place_id,))
        await self._connection.commit()

    async def get_place(self, place_id: int):
        await self._cursor.execute("SELECT * FROM places WHERE id = (?)", (place_id,))
        place = await self._cursor.fetchone()

        return place

    async def get_place_by_coordinates(
            self, user_id: int, lat: int | float, lon: int | float
    ):
        await self._cursor.execute(
            "SELECT * FROM places WHERE user_id = (?) AND lat = (?) AND lon = (?)",
            (
                user_id,
                lat,
                lon,
            ),
        )
        place = await self._cursor.fetchone()

        return place

    async def get_place_by_name(self, name: str, user_id: int):
        await self._cursor.execute(
            "SELECT * FROM places WHERE user_id = (?) AND name = (?)",
            (user_id, name),
        )
        place = await self._cursor.fetchone()

        return place

    async def connect(self):
        self._connection = await aiosqlite.connect(os.path.join("database.db"))

        # Enable Foreign Key Support
        await self._connection.execute("PRAGMA foreign_keys = ON;")

        self._cursor = await self._connection.cursor()

    async def close(self):
        await self._cursor.close()
        await self._connection.close()

    async def setup(self):
        await self._create_tables()
