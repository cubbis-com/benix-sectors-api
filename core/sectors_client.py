"""
Asynchronous HTTP Client for Sectors Financial API v2.
Includes ticker normalization, smart caching (Credit Shield), and audit logging.
"""
import time
import logging
from typing import Optional, Dict, Any
import httpx
from config import settings
from core.cache import cache_manager, make_cache_key
from core.credits_tracker import credits_tracker

logger = logging.getLogger("sectors.client")

def normalize_ticker(ticker: str) -> str:
    """Normalize ticker symbol: e.g., 'bbca.jk' -> 'BBCA', 'd05.si' -> 'D05'."""
    if not ticker:
        return ""
    t = ticker.strip().upper()
    if t.endswith(".JK"):
        t = t[:-3]
    elif t.endswith(".SI"):
        t = t[:-3]
    return t

class SectorsClient:
    def __init__(self):
        self.base_url = settings.SECTORS_BASE_URL.rstrip("/")
        self.api_key = settings.SECTORS_API_KEY
        self.user_agent = settings.USER_AGENT
        self.timeout = settings.REQUEST_TIMEOUT_SECONDS

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": self.api_key,
            "User-Agent": self.user_agent,
            "Accept": "application/json"
        }

    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        ttl_seconds: int = settings.CACHE_TTL_DEFAULT,
        bypass_cache: bool = False
    ) -> Dict[str, Any]:
        """
        Execute GET request to Sectors API v2 with caching and credit tracking.
        Returns response wrapped with metadata (_meta).
        """
        endpoint_clean = endpoint if endpoint.startswith("/") else f"/{endpoint}"
        cache_key = make_cache_key(endpoint_clean, params)

        # 1. Check Credit Shield Cache
        if not bypass_cache:
            cached_data = await cache_manager.get(cache_key)
            if cached_data is not None:
                await credits_tracker.log_call(
                    endpoint=endpoint_clean,
                    params=params,
                    status_code=200,
                    from_cache=True,
                    duration_ms=0.5
                )
                logger.info("⚡ [CACHE HIT] %s - 0 credits billed", cache_key)
                return {
                    "data": cached_data,
                    "_meta": {
                        "source": "cache",
                        "credits_consumed": 0,
                        "cache_key": cache_key,
                        "status": 200
                    }
                }

        # 2. Cache Miss: Execute Network Request
        url = f"{self.base_url}{endpoint_clean}"
        headers = self._get_headers()
        clean_params = {k: v for k, v in (params or {}).items() if v is not None}

        start_time = time.time()
        status_code = 500
        response_data = None
        error_msg = None

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(url, headers=headers, params=clean_params)
                status_code = resp.status_code
                duration_ms = (time.time() - start_time) * 1000

                if resp.status_code == 200:
                    response_data = resp.json()
                    # Store in cache
                    await cache_manager.set(cache_key, endpoint_clean, response_data, ttl_seconds)
                else:
                    try:
                        response_data = resp.json()
                    except Exception:
                        response_data = {"raw_text": resp.text}
                    error_msg = f"Sectors API returned HTTP {resp.status_code}"

        except httpx.TimeoutException:
            duration_ms = (time.time() - start_time) * 1000
            status_code = 504
            error_msg = "Sectors API request timed out"
            response_data = {"error": "GATEWAY_TIMEOUT", "message": error_msg}
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            status_code = 500
            error_msg = str(e)
            response_data = {"error": "INTERNAL_CLIENT_ERROR", "message": error_msg}

        # 3. Log credit expenditure
        credits_billed = await credits_tracker.log_call(
            endpoint=endpoint_clean,
            params=clean_params,
            status_code=status_code,
            from_cache=False,
            duration_ms=duration_ms
        )

        logger.info(
            "🌐 [NETWORK CALL] %s -> HTTP %d (%s credits, %.1f ms)",
            endpoint_clean, status_code, credits_billed, duration_ms
        )

        return {
            "data": response_data,
            "error": error_msg,
            "_meta": {
                "source": "network",
                "credits_consumed": credits_billed,
                "latency_ms": round(duration_ms, 2),
                "status": status_code,
                "endpoint": endpoint_clean
            }
        }

sectors_client = SectorsClient()
