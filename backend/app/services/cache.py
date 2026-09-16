import json
import logging
import redis.asyncio as redis
from typing import Dict, Any
import os

logger = logging.getLogger(__name__)

# Initialize Redis client (typically configured centrally).
redis_client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))

async def get_revenue_summary(property_id: str, tenant_id: str) -> Dict[str, Any]:
    """
    Fetches revenue summary, utilizing caching to improve performance.
    """
    cache_key = f"revenue:{tenant_id}:{property_id}"

    # Try to get from cache
    cached = await redis_client.get(cache_key)
    if cached:
        logger.info(f"revenue: cache hit for {tenant_id}/{property_id}")
        return json.loads(cached)

    # Revenue calculation is delegated to the reservation service.
    from app.services.reservations import calculate_total_revenue

    logger.info(f"revenue: cache miss for {tenant_id}/{property_id}, hitting the db")

    # Calculate revenue
    result = await calculate_total_revenue(property_id, tenant_id)

    # Cache the result for 5 minutes
    await redis_client.setex(cache_key, 300, json.dumps(result))

    return result
