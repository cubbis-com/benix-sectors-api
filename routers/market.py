"""
Market Data, Indices, Movers & News Router.
"""
from typing import Optional
from fastapi import APIRouter, Query, Path
from core.sectors_client import sectors_client, normalize_ticker
from config import settings

router = APIRouter(prefix="/market", tags=["Market Data & Transactions"])

@router.get("/summary", summary="IDX Total Market Capitalization")
async def get_idx_summary(
    start: Optional[str] = Query(None, description="Start date YYYY-MM-DD (up to 90 days)"),
    end: Optional[str] = Query(None, description="End date YYYY-MM-DD"),
    bypass_cache: bool = Query(False)
):
    """
    Returns historical total IDX market capitalization.
    """
    params = {"start": start, "end": end}
    return await sectors_client.get(
        "/idx-total/",
        params=params,
        ttl_seconds=settings.CACHE_TTL_DAILY,
        bypass_cache=bypass_cache
    )

@router.get("/close", summary="Daily Full-Universe Close (All IDX Stocks)")
async def get_full_universe_close(
    date: Optional[str] = Query(None, description="Trading date YYYY-MM-DD"),
    page: Optional[int] = Query(1, ge=1),
    bypass_cache: bool = Query(False)
):
    """
    Returns closing prices for EVERY ticker on IDX in one paginated feed.
    """
    params = {"date": date, "page": page}
    return await sectors_client.get(
        "/close/",
        params=params,
        ttl_seconds=settings.CACHE_TTL_DAILY,
        bypass_cache=bypass_cache
    )

@router.get("/daily/{symbol}", summary="Daily Transaction Data per Symbol")
async def get_daily_transactions(
    symbol: str = Path(..., description="IDX ticker e.g. BBCA"),
    start: Optional[str] = Query(None, description="Start date YYYY-MM-DD"),
    end: Optional[str] = Query(None, description="End date YYYY-MM-DD"),
    bypass_cache: bool = Query(False)
):
    """
    Returns daily close price, volume, and market cap over a date range (up to 90 days).
    """
    clean_sym = normalize_ticker(symbol)
    params = {"start": start, "end": end}
    return await sectors_client.get(
        f"/daily/{clean_sym}/",
        params=params,
        ttl_seconds=settings.CACHE_TTL_DAILY,
        bypass_cache=bypass_cache
    )

@router.get("/transaction/daily/{symbol}", summary="Daily Market Transactions Alias", include_in_schema=False)
async def get_daily_transactions_alias(
    symbol: str = Path(..., description="IDX ticker e.g. BBCA"),
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
    bypass_cache: bool = Query(False)
):
    return await get_daily_transactions(symbol=symbol, start=start, end=end, bypass_cache=bypass_cache)

@router.get("/top-movers", summary="Top Gainers & Losers")
async def get_top_movers(
    classifications: Optional[str] = Query(
        "top_gainers",
        description="Classification: top_gainers or top_losers"
    ),
    periods: Optional[str] = Query(
        "1d",
        description="Period: 1d, 7d, 14d, 30d, 365d"
    ),
    sub_sector: Optional[str] = Query(None, description="Filter by subsector slug e.g. banks"),
    n_stock: Optional[int] = Query(10, ge=1, le=50, description="Number of stocks to return"),
    bypass_cache: bool = Query(False)
):
    """
    Returns top gainers or losers across specified periods.
    """
    params = {
        "classifications": classifications,
        "periods": periods,
        "sub_sector": sub_sector,
        "n_stock": n_stock
    }
    return await sectors_client.get(
        "/companies/top-changes/",
        params=params,
        ttl_seconds=1800,  # 30 mins
        bypass_cache=bypass_cache
    )

@router.get("/most-traded", summary="Most Traded Stocks (By Volume)")
async def get_most_traded(
    start: Optional[str] = Query(None, description="Start date YYYY-MM-DD"),
    end: Optional[str] = Query(None, description="End date YYYY-MM-DD"),
    n_stock: Optional[int] = Query(10, ge=1, le=50),
    sub_sector: Optional[str] = Query(None),
    bypass_cache: bool = Query(False)
):
    """
    Returns most traded IDX stocks by transaction volume over a date range.
    """
    params = {
        "start": start,
        "end": end,
        "n_stock": n_stock,
        "sub_sector": sub_sector
    }
    return await sectors_client.get(
        "/most-traded/",
        params=params,
        ttl_seconds=1800,
        bypass_cache=bypass_cache
    )

