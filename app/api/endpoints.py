from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis
from app.database import get_db, get_redis
from app.crud.data import get_latest_count, get_count_history, get_cached_count
from app.schemas.data import UserCountResponse, UserCountHistory
from datetime import datetime

router = APIRouter()

@router.get("/count", response_model=UserCountResponse)
async def get_current_count(
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis)
):
    # Try to get from cache first
    cached_count, cached_timestamp = await get_cached_count(redis_client)
    if cached_count is not None and cached_timestamp is not None:
        return UserCountResponse(
            current_count=cached_count,
            last_updated=cached_timestamp
        )
    
    # If not in cache, get from database
    db_count = await get_latest_count(db)
    if not db_count:
        raise HTTPException(status_code=404, detail="No count data available")
    
    return UserCountResponse(
        current_count=db_count.count,
        last_updated=db_count.timestamp
    )

@router.get("/history", response_model=UserCountHistory)
async def get_count_history_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    history, total = await get_count_history(db, skip=skip, limit=limit)
    return UserCountHistory(
        history=history,
        total_records=total
    )
