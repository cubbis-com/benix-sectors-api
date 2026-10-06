"""
Credit Shield Caching Layer (SQLite Async).
Prevents repeated API calls to Sectors, saving limited credits/quota.
"""
import time
import json
import logging
from typing import Optional, Any, Dict
from core.aiosqlite_compat import aiosqlite
from config import settings

logger = logging.getLogger("sectors.cache")

def make_cache_key(endpoint: str, params: Optional[Dict[str, Any]] = None) -> str:
    """Generate a consistent cache key from endpoint and sorted query params."""
    endpoint_clean = endpoint.strip("/")
    if not params:
        return endpoint_clean
    sorted_items = sorted([(k, str(v)) for k, v in params.items() if v is not None])
    query_str = "&".join(f"{k}={v}" for k, v in sorted_items)
    return f"{endpoint_clean}?{query_str}" if query_str else endpoint_clean

class CacheManager:
    def __init__(self, db_path: str = settings.DATABASE_PATH):
        self.db_path = db_path

    async def init_db(self):
        """Create cache table if not exists."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS api_cache (
                    cache_key TEXT PRIMARY KEY,
                    endpoint TEXT NOT NULL,
                    data_json TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    expires_at REAL NOT NULL,
                    hit_count INTEGER DEFAULT 0
                )
            """)
            await db.execute("CREATE INDEX IF NOT EXISTS idx_cache_expires ON api_cache(expires_at)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_cache_endpoint ON api_cache(endpoint)")
            await db.commit()
            logger.info("Cache database initialized at %s", self.db_path)

    async def get(self, cache_key: str) -> Optional[Any]:
        """Retrieve unexpired cached data."""
        now = time.time()
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute(
                    "SELECT data_json, expires_at FROM api_cache WHERE cache_key = ?",
                    (cache_key,)
                ) as cursor:
                    row = await cursor.fetchone()
                    if not row:
                        return None
                    data_json, expires_at = row
                    if expires_at <= now:
                        # Entry expired: delete asynchronously
                        await db.execute("DELETE FROM api_cache WHERE cache_key = ?", (cache_key,))
                        await db.commit()
                        return None
                    # Update hit count
                    await db.execute(
                        "UPDATE api_cache SET hit_count = hit_count + 1 WHERE cache_key = ?",
                        (cache_key,)
                    )
                    await db.commit()
                    return json.loads(data_json)
        except Exception as e:
            logger.warning("Cache get error for key %s: %s", cache_key, e)
            return None

    async def set(self, cache_key: str, endpoint: str, data: Any, ttl_seconds: int):
        """Save data to cache with specific TTL."""
        now = time.time()
        expires_at = now + ttl_seconds
        data_json = json.dumps(data)
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO api_cache (cache_key, endpoint, data_json, created_at, expires_at, hit_count)
                    VALUES (?, ?, ?, ?, ?, 0)
                    ON CONFLICT(cache_key) DO UPDATE SET
                        data_json = excluded.data_json,
                        created_at = excluded.created_at,
                        expires_at = excluded.expires_at
                """, (cache_key, endpoint, data_json, now, expires_at))
                await db.commit()
        except Exception as e:
            logger.warning("Cache set error for key %s: %s", cache_key, e)

    async def delete(self, cache_key: str) -> bool:
        """Remove a specific cache key."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("DELETE FROM api_cache WHERE cache_key = ?", (cache_key,))
                await db.commit()
                return True
        except Exception as e:
            logger.error("Cache delete error: %s", e)
            return False

    async def clear_expired(self) -> int:
        """Delete all expired entries."""
        now = time.time()
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("DELETE FROM api_cache WHERE expires_at <= ?", (now,))
                deleted = cursor.rowcount
                await db.commit()
                return deleted
        except Exception as e:
            logger.error("Cache clear_expired error: %s", e)
            return 0

    async def get_stats(self) -> Dict[str, Any]:
        """Return cache health and usage statistics."""
        now = time.time()
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Active items
                async with db.execute("SELECT COUNT(*), SUM(hit_count) FROM api_cache WHERE expires_at > ?", (now,)) as cur:
                    row = await cur.fetchone()
                    active_items = row[0] or 0
                    total_hits = row[1] or 0

                # Expired items
                async with db.execute("SELECT COUNT(*) FROM api_cache WHERE expires_at <= ?", (now,)) as cur:
                    row = await cur.fetchone()
                    expired_items = row[0] or 0

                return {
                    "active_cached_keys": active_items,
                    "expired_keys": expired_items,
                    "total_cache_hits": total_hits,
                    "estimated_credits_saved": total_hits,  # Minimum 1 credit per hit saved!
                }
        except Exception as e:
            logger.error("Cache get_stats error: %s", e)
            return {"error": str(e)}

cache_manager = CacheManager()
