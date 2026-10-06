"""
System Metrics & Credit Shield Health Router.
"""
from fastapi import APIRouter
from core.credits_tracker import credits_tracker
from core.cache import cache_manager
from config import settings

router = APIRouter(tags=["Metrics & Health"])

@router.get("/metrics/credits", summary="Credit Shield & Quota Audit Dashboard")
async def get_credit_metrics():
    """
    Returns real-time analytics on Sectors API credit expenditure,
    cache hit ratio, estimated credits saved, and recent audit logs.
    """
    credit_summary = await credits_tracker.get_summary()
    cache_stats = await cache_manager.get_stats()

    return {
        "status": "active",
        "credit_shield": {
            "total_requests": credit_summary.get("total_gateway_requests", 0),
            "credits_consumed": credit_summary.get("estimated_credits_consumed", 0),
            "credits_saved_by_cache": credit_summary.get("credits_saved_by_cache", 0),
            "cache_hit_rate": f"{credit_summary.get('cache_hit_ratio_percent', 0)}%",
            "active_cached_keys": cache_stats.get("active_cached_keys", 0)
        },
        "recent_audit_trail": credit_summary.get("recent_audit_trail", [])
    }

@router.get("/health", summary="Middleware Health Check")
async def health_check():
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "sectors_base_url": settings.SECTORS_BASE_URL,
        "sectors_mcp_url": settings.SECTORS_MCP_URL
    }
