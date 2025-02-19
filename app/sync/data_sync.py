import aiohttp
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from app.crud.data import create_user_count, cache_user_count
import redis.asyncio as redis

logger = logging.getLogger(__name__)

HETU_API_URL = "https://api.hetuverse.com/api/v1/user/count"

async def fetch_user_count() -> int:
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(HETU_API_URL) as response:
                if response.status == 200:
                    data = await response.json()
                    print(data)
                    return data["result"]["count"]
                else:
                    logger.error(f"API request failed with status {response.status}")
                    raise Exception(f"API request failed with status {response.status}")
        except Exception as e:
            logger.error(f"Error fetching user count: {str(e)}")
            raise

async def sync_user_count(db: AsyncSession, redis_client: redis.Redis):
    try:
        # Fetch count from API
        count = await fetch_user_count()
        
        # Store in database
        user_count = await create_user_count(db, count)
        
        # Update cache
        await cache_user_count(
            redis_client,
            count,
            user_count.timestamp
        )
        
        logger.info(f"Successfully synced user count: {count}")
        return count
    except Exception as e:
        logger.error(f"Failed to sync user count: {str(e)}")
        raise

async def start_sync_scheduler(db: AsyncSession, redis_client: redis.Redis):
    while True:
        try:
            await sync_user_count(db, redis_client)
        except Exception as e:
            logger.error(f"Sync scheduler error: {str(e)}")
        
        # Wait for 5 minutes before next sync
        await asyncio.sleep(300)

if __name__ == '__main__':
    import asyncio
    asyncio.run(fetch_user_count())