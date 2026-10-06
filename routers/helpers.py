"""
Helper Lists Router.
Taxonomies, sectors, industries, and tags.
These endpoints are cached for 24 hours to maximize credit efficiency.
"""
from typing import Optional
from fastapi import APIRouter, Query, Path
from core.sectors_client import sectors_client, normalize_ticker
from config import settings

router = APIRouter(prefix="/helpers", tags=["Helper Lists & Taxonomy"])

@router.get("/subsectors", summary="List All IDX Subsectors")
async def get_subsectors(bypass_cache: bool = Query(False)):
    """
    Returns all sector/subsector pairs as kebab-case slugs.
    Cached for 24 hours.
    """
    return await sectors_client.get(
        "/subsectors/",
        ttl_seconds=settings.CACHE_TTL_HELPERS,
        bypass_cache=bypass_cache
    )

@router.get("/industries", summary="List All IDX Industries")
async def get_industries(bypass_cache: bool = Query(False)):
    """
    Returns all subsector/industry pairs as kebab-case slugs.
    Cached for 24 hours.
    """
    return await sectors_client.get(
        "/industries/",
        ttl_seconds=settings.CACHE_TTL_HELPERS,
        bypass_cache=bypass_cache
    )

@router.get("/subindustries", summary="List All IDX Subindustries")
async def get_subindustries(bypass_cache: bool = Query(False)):
    """
    Returns all industry/sub-industry pairs as kebab-case slugs.
    Cached for 24 hours.
    """
    return await sectors_client.get(
        "/subindustries/",
        ttl_seconds=settings.CACHE_TTL_HELPERS,
        bypass_cache=bypass_cache
    )

@router.get("/tags", summary="List All News & Filing Tags")
async def get_tags(bypass_cache: bool = Query(False)):
    """
    Returns sorted array of tag slugs used across news and filings.
    Cached for 24 hours.
    """
    return await sectors_client.get(
        "/tags/",
        ttl_seconds=settings.CACHE_TTL_HELPERS,
        bypass_cache=bypass_cache
    )

@router.get("/companies-with-segments", summary="Companies with Revenue Segments Available")
async def get_companies_with_segments(bypass_cache: bool = Query(False)):
    """
    Returns dictionary of companies that have revenue and cost segment data.
    """
    return await sectors_client.get(
        "/companies/list_companies_with_segments/",
        ttl_seconds=settings.CACHE_TTL_HELPERS,
        bypass_cache=bypass_cache
    )

@router.get("/quarterly-dates", summary="Universe Quarterly Financial Dates")
async def get_universe_quarterly_dates(
    since: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    bypass_cache: bool = Query(False)
):
    """
    Returns the latest available quarterly report date for EVERY company.
    """
    params = {"since": since, "year": year}
    return await sectors_client.get(
        "/companies/quarterly-financial-dates/",
        params=params,
        ttl_seconds=settings.CACHE_TTL_HELPERS,
        bypass_cache=bypass_cache
    )

@router.get("/quarterly-dates/{symbol}", summary="Quarterly Financial Dates for Symbol")
async def get_symbol_quarterly_dates(
    symbol: str = Path(..., description="IDX ticker e.g. BBCA"),
    bypass_cache: bool = Query(False)
):
    """
    Returns all quarterly report dates available for a specific ticker.
    """
    clean_sym = normalize_ticker(symbol)
    return await sectors_client.get(
        f"/company/get_quarterly_financial_dates/{clean_sym}/",
        ttl_seconds=settings.CACHE_TTL_HELPERS,
        bypass_cache=bypass_cache
    )
