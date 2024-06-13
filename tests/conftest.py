from dotenv import load_dotenv
import os
import asyncio
from typing import AsyncGenerator
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()
os.environ["ENV"] = "test"
from src.main import app
from src.models import Base


@pytest.fixture(scope='session')
async def init_db():
    engine_test = create_async_engine(os.getenv("DATABASE_URL_TEST"))
    async_session_maker = sessionmaker(engine_test)
    session = async_session_maker()
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine_test.dispose()
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


client = TestClient(app)


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
