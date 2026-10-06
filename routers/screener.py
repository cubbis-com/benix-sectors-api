"""
Companies Screener Router.
Supports both structured SQL-like queries (where, order_by) and natural language queries (q).
"""
from typing import Optional
from fastapi import APIRouter, Query
from core.sectors_client import sectors_client
from config import settings

router = APIRouter(prefix="/screener", tags=["Company Screener"])

@router.get("", summary="Companies Screener")
async def screen_companies(
    where: Optional[str] = Query(None, description="SQL-like conditions e.g. sub_sector = 'banks'"),
    q: Optional[str] = Query(None, description="Natural language search e.g. top 5 banks by market cap"),
    order_by: Optional[str] = Query(None, description="Sort field e.g. -market_cap"),
    desc: Optional[bool] = Query(None, description="Sort descending flag"),
    limit: Optional[int] = Query(50, ge=1, le=200, description="Max results (max 200)"),
    offset: Optional[int] = Query(0, ge=0, description="Pagination offset"),
    include_query_values: Optional[bool] = Query(False, description="Include matched query filter values"),
    bypass_cache: bool = Query(False, description="Bypass Credit Shield cache")
):
    """
    Screener for IDX listed companies.
    - Structured queries cost 1 credit.
    - Natural language (q) queries cost 3 credits.
    - Cached requests cost 0 credits.
    """
    params = {
        "where": where,
        "q": q,
        "order_by": order_by,
        "desc": desc,
        "limit": limit,
        "offset": offset,
        "include_query_values": include_query_values
    }
    # Natural language queries have shorter TTL (1 hr), structured queries 2 hrs
    ttl = 3600 if q else 7200
    res = await sectors_client.get("/companies/", params=params, ttl_seconds=ttl, bypass_cache=bypass_cache)
    return res

@router.get("/free-float", summary="Free Float Market Analysis")
async def get_free_float(
    sector: Optional[str] = Query(None, description="Sector slug e.g. financials"),
    sub_sector: Optional[str] = Query(None, description="Subsector slug e.g. banks"),
    industry: Optional[str] = Query(None, description="Industry slug"),
    limit: Optional[int] = Query(100, ge=1, le=500),
    offset: Optional[int] = Query(0, ge=0),
    bypass_cache: bool = Query(False)
):
    """
    Returns free float percentage for IDX listed companies ordered descending.
    """
    params = {
        "sector": sector,
        "sub_sector": sub_sector,
        "industry": industry,
        "limit": limit,
        "offset": offset
    }
    res = await sectors_client.get("/free-float/", params=params, ttl_seconds=settings.CACHE_TTL_DEFAULT, bypass_cache=bypass_cache)
    return res
