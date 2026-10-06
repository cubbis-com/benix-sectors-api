"""
Broker Summary, Activity, Flow & Bandarmology Router.
"""
from typing import Optional
from fastapi import APIRouter, Query, Path
from core.sectors_client import sectors_client, normalize_ticker
from config import settings

router = APIRouter(prefix="/brokers", tags=["Brokers & Foreign Flow"])

@router.get("", summary="IDX Broker Registry")
async def get_broker_registry(
    origin: Optional[str] = Query(None, description="foreign or domestic"),
    cohort: Optional[str] = Query(None, description="retail, institutional, mixed, unknown"),
    bypass_cache: bool = Query(False)
):
    """
    Curated registry of IDX exchange-member brokers with code, name, origin, and cohort.
    """
    params = {"origin": origin, "cohort": cohort}
    return await sectors_client.get(
        "/brokers/",
        params=params,
        ttl_seconds=settings.CACHE_TTL_HELPERS,
        bypass_cache=bypass_cache
    )

@router.get("/top", summary="Top Brokers Daily Ranking")
async def get_top_brokers(
    date: Optional[str] = Query(None, description="Date YYYY-MM-DD"),
    metric: Optional[str] = Query("gross_trade_value", description="gross_trade_value or abs_net_flow"),
    n_brokers: Optional[int] = Query(10, ge=1, le=50),
    origin: Optional[str] = Query(None),
    cohort: Optional[str] = Query(None),
    bypass_cache: bool = Query(False)
):
    """
    Brokers ranked by gross trade value or absolute net flow.
    """
    params = {
        "date": date,
        "metric": metric,
        "n_brokers": n_brokers,
        "origin": origin,
        "cohort": cohort
    }
    return await sectors_client.get(
        "/brokers/top/",
        params=params,
        ttl_seconds=settings.CACHE_TTL_BROKERS,
        bypass_cache=bypass_cache
    )

@router.get("/foreign-flow", summary="Daily Full-Universe Foreign Flow")
async def get_foreign_flow_universe(
    date: Optional[str] = Query(None, description="Date YYYY-MM-DD"),
    page: Optional[int] = Query(1),
    bypass_cache: bool = Query(False)
):
    """
    Net foreign-investor flow of EVERY IDX ticker on a single trading day.
    """
    params = {"date": date, "page": page}
    return await sectors_client.get(
        "/foreign-flow/",
        params=params,
        ttl_seconds=settings.CACHE_TTL_BROKERS,
        bypass_cache=bypass_cache
    )

@router.get("/foreign-flow/{symbol}", summary="Daily Net Foreign Inflow for a Stock")
async def get_foreign_flow_by_symbol(
    symbol: str = Path(..., description="IDX ticker e.g. BBCA, BBRI"),
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
    bypass_cache: bool = Query(False)
):
    """
    Daily net foreign investor inflow/outflow (IDR) and foreign share percentage.
    """
    clean_sym = normalize_ticker(symbol)
    params = {"start": start, "end": end}
    return await sectors_client.get(
        f"/foreign-flow/{clean_sym}/",
        params=params,
        ttl_seconds=settings.CACHE_TTL_BROKERS,
        bypass_cache=bypass_cache
    )

@router.get("/symbol/{symbol}/summary", summary="Broker Activity Per Symbol")
async def get_broker_summary_by_symbol(
    symbol: str = Path(..., description="IDX ticker e.g. BBCA"),
    broker_code: Optional[str] = Query(None, description="Two-letter code e.g. YP, CC"),
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
    bypass_cache: bool = Query(False)
):
    """
    Daily broker trading rows for one ticker over up to 14 days.
    """
    clean_sym = normalize_ticker(symbol)
    params = {"broker_code": broker_code, "start": start, "end": end}
    return await sectors_client.get(
        f"/broker-summary/{clean_sym}/",
        params=params,
        ttl_seconds=settings.CACHE_TTL_BROKERS,
        bypass_cache=bypass_cache
    )

@router.get("/symbol/{symbol}/top", summary="Top Buyers & Sellers for a Stock")
async def get_top_buyers_sellers(
    symbol: str = Path(..., description="IDX ticker e.g. BBCA"),
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
    n_brokers: Optional[int] = Query(5, ge=1, le=20),
    bypass_cache: bool = Query(False)
):
    """
    Top accumulating and distributing brokers for a single stock over date range.
    Costs 2 credits on Sectors API (unless cached).
    """
    clean_sym = normalize_ticker(symbol)
    params = {"start": start, "end": end, "n_brokers": n_brokers}
    return await sectors_client.get(
        f"/broker-summary/{clean_sym}/top/",
        params=params,
        ttl_seconds=settings.CACHE_TTL_BROKERS,
        bypass_cache=bypass_cache
    )

@router.get("/{broker_code}/activity", summary="Broker Activity by Broker Code")
async def get_broker_activity_by_code(
    broker_code: str = Path(..., description="Two-letter broker code e.g. YP, CC, AK"),
    symbol: Optional[str] = Query(None),
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
    bypass_cache: bool = Query(False)
):
    """
    All stocks traded by a broker over up to 14 days.
    """
    clean_sym = normalize_ticker(symbol) if symbol else None
    params = {"symbol": clean_sym, "start": start, "end": end}
    return await sectors_client.get(
        f"/broker-activity/{broker_code.upper()}/",
        params=params,
        ttl_seconds=settings.CACHE_TTL_BROKERS,
        bypass_cache=bypass_cache
    )

@router.get("/{broker_code}/top", summary="Top Accumulations and Distributions by Broker")
async def get_broker_top_accumulations(
    broker_code: str = Path(..., description="Two-letter broker code e.g. YP, CC"),
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
    n_stocks: Optional[int] = Query(5, ge=1, le=20),
    bypass_cache: bool = Query(False)
):
    """
    Stocks a single broker has been most actively buying (accumulating) or selling (distributing).
    Costs 2 credits on Sectors API (unless cached).
    """
    params = {"start": start, "end": end, "n_stocks": n_stocks}
    return await sectors_client.get(
        f"/broker-activity/{broker_code.upper()}/top/",
        params=params,
        ttl_seconds=settings.CACHE_TTL_BROKERS,
        bypass_cache=bypass_cache
    )
