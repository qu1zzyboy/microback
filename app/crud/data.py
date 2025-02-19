from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.sql import func
from typing import List, Optional
from app.models.data import UserCount
from datetime import datetime
import redis.asyncio as redis

async def create_user_count(db: AsyncSession, count: int) -> UserCount:
    db_user_count = UserCount(
        count=count,
        timestamp=datetime.utcnow()
    )
    db.add(db_user_count)
    await db.commit()
    await db.refresh(db_user_count)
    return db_user_count

async def get_latest_count(db: AsyncSession) -> Optional[UserCount]:
    result = await db.execute(
        select(UserCount).order_by(desc(UserCount.timestamp)).limit(1)
    )
    return result.scalar_one_or_none()

async def get_count_history(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> tuple[List[UserCount], int]:
    # Get total count
    total = await db.scalar(select(func.count()).select_from(UserCount))
    
    # Get paginated results
    result = await db.execute(
        select(UserCount)
        .order_by(desc(UserCount.timestamp))
        .offset(skip)
        .limit(limit)
    )
    
    return list(result.scalars().all()), total

async def cache_user_count(redis_client: redis.Redis, count: int, timestamp: datetime):
    await redis_client.set(
        "latest_user_count",
        str(count),
        ex=300  # expire in 5 minutes
    )
    await redis_client.set(
        "latest_count_timestamp",
        timestamp.isoformat(),
        ex=300
    )

async def get_cached_count(redis_client: redis.Redis) -> tuple[Optional[int], Optional[datetime]]:
    count = await redis_client.get("latest_user_count")
    timestamp_str = await redis_client.get("latest_count_timestamp")
    
    if count and timestamp_str:
        return int(count), datetime.fromisoformat(timestamp_str)
    return None, None
