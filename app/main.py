from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
import logging
from app.database import get_db, get_redis, engine, Base
from app.api import endpoints
from app.sync.data_sync import start_sync_scheduler
import redis.asyncio as redis

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Hetu User Count API")

@app.on_event("startup")
async def startup_event():
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Start background sync task
    asyncio.create_task(
        start_sync_scheduler(
            db=AsyncSession(engine),
            redis_client=await get_redis()
        )
    )
    logger.info("Background sync task started")

@app.on_event("shutdown")
async def shutdown_event():
    await engine.dispose()
    redis_client = await get_redis()
    await redis_client.close()

# Include API routes
app.include_router(endpoints.router, prefix="/api/v1/users", tags=["users"])

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
