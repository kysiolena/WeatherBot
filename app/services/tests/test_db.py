from sqlite3 import Row

import aiosqlite
import pytest
import pytest_asyncio

from app.services.db import DBService, DBError


# --- Fixture for In-Memory Database Service ---

@pytest_asyncio.fixture
async def db_service() -> DBService:
    """
    Fixture to set up an in-memory SQLite database, create tables,
    and yield a connected DBService instance for testing.
    """
    # 1. Initialize DBService
    db = DBService()

    try:
        # 2. Establish in-memory connection manually (bypassing the file path in connect())
        db._connection = await aiosqlite.connect(":memory:")

        # 3. Set the row factory
        # This allows accessing columns by name (e.g., user['id'])
        db._connection.row_factory = aiosqlite.Row

        # 4. Enable Foreign Key Support
        await db._connection.execute("PRAGMA foreign_keys = ON;")
        db._cursor = await db._connection.cursor()

        # 5. Setup tables
        await db.setup()

        yield db
    finally:
        # 4. Cleanup
        if db._connection:
            await db.close()


# --- Constants for Testing ---

TEST_USER_ID = 123456
TEST_USER_PHONE = "1234567890"

PLACE_1_NAME = "Home"
PLACE_1_LAT = 40.7128
PLACE_1_LON = -74.0060

PLACE_2_NAME = "Work"
PLACE_2_LAT = 34.0522
PLACE_2_LON = -118.2437


# --- Pytest Test Cases for User Operations ---

@pytest.mark.asyncio
async def test_create_and_get_user_success(db_service: DBService):
    """
    Tests successful creation of a user and subsequent retrieval.
    """
    # 1. Create User
    created_user_id = await db_service.create_user(
        user_id=TEST_USER_ID, phone=TEST_USER_PHONE
    )

    # Note: SQLite's lastrowid for a row inserted with explicit ID is often the ID itself
    assert created_user_id == TEST_USER_ID

    # 2. Get User
    user = await db_service.get_user(user_id=TEST_USER_ID)

    assert isinstance(user, Row)
    assert user["id"] == TEST_USER_ID
    assert user["phone"] == TEST_USER_PHONE


@pytest.mark.asyncio
async def test_get_nonexistent_user(db_service: DBService):
    """
    Tests retrieval of a user that does not exist.
    """
    user = await db_service.get_user(user_id=99999)
    assert user is None


@pytest.mark.asyncio
async def test_create_user_duplicate_id_raises_dberror(db_service: DBService):
    """
    Tests that attempting to create a user with an existing ID raises DBError
    due to primary key constraint violation.
    """
    await db_service.create_user(user_id=TEST_USER_ID, phone=TEST_USER_PHONE)

    with pytest.raises(DBError) as excinfo:
        await db_service.create_user(user_id=TEST_USER_ID, phone="0000000000")

    assert "UNIQUE constraint failed: users.id" in str(excinfo.value)


@pytest.mark.asyncio
async def test_delete_user_success(db_service: DBService):
    """
    Tests successful deletion of an existing user.
    """
    # 1. Create user
    await db_service.create_user(user_id=TEST_USER_ID, phone=TEST_USER_PHONE)

    # 2. Delete user
    result = await db_service.delete_user(user_id=TEST_USER_ID)
    assert result is True

    # 3. Verify deletion
    user = await db_service.get_user(user_id=TEST_USER_ID)
    assert user is None


# --- Pytest Test Cases for Place Operations ---

@pytest.mark.asyncio
async def test_get_user_places_empty(db_service: DBService):
    """
    Tests retrieving an empty list of places for a user.
    """
    # Create user first
    await db_service.create_user(user_id=TEST_USER_ID, phone=TEST_USER_PHONE)

    places = await db_service.get_user_places(user_id=TEST_USER_ID)
    assert places == []


@pytest.mark.asyncio
async def test_create_and_get_user_places_success(db_service: DBService):
    """
    Tests creating multiple places and retrieving them for a specific user.
    """
    # 1. Setup: Create user
    await db_service.create_user(user_id=TEST_USER_ID, phone=TEST_USER_PHONE)

    # 2. Create places
    place_1_id = await db_service.create_place(
        name=PLACE_1_NAME, lat=PLACE_1_LAT, lon=PLACE_1_LON, user_id=TEST_USER_ID
    )
    place_2_id = await db_service.create_place(
        name=PLACE_2_NAME, lat=PLACE_2_LAT, lon=PLACE_2_LON, user_id=TEST_USER_ID
    )

    # 3. Get all places for user
    places = await db_service.get_user_places(user_id=TEST_USER_ID)

    assert len(places) == 2
    assert isinstance(places, list)
    assert all(isinstance(p, Row) for p in places)
    assert {p["name"] for p in places} == {PLACE_1_NAME, PLACE_2_NAME}
    assert {p["id"] for p in places} == {place_1_id, place_2_id}


