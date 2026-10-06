"""
Credit & Quota Audit Tracker.
Logs credit expenditure and audit trails to monitor Sectors API credit quota.
"""
import time
import json
import logging
from typing import Optional, Dict, Any, List
from core.aiosqlite_compat import aiosqlite
from config import settings

logger = logging.getLogger("sectors.credits")

def estimate_endpoint_credits(
    endpoint: str,
    params: Optional[Dict[str, Any]] = None,
    status_code: int = 200,
    from_cache: bool = False
) -> int:
    """
    Calculate credit consumption based on Sectors API v2 rules:
    - Cached response: 0 credits (Shielded)
    - 400 Bad Request: 0 credits (except screener with 'q' LLM translation failure = 1 credit)
    - 401/403/429/5xx: 0 credits
    - 404 Not Found: 1 credit (lookup was performed)
    - 2xx Success:
      * Screener with ?q= (Natural Language): 3 credits
      * Top Accumulations/Distributions (top broker/symbol): 2 credits
      * Standard endpoints: 1 credit
    """
    if from_cache:
        return 0

    params = params or {}
    has_q = bool(params.get("q"))

    if status_code == 400:
        if has_q and ("companies" in endpoint):
            return 1  # LLM failure after execution charges 1 credit
        return 0

    if status_code in (401, 403, 429) or status_code >= 500:
        return 0

    if status_code == 404:
        return 1

    if 200 <= status_code < 300:
        # Check Natural Language screener
        if has_q and ("companies" in endpoint):
            return 3
        # Check top broker endpoints
        if "/top/" in endpoint or endpoint.endswith("/top"):
            return 2
        return 1

    return 1

class CreditsTracker:
    def __init__(self, db_path: str = settings.DATABASE_PATH):
        self.db_path = db_path

    async def init_db(self):
        """Create audit log table."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS credit_audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    endpoint TEXT NOT NULL,
                    params_json TEXT,
                    status_code INTEGER NOT NULL,
                    estimated_credits INTEGER NOT NULL,
                    from_cache INTEGER NOT NULL,
                    duration_ms REAL NOT NULL
                )
            """)
            await db.execute("CREATE INDEX IF NOT EXISTS idx_credit_ts ON credit_audit_logs(timestamp)")
            await db.commit()

    async def log_call(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]],
        status_code: int,
        from_cache: bool,
        duration_ms: float
    ) -> int:
        """Record an API execution and return estimated credits used."""
        credits = estimate_endpoint_credits(
            endpoint=endpoint,
            params=params,
            status_code=status_code,
            from_cache=from_cache
        )
        now = time.time()
        params_str = json.dumps(params) if params else "{}"

        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO credit_audit_logs (
                        timestamp, endpoint, params_json, status_code,
                        estimated_credits, from_cache, duration_ms
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (now, endpoint, params_str, status_code, credits, 1 if from_cache else 0, duration_ms))
                await db.commit()
        except Exception as e:
            logger.warning("Error writing credit log: %s", e)

        return credits

    async def get_summary(self) -> Dict[str, Any]:
        """Get aggregate metrics on credits used vs credits saved."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Total actual credits billed
                async with db.execute("""
                    SELECT 
                        COUNT(*),
                        SUM(CASE WHEN from_cache = 0 THEN estimated_credits ELSE 0 END),
                        SUM(CASE WHEN from_cache = 1 THEN 1 ELSE 0 END),
                        SUM(CASE WHEN from_cache = 1 THEN 1 ELSE 0 END) * 1.0 / MAX(COUNT(*), 1)
                    FROM credit_audit_logs
                """) as cur:
                    row = await cur.fetchone()
                    total_requests = row[0] or 0
                    credits_consumed = row[1] or 0
                    cache_hits = row[2] or 0
                    cache_hit_rate = round((row[3] or 0.0) * 100, 2)

                # Recent logs
                recent_logs: List[Dict[str, Any]] = []
                async with db.execute("""
                    SELECT id, timestamp, endpoint, status_code, estimated_credits, from_cache, duration_ms
                    FROM credit_audit_logs
                    ORDER BY id DESC LIMIT 10
                """) as cur:
                    async for r in cur:
                        recent_logs.append({
                            "id": r[0],
                            "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(r[1])),
                            "endpoint": r[2],
                            "status": r[3],
                            "credits": r[4],
                            "cached": bool(r[5]),
                            "latency_ms": round(r[6], 1)
                        })

                return {
                    "total_gateway_requests": total_requests,
                    "estimated_credits_consumed": credits_consumed,
                    "credits_saved_by_cache": cache_hits,
                    "cache_hit_ratio_percent": cache_hit_rate,
                    "recent_audit_trail": recent_logs
                }
        except Exception as e:
            logger.error("Error generating credit summary: %s", e)
            return {"error": str(e)}

credits_tracker = CreditsTracker()
