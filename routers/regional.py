"""
Regional Markets Router (Singapore SGX & Malaysia KLSE).
"""
from typing import Optional
from fastapi import APIRouter, Query, Path
from core.sectors_client import sectors_client, normalize_ticker
from config import settings

router = APIRouter(prefix="/regional", tags=["Regional Markets (SGX & KLSE)"])

# ==================== SINGAPORE (SGX) ====================

@router.get("/sgx/companies", summary="SGX Companies Screener")
async def screen_sgx_companies(
    where: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    order_by: Optional[str] = Query(None),
    limit: Optional[int] = Query(50),
    offset: Optional[int] = Query(0),
    bypass_cache: bool = Query(False)
):
    """
    Screener for SGX listed companies (e.g. D05, U11, Z74).
    """
    params = {"where": where, "q": q, "order_by": order_by, "limit": limit, "offset": offset}
    ttl = 3600 if q else 7200
    return await sectors_client.get(
        "/sgx/companies/",
        params=params,
        ttl_seconds=ttl,
        bypass_cache=bypass_cache
    )

@router.get("/sgx/company/{symbol}", summary="SGX Company Full Report")
async def get_sgx_company_report(
    symbol: str = Path(..., description="SGX ticker e.g. D05, U11"),
    sections: Optional[str] = Query(None),
    bypass_cache: bool = Query(False)
):
    """
    Comprehensive report for SGX listed company.
    """
    clean_sym = normalize_ticker(symbol)
    params = {"sections": sections} if sections else None
    return await sectors_client.get(
        f"/sgx/company/report/{clean_sym}/",
        params=params,
        ttl_seconds=settings.CACHE_TTL_REPORTS,
        bypass_cache=bypass_cache
    )

@router.get("/sgx/sectors", summary="List All SGX Sectors")
async def get_sgx_sectors(bypass_cache: bool = Query(False)):
    return await sectors_client.get(
        "/sgx/sectors/",
        ttl_seconds=settings.CACHE_TTL_HELPERS,
        bypass_cache=bypass_cache
    )

@router.get("/sgx/subsectors", summary="List All SGX Subsectors")
async def get_sgx_subsectors(bypass_cache: bool = Query(False)):
    return await sectors_client.get(
        "/sgx/subsectors/",
        ttl_seconds=settings.CACHE_TTL_HELPERS,
        bypass_cache=bypass_cache
    )

@router.get("/sgx/top", summary="Top SGX Companies Ranking")
async def get_top_sgx_companies(
    classifications: Optional[str] = Query("dividend_yield", description="dividend_yield, revenue, earnings, market_cap, pe"),
    sector: Optional[str] = Query(None),
    bypass_cache: bool = Query(False)
):
    params = {"classifications": classifications, "sector": sector}
    return await sectors_client.get(
        "/sgx/companies/top/",
        params=params,
        ttl_seconds=settings.CACHE_TTL_DAILY,
        bypass_cache=bypass_cache
    )

@router.get("/sgx/daily/{symbol}", summary="SGX Daily Price Data")
async def get_sgx_daily(
    symbol: str = Path(..., description="SGX ticker e.g. D05"),
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
    bypass_cache: bool = Query(False)
):
    clean_sym = normalize_ticker(symbol)
    params = {"start": start, "end": end}
    return await sectors_client.get(
        f"/sgx/daily/{clean_sym}/",
        params=params,
        ttl_seconds=settings.CACHE_TTL_DAILY,
        bypass_cache=bypass_cache
    )

@router.get("/sgx/buybacks", summary="SGX Share Buybacks")
async def get_sgx_buybacks(
    symbol: Optional[str] = Query(None),
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
    bypass_cache: bool = Query(False)
):
    clean_sym = normalize_ticker(symbol) if symbol else None
    params = {"symbol": clean_sym, "start": start, "end": end}
    return await sectors_client.get(
        "/sgx/buybacks/",
        params=params,
        ttl_seconds=settings.CACHE_TTL_DAILY,
        bypass_cache=bypass_cache
    )

@router.get("/sgx/short-sell", summary="SGX Short Sell Data")
async def get_sgx_short_sell(
    symbol: Optional[str] = Query(None),
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
    order_by: Optional[str] = Query(None),
    bypass_cache: bool = Query(False)
):
    clean_sym = normalize_ticker(symbol) if symbol else None
    params = {"symbol": clean_sym, "start": start, "end": end, "order_by": order_by}
    return await sectors_client.get(
        "/sgx/short-sell/",
        params=params,
        ttl_seconds=settings.CACHE_TTL_DAILY,
        bypass_cache=bypass_cache
    )

# ==================== MALAYSIA (KLSE) ====================

@router.get("/klse/sectors", summary="List All KLSE Sectors")
async def get_klse_sectors(bypass_cache: bool = Query(False)):
    return await sectors_client.get(
        "/klse/sectors/",
        ttl_seconds=settings.CACHE_TTL_HELPERS,
        bypass_cache=bypass_cache
    )

@router.get("/klse/companies", summary="List KLSE Companies by Sector")
async def get_klse_companies_by_sector(
    sector: str = Query(..., description="KLSE sector slug e.g. financial-services"),
    bypass_cache: bool = Query(False)
):
    params = {"sector": sector}
    return await sectors_client.get(
        "/klse/companies/",
        params=params,
        ttl_seconds=settings.CACHE_TTL_HELPERS,
        bypass_cache=bypass_cache
    )

@router.get("/klse/top", summary="Top KLSE Companies Ranking")
async def get_top_klse_companies(
    classifications: Optional[str] = Query("market_cap"),
    sector: Optional[str] = Query(None),
    bypass_cache: bool = Query(False)
):
    params = {"classifications": classifications, "sector": sector}
    return await sectors_client.get(
        "/klse/companies/top/",
        params=params,
        ttl_seconds=settings.CACHE_TTL_DAILY,
        bypass_cache=bypass_cache
    )

@router.get("/klse/company/{symbol}", summary="KLSE Company Full Report")
async def get_klse_company_report(
    symbol: str = Path(..., description="4-digit numeric code e.g. 1155"),
    sections: Optional[str] = Query(None),
    bypass_cache: bool = Query(False)
):
    params = {"sections": sections} if sections else None
    return await sectors_client.get(
        f"/klse/company/report/{symbol}/",
        params=params,
        ttl_seconds=settings.CACHE_TTL_REPORTS,
        bypass_cache=bypass_cache
    )
