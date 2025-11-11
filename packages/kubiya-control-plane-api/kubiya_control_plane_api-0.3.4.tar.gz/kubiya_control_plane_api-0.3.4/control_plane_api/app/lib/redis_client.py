"""Redis client for caching authentication tokens and user data using Upstash REST API."""

import os
import json
from typing import Optional, Any
import httpx
import structlog

logger = structlog.get_logger()

# Upstash Redis configuration
_redis_url: Optional[str] = None
_redis_token: Optional[str] = None


class UpstashRedisClient:
    """Upstash Redis client using direct HTTP REST API calls (serverless-friendly)."""

    def __init__(self, url: str, token: str):
        self.url = url.rstrip('/')
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    async def get(self, key: str) -> Optional[str]:
        """Get value from Redis."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    f"{self.url}/get/{key}",
                    headers=self.headers
                )

                if response.status_code == 200:
                    result = response.json()
                    return result.get("result")

                logger.warning("redis_get_failed", status=response.status_code, key=key[:20])
                return None

        except Exception as e:
            logger.warning("redis_get_error", error=str(e), key=key[:20])
            return None

    async def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        """Set value in Redis with optional expiry (seconds)."""
        try:
            # Build command
            if ex:
                command = ["SET", key, value, "EX", str(ex)]
            else:
                command = ["SET", key, value]

            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    f"{self.url}/pipeline",
                    headers=self.headers,
                    json=[command]
                )

                if response.status_code == 200:
                    return True

                logger.warning("redis_set_failed", status=response.status_code, key=key[:20])
                return False

        except Exception as e:
            logger.warning("redis_set_error", error=str(e), key=key[:20])
            return False

    async def setex(self, key: str, seconds: int, value: str) -> bool:
        """Set value in Redis with expiry (seconds). Alias for set with ex parameter."""
        return await self.set(key, value, ex=seconds)

    async def delete(self, key: str) -> bool:
        """Delete a key from Redis."""
        try:
            command = ["DEL", key]

            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    f"{self.url}/pipeline",
                    headers=self.headers,
                    json=[command]
                )

                if response.status_code == 200:
                    return True

                logger.warning("redis_delete_failed", status=response.status_code, key=key[:20])
                return False

        except Exception as e:
            logger.warning("redis_delete_error", error=str(e), key=key[:20])
            return False

    async def hset(self, key: str, mapping: dict) -> bool:
        """Set hash fields in Redis."""
        try:
            # Convert dict to list of field-value pairs
            fields = []
            for k, v in mapping.items():
                fields.extend([k, str(v)])

            command = ["HSET", key] + fields

            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    f"{self.url}/pipeline",
                    headers=self.headers,
                    json=[command]
                )

                if response.status_code == 200:
                    return True

                logger.warning("redis_hset_failed", status=response.status_code, key=key[:20])
                return False

        except Exception as e:
            logger.warning("redis_hset_error", error=str(e), key=key[:20])
            return False

    async def hgetall(self, key: str) -> Optional[dict]:
        """Get all hash fields from Redis."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    f"{self.url}/pipeline",
                    headers=self.headers,
                    json=[["HGETALL", key]]
                )

                if response.status_code == 200:
                    result = response.json()
                    if result and isinstance(result, list) and len(result) > 0:
                        data = result[0].get("result", [])
                        # Convert list to dict [k1, v1, k2, v2] -> {k1: v1, k2: v2}
                        return {data[i]: data[i+1] for i in range(0, len(data), 2)} if data else {}

                return None

        except Exception as e:
            logger.warning("redis_hgetall_error", error=str(e), key=key[:20])
            return None

    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiry on a key."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    f"{self.url}/pipeline",
                    headers=self.headers,
                    json=[["EXPIRE", key, str(seconds)]]
                )

                return response.status_code == 200

        except Exception as e:
            logger.warning("redis_expire_error", error=str(e), key=key[:20])
            return False

    async def sadd(self, key: str, *members: str) -> bool:
        """Add members to a set."""
        try:
            command = ["SADD", key] + list(members)

            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    f"{self.url}/pipeline",
                    headers=self.headers,
                    json=[command]
                )

                return response.status_code == 200

        except Exception as e:
            logger.warning("redis_sadd_error", error=str(e), key=key[:20])
            return False

    async def scard(self, key: str) -> int:
        """Get count of set members."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    f"{self.url}/pipeline",
                    headers=self.headers,
                    json=[["SCARD", key]]
                )

                if response.status_code == 200:
                    result = response.json()
                    if result and isinstance(result, list):
                        return result[0].get("result", 0)

                return 0

        except Exception as e:
            logger.warning("redis_scard_error", error=str(e), key=key[:20])
            return 0

    async def lpush(self, key: str, *values: str) -> bool:
        """Push values to start of list."""
        try:
            command = ["LPUSH", key] + list(values)

            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    f"{self.url}/pipeline",
                    headers=self.headers,
                    json=[command]
                )

                return response.status_code == 200

        except Exception as e:
            logger.warning("redis_lpush_error", error=str(e), key=key[:20])
            return False

    async def ltrim(self, key: str, start: int, stop: int) -> bool:
        """Trim list to specified range."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    f"{self.url}/pipeline",
                    headers=self.headers,
                    json=[["LTRIM", key, str(start), str(stop)]]
                )

                return response.status_code == 200

        except Exception as e:
            logger.warning("redis_ltrim_error", error=str(e), key=key[:20])
            return False

    async def lrange(self, key: str, start: int, stop: int) -> list:
        """Get range of list elements."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    f"{self.url}/pipeline",
                    headers=self.headers,
                    json=[["LRANGE", key, str(start), str(stop)]]
                )

                if response.status_code == 200:
                    result = response.json()
                    if result and isinstance(result, list):
                        return result[0].get("result", [])

                return []

        except Exception as e:
            logger.warning("redis_lrange_error", error=str(e), key=key[:20])
            return []

    async def llen(self, key: str) -> int:
        """Get length of list."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    f"{self.url}/pipeline",
                    headers=self.headers,
                    json=[["LLEN", key]]
                )

                if response.status_code == 200:
                    result = response.json()
                    if result and isinstance(result, list):
                        return result[0].get("result", 0)

                return 0

        except Exception as e:
            logger.warning("redis_llen_error", error=str(e), key=key[:20])
            return 0

    async def publish(self, channel: str, message: str) -> bool:
        """Publish message to Redis pub/sub channel."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    f"{self.url}/pipeline",
                    headers=self.headers,
                    json=[["PUBLISH", channel, message]]
                )

                if response.status_code == 200:
                    return True

                logger.warning("redis_publish_failed", status=response.status_code, channel=channel[:20])
                return False

        except Exception as e:
            logger.warning("redis_publish_error", error=str(e), channel=channel[:20])
            return False


def get_redis_client() -> Optional[UpstashRedisClient]:
    """
    Get or create Upstash Redis client using REST API.

    Returns:
        Redis client instance or None if not configured
    """
    global _redis_url, _redis_token

    # Try multiple environment variable names for compatibility
    if not _redis_url:
        _redis_url = (
            os.getenv("KV_REST_API_URL") or
            os.getenv("UPSTASH_REDIS_REST_URL") or
            os.getenv("UPSTASH_REDIS_URL")
        )

    if not _redis_token:
        _redis_token = (
            os.getenv("KV_REST_API_TOKEN") or
            os.getenv("UPSTASH_REDIS_REST_TOKEN") or
            os.getenv("UPSTASH_REDIS_TOKEN")
        )

    if not _redis_url or not _redis_token:
        logger.warning(
            "redis_not_configured",
            message="Redis REST API URL or TOKEN not set, caching disabled",
            checked_vars=["KV_REST_API_URL", "KV_REST_API_TOKEN", "UPSTASH_*"]
        )
        return None

    try:
        client = UpstashRedisClient(url=_redis_url, token=_redis_token)
        logger.debug("redis_client_created", url=_redis_url[:30] + "...")
        return client
    except Exception as e:
        logger.error("redis_client_init_failed", error=str(e))
        return None


# Worker-specific caching functions

async def cache_worker_heartbeat(
    worker_id: str,
    queue_id: str,
    organization_id: str,
    status: str,
    last_heartbeat: str,
    tasks_processed: int,
    system_info: Optional[dict] = None,
    ttl: int = 60
) -> bool:
    """
    Cache worker heartbeat data in Redis.

    Args:
        worker_id: Worker UUID
        queue_id: Queue UUID
        organization_id: Organization ID
        status: Worker status
        last_heartbeat: ISO timestamp
        tasks_processed: Task count
        system_info: Optional system metrics
        ttl: Cache TTL in seconds

    Returns:
        True if cached successfully
    """
    client = get_redis_client()
    if not client:
        return False

    try:
        data = {
            "worker_id": worker_id,
            "queue_id": queue_id,
            "organization_id": organization_id,
            "status": status,
            "last_heartbeat": last_heartbeat,
            "tasks_processed": tasks_processed,
        }

        if system_info:
            data["system_info"] = json.dumps(system_info)

        # Cache worker status
        await client.hset(f"worker:{worker_id}:status", data)
        await client.expire(f"worker:{worker_id}:status", ttl)

        # Add to queue workers set
        await client.sadd(f"queue:{queue_id}:workers", worker_id)
        await client.expire(f"queue:{queue_id}:workers", ttl)

        logger.debug("worker_heartbeat_cached", worker_id=worker_id[:8])
        return True

    except Exception as e:
        logger.error("cache_worker_heartbeat_failed", error=str(e), worker_id=worker_id[:8])
        return False


async def cache_worker_logs(worker_id: str, logs: list, ttl: int = 300) -> bool:
    """Cache worker logs in Redis."""
    client = get_redis_client()
    if not client or not logs:
        return False

    try:
        # Add logs to list
        await client.lpush(f"worker:{worker_id}:logs", *logs)
        # Keep only last 100 logs
        await client.ltrim(f"worker:{worker_id}:logs", 0, 99)
        # Set expiry
        await client.expire(f"worker:{worker_id}:logs", ttl)

        logger.debug("worker_logs_cached", worker_id=worker_id[:8], count=len(logs))
        return True

    except Exception as e:
        logger.error("cache_worker_logs_failed", error=str(e), worker_id=worker_id[:8])
        return False


async def get_queue_worker_count_cached(queue_id: str) -> Optional[int]:
    """Get active worker count for queue from cache."""
    client = get_redis_client()
    if not client:
        return None

    try:
        count = await client.scard(f"queue:{queue_id}:workers")
        return count
    except Exception as e:
        logger.error("get_queue_worker_count_failed", error=str(e), queue_id=queue_id[:8])
        return None
