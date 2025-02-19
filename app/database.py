from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
import redis.asyncio as redis
from typing import AsyncGenerator

# SQLALCHEMY_DATABASE_URL = "mysql+aiomysql://hetu:hetu123@db/hetudb"

SQLALCHEMY_DATABASE_URL = "mysql+aiomysql://hetu:hetu123@127.0.0.1:3306/hetudb"

#REDIS_URL = "redis://redis:6379/0"
REDIS_URL = "redis://127.0.0.1:6379/0"

# SQLAlchemy setup
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

# Redis setup
redis_client = redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def get_redis():
    return redis_client
