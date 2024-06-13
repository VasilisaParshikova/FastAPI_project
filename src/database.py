from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

load_dotenv()


def get_database_url():
    if os.environ.get("ENV") == "test":
        return os.getenv("DATABASE_URL_TEST")
    elif os.environ.get("ENV") == "debug":
        return os.getenv("DATABASE_URL_DEBUG")
    else:
        return os.getenv("DATABASE_URL")



DATABASE_URL = get_database_url()

engine = create_async_engine(DATABASE_URL, echo=True)

async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
session = async_session()
Base = declarative_base()