@router.get("/ranking/most-traded", summary="Top Traded Company Rankings Alias", include_in_schema=False)
async def get_ranking_most_traded(
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
    n_stock: Optional[int] = Query(10, ge=1, le=50),
    sub_sector: Optional[str] = Query(None),
    bypass_cache: bool = Query(False)
):
    return await get_most_traded(start=start, end=end, n_stock=n_stock, sub_sector=sub_sector, bypass_cache=bypass_cache)

@router.get("/indices", summary="Daily Full-Universe Index Close")
async def get_all_indices_close(
    date: Optional[str] = Query(None, description="Trading date YYYY-MM-DD"),
    bypass_cache: bool = Query(False)
):
    """
    Returns closing levels of EVERY index (IHSG, LQ45, IDX30, etc.) on a single trading day.
    """
    params = {"date": date}
    return await sectors_client.get(
        "/index-daily/",
        params=params,
        ttl_seconds=settings.CACHE_TTL_DAILY,
        bypass_cache=bypass_cache
    )

@router.get("/indices/{index_code}", summary="Index Daily Transaction History")
async def get_index_daily(
    index_code: str = Path(..., description="Index code e.g. idx30, lq45, composite"),
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
    bypass_cache: bool = Query(False)
):
    """
    Returns historical daily closing levels for an index over up to 90 days.
    """
    params = {"start": start, "end": end}
    return await sectors_client.get(
        f"/index-daily/{index_code.lower()}/",
        params=params,
        ttl_seconds=settings.CACHE_TTL_DAILY,
        bypass_cache=bypass_cache
    )

@router.get("/news", summary="Financial & Market News")
async def get_news(
    extension: Optional[str] = Query("idx", description="News extension: 'idx' or 'mining'"),
    sector: Optional[str] = Query(None),
    sub_sector: Optional[str] = Query(None),
    symbols: Optional[str] = Query(None, description="Comma-separated tickers"),
    tags: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    page: Optional[int] = Query(1),
    bypass_cache: bool = Query(False)
):
    """
    Paginated financial news articles from IDX or mining sources.
    """
    params = {
        "extension": extension,
        "sector": sector,
        "sub_sector": sub_sector,
        "symbols": symbols,
        "tags": tags,
        "keyword": keyword,
        "page": page
    }
    return await sectors_client.get(
        "/news/",
        params=params,
        ttl_seconds=3600,
        bypass_cache=bypass_cache
    )

@router.get("/filings", summary="Insider Filings & Transactions")
async def get_filings(
    symbol: Optional[str] = Query(None),
    sector: Optional[str] = Query(None),
    sub_sector: Optional[str] = Query(None),
    tags: Optional[str] = Query(None),
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
    bypass_cache: bool = Query(False)
):
    """
    Returns insider trading filings (buy/sell by directors and major shareholders).
    """
    clean_sym = normalize_ticker(symbol) if symbol else None
    params = {
        "symbol": clean_sym,
        "sector": sector,
        "sub_sector": sub_sector,
        "tags": tags,
        "start": start,
        "end": end
    }
    return await sectors_client.get(
        "/filings/",
        params=params,
        ttl_seconds=3600,
        bypass_cache=bypass_cache
    )

@router.get("/suspensions", summary="Historical Stock Suspensions")
async def get_suspensions(
    symbol: Optional[str] = Query(None),
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
    bypass_cache: bool = Query(False)
):
    """
    Returns historical stock suspensions with official IDX reasons.
    """
    clean_sym = normalize_ticker(symbol) if symbol else None
    params = {"symbol": clean_sym, "start": start, "end": end}
    return await sectors_client.get(
        "/suspensions/",
        params=params,
        ttl_seconds=settings.CACHE_TTL_DAILY,
        bypass_cache=bypass_cache
    )
