import os

import aiosqlite


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