@pytest.mark.asyncio
async def test_create_place_duplicate_name_raises_dberror(db_service: DBService):
    """
    Tests that the UNIQUE (name, user_id) constraint prevents duplicate place names
    for the same user.
    """
    await db_service.create_user(user_id=TEST_USER_ID, phone=TEST_USER_PHONE)

    await db_service.create_place(
        name=PLACE_1_NAME, lat=PLACE_1_LAT, lon=PLACE_1_LON, user_id=TEST_USER_ID
    )

    with pytest.raises(DBError) as excinfo:
        await db_service.create_place(
            name=PLACE_1_NAME, lat=55.0, lon=55.0, user_id=TEST_USER_ID
        )

    assert "UNIQUE constraint failed: places.name, places.user_id" in str(excinfo.value)


@pytest.mark.asyncio
async def test_update_place_success(db_service: DBService):
    """
    Tests successful renaming of a place.
    """
    await db_service.create_user(user_id=TEST_USER_ID, phone=TEST_USER_PHONE)
    place_id = await db_service.create_place(
        name=PLACE_1_NAME, lat=PLACE_1_LAT, lon=PLACE_1_LON, user_id=TEST_USER_ID
    )
    NEW_NAME = "My New Home"

    # 1. Update place name
    result = await db_service.update_place(name=NEW_NAME, place_id=place_id)
    assert result is True

    # 2. Verify update
    place = await db_service.get_place(place_id=place_id)
    assert place["name"] == NEW_NAME


@pytest.mark.asyncio
async def test_delete_place_success(db_service: DBService):
    """
    Tests successful deletion of a place.
    """
    await db_service.create_user(user_id=TEST_USER_ID, phone=TEST_USER_PHONE)
    place_id = await db_service.create_place(
        name=PLACE_1_NAME, lat=PLACE_1_LAT, lon=PLACE_1_LON, user_id=TEST_USER_ID
    )

    # 1. Delete place
    result = await db_service.delete_place(place_id=place_id)
    assert result is True

    # 2. Verify deletion
    place = await db_service.get_place(place_id=place_id)
    assert place is None


@pytest.mark.asyncio
async def test_get_place_by_coordinates_success(db_service: DBService):
    """
    Tests retrieving a place using coordinates and user ID.
    """
    await db_service.create_user(user_id=TEST_USER_ID, phone=TEST_USER_PHONE)
    await db_service.create_place(
        name=PLACE_1_NAME, lat=PLACE_1_LAT, lon=PLACE_1_LON, user_id=TEST_USER_ID
    )

    place = await db_service.get_place_by_coordinates(
        user_id=TEST_USER_ID, lat=PLACE_1_LAT, lon=PLACE_1_LON
    )

    assert isinstance(place, Row)
    assert place["name"] == PLACE_1_NAME


@pytest.mark.asyncio
async def test_get_place_by_name_success(db_service: DBService):
    """
    Tests retrieving a place using name and user ID.
    """
    await db_service.create_user(user_id=TEST_USER_ID, phone=TEST_USER_PHONE)
    await db_service.create_place(
        name=PLACE_1_NAME, lat=PLACE_1_LAT, lon=PLACE_1_LON, user_id=TEST_USER_ID
    )

    place = await db_service.get_place_by_name(
        name=PLACE_1_NAME, user_id=TEST_USER_ID
    )

    assert isinstance(place, Row)
    assert place["lat"] == PLACE_1_LAT


@pytest.mark.asyncio
async def test_delete_user_cascades_delete_places(db_service: DBService):
    """
    Tests that deleting a user automatically deletes their associated places
    due to the FOREIGN KEY ... ON DELETE CASCADE constraint.
    """
    # 1. Setup: Create user and a place
    await db_service.create_user(user_id=TEST_USER_ID, phone=TEST_USER_PHONE)
    await db_service.create_place(
        name=PLACE_1_NAME, lat=PLACE_1_LAT, lon=PLACE_1_LON, user_id=TEST_USER_ID
    )

    # 2. Verify place exists
    places_before = await db_service.get_user_places(user_id=TEST_USER_ID)
    assert len(places_before) == 1

    # 3. Delete user
    await db_service.delete_user(user_id=TEST_USER_ID)

    # 4. Verify places are gone
    places_after = await db_service.get_user_places(user_id=TEST_USER_ID)
    assert places_after == []
