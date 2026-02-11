import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest

# Use SQLite for testing (no external database needed)
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"

# Now import app modules
from datetime import datetime
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from core.redis import redis_manager
from core.setup import Base, get_db
from main import app
from models.task_model import Task
from models.user_model import User
from schemas import PriorityEnum
from utils.auth_utils import hash_pwd


@pytest.fixture
def user_data() -> dict:
    return {
        "email": "testuser@example.com",
        "username": "testuser",
        "password": "TestPass123!",
    }


@pytest.fixture
def user_create_data() -> dict:
    return {
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "NewPass123!",
        "confirm_password": "NewPass123!",
    }


@pytest.fixture
def admin_user_data() -> dict:
    return {
        "email": "admin@example.com",
        "username": "admin",
        "password": "AdminPass123!",
    }


@pytest.fixture
async def test_user(db_session: AsyncSession, user_data: dict) -> User:
    """Create a test user in database."""
    hashed_password = hash_pwd(user_data["password"])
    user = User(
        email=user_data["email"],
        username=user_data["username"],
        password=hashed_password,
        created_at=datetime.utcnow(),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


# ========== TASK FIXTURES ==========
@pytest.fixture
def task_data() -> dict:
    return {
        "title": "Test Task",
        "description": "Test task description",
        "time": "2024-12-31T23:59:59",
        "priority": PriorityEnum.HIGH.value,
        "is_completed": False,
    }


@pytest.fixture
def task_create_data() -> dict:
    return {
        "title": "New Task",
        "description": "New task description",
        "time": "3pm",
        "priority": PriorityEnum.MEDIUM.value,
        "is_completed": False,
        "user_id": 1,
    }


@pytest.fixture
def task_update_data() -> dict:
    return {
        "title": "Updated Task Title",
        "description": "Updated description",
        "is_completed": True,
    }


@pytest.fixture
async def test_task(db_session: AsyncSession, test_user: User) -> Task:
    """Create a test task for a user."""
    task = Task(
        title="Complete project",
        description="Finish the FastAPI project with tests",
        time="2024-12-31T23:59:59",
        priority=PriorityEnum.HIGH.value,
        is_completed=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        user_id=test_user.id,
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)
    return task


@pytest.fixture
async def multiple_tasks(db_session: AsyncSession, test_user: User) -> list[Task]:
    """Create multiple tasks for a user."""
    tasks = []
    priorities = [PriorityEnum.HIGH, PriorityEnum.MEDIUM, PriorityEnum.LOW]

    for i in range(5):
        task = Task(
            title=f"Task {i}",
            description=f"Description for task {i}",
            time=f"2024-12-{i + 1:02d}T12:00:00",
            priority=priorities[i % 3].value,
            is_completed=(i % 2 == 0),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            user_id=test_user.id,
        )
        tasks.append(task)
        db_session.add(task)

    await db_session.commit()
    for task in tasks:
        await db_session.refresh(task)

    return tasks


@pytest.fixture
async def tasks_for_multiple_users(
    db_session: AsyncSession, multiple_users: list[User]
) -> dict:
    """Create tasks for multiple different users."""
    user_tasks = {}

    for user in multiple_users:
        tasks = []
        for i in range(2):
            task = Task(
                title=f"Task for {user.username} #{i}",
                description=f"Task description for {user.username}",
                time="2024-12-31T23:59:59",
                priority=PriorityEnum.MEDIUM.value,
                is_completed=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                user_id=user.id,
            )
            tasks.append(task)
            db_session.add(task)

        await db_session.commit()
        for task in tasks:
            await db_session.refresh(task)

        user_tasks[user.id] = tasks

    return user_tasks


@pytest.fixture
async def multiple_users(db_session: AsyncSession) -> list[User]:
    """Create multiple test users."""
    users = []
    for i in range(3):
        user = User(
            email=f"user{i}@example.com",
            username=f"user{i}",
            password=hash_pwd(f"Password{i}!"),
            created_at=datetime.utcnow(),
        )
        users.append(user)
        db_session.add(user)

    await db_session.commit()
    for user in users:
        await db_session.refresh(user)

    return users


# Test engine with SQLite
test_engine = create_async_engine(
    "sqlite+aiosqlite:///./test.db",
    poolclass=NullPool,
    echo=False,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """Create and drop test database tables."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    # Clean up SQLite file
    import os

    if os.path.exists("./test.db"):
        os.remove("./test.db")


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        try:
            # Start a transaction
            await session.begin()
            yield session
        finally:
            # ROLLBACK EVERYTHING
            await session.rollback()
            await session.close()


# @pytest.fixture
# async def client(db_session: AsyncSession) -> AsyncGenerator[TestClient, None]:
#     """Create test client with overridden dependencies."""

#     async def override_get_db():
#         try:
#             yield db_session
#         finally:
#             pass

#     app.dependency_overrides[get_db] = override_get_db

#     with TestClient(app) as test_client:
#         yield test_client


#     app.dependency_overrides.clear()
@pytest.fixture(autouse=True)
async def mock_redis():
    """Mock Redis connection, NOT the rate limit dependency."""
    # Mock the Redis client
    mock_client = AsyncMock()

    # Mock all Redis methods used in rate limiting
    mock_client.zremrangebyscore = AsyncMock(return_value=0)
    mock_client.zcard = AsyncMock(return_value=0)
    mock_client.zadd = AsyncMock(return_value=1)
    mock_client.expire = AsyncMock(return_value=True)

    # Patch the redis_manager.client
    with patch.object(redis_manager, "client", mock_client):
        yield


@pytest.fixture
def client(db_session: AsyncSession):
    """Create test client with mocked Redis."""
    app.dependency_overrides[get_db] = lambda: db_session

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
