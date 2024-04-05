from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = "sqlite+aiosqlite:///./app.db"

engine = create_async_engine(DATABASE_URL, echo=True)

async_session = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)
session = async_session()
Base = declarative_base()
