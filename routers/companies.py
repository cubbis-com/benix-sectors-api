"""
Company Analysis & Fundamental Reports Router.
"""
from typing import Optional
from fastapi import APIRouter, Query, Path
from core.sectors_client import sectors_client, normalize_ticker
from config import settings

router = APIRouter(prefix="/companies", tags=["Companies & Reports"])

@router.get("/{symbol}", summary="Company Report (Comprehensive)")
async def get_company_report(
    symbol: str = Path(..., description="IDX stock symbol e.g. BBCA, TLKM"),
    sections: Optional[str] = Query(
        None,
        description="Comma-separated sections: overview, valuation, future, peers, financials, dividend, management, ownership. If omitted, all sections returned."
    ),
    bypass_cache: bool = Query(False)
):
    """
    Returns comprehensive company report.
    Use 'sections' to filter specific aspects and minimize payload size.
    """
    clean_sym = normalize_ticker(symbol)
    endpoint = f"/company/report/{clean_sym}/"
    params = {"sections": sections} if sections else None
    return await sectors_client.get(
        endpoint,
        params=params,
        ttl_seconds=settings.CACHE_TTL_REPORTS,
        bypass_cache=bypass_cache
    )

@router.get("/{symbol}/quarterly", summary="Company Quarterly Financials")
async def get_quarterly_financials(
    symbol: str = Path(..., description="IDX ticker e.g. BBCA, BMRI"),
    n_quarters: Optional[int] = Query(4, ge=1, le=20, description="Number of recent quarters"),
    report_date: Optional[str] = Query(None, description="Specific report date YYYY-MM-DD"),
    bypass_cache: bool = Query(False)
):
    """
    Returns income statement and balance sheet quarterly metrics.
    Financial sector companies include net_interest_income, gross_loan, total_deposit.
    """
    clean_sym = normalize_ticker(symbol)
    endpoint = f"/financials/quarterly/{clean_sym}/"
    params = {"n_quarters": n_quarters, "report_date": report_date}
    return await sectors_client.get(
        endpoint,
        params=params,
        ttl_seconds=settings.CACHE_TTL_REPORTS,
        bypass_cache=bypass_cache
    )

@router.get("/{symbol}/segments", summary="Company Revenue Segments")
async def get_company_segments(
    symbol: str = Path(..., description="IDX ticker e.g. ASII, UNVR"),
    year: Optional[int] = Query(None, description="Financial year e.g. 2024"),
    bypass_cache: bool = Query(False)
):
    """
    Returns Sankey-graph-ready revenue and cost breakdown.
    """
    clean_sym = normalize_ticker(symbol)
    endpoint = f"/company/get-segments/{clean_sym}/"
    params = {"year": year} if year else None
    return await sectors_client.get(
        endpoint,
        params=params,
        ttl_seconds=settings.CACHE_TTL_REPORTS,
        bypass_cache=bypass_cache
    )

@router.get("/{symbol}/shareholders", summary="Shareholders Composition")
async def get_shareholders(
    symbol: str = Path(..., description="IDX ticker e.g. BBCA"),
    year: Optional[int] = Query(None, description="Year e.g. 2024"),
    bypass_cache: bool = Query(False)
):
    """
    Returns breakdown of local vs foreign institutional and retail shareholders.
    """
    clean_sym = normalize_ticker(symbol)
    endpoint = f"/company/shareholders-composition/{clean_sym}/"
    params = {"year": year} if year else None
    return await sectors_client.get(
        endpoint,
        params=params,
        ttl_seconds=settings.CACHE_TTL_REPORTS,
        bypass_cache=bypass_cache
    )

@router.get("/{symbol}/corporate-actions", summary="Corporate Actions History")
async def get_corporate_actions(
    symbol: str = Path(..., description="IDX ticker e.g. BBCA"),
    bypass_cache: bool = Query(False)
):
    """
    Returns splits, rights, dividends, bonus shares, warrants, and AGM records for an emiten.
    """
    clean_sym = normalize_ticker(symbol)
    endpoint = f"/company/corporate-actions/{clean_sym}/"
    return await sectors_client.get(
        endpoint,
        ttl_seconds=settings.CACHE_TTL_REPORTS,
        bypass_cache=bypass_cache
    )

@router.get("/{symbol}/ipo", summary="IPO & Listing Performance")
async def get_listing_performance(
    symbol: str = Path(..., description="IDX ticker e.g. GOTO, BREN"),
    bypass_cache: bool = Query(False)
):
    """
    Returns percentage gain/loss since IPO listing across 7d, 30d, 90d, 365d windows.
    """
    clean_sym = normalize_ticker(symbol)
    endpoint = f"/listing-performance/{clean_sym}/"
    return await sectors_client.get(
        endpoint,
        ttl_seconds=settings.CACHE_TTL_REPORTS,
        bypass_cache=bypass_cache
    )

@router.get("/subsectors/{sub_sector}/report", summary="Subsector Comprehensive Report")
async def get_subsector_report(
    sub_sector: str = Path(..., description="Subsector slug e.g. banks, renewable-energy"),
    sections: Optional[str] = Query(None, description="Sections filter"),
    bypass_cache: bool = Query(False)
):
    """
    Returns aggregated metrics, market caps, valuation, and constituent companies for an IDX subsector.
    """
    endpoint = f"/subsector/report/{sub_sector.lower()}/"
    params = {"sections": sections} if sections else None
    return await sectors_client.get(
        endpoint,
        params=params,
        ttl_seconds=settings.CACHE_TTL_REPORTS,
        bypass_cache=bypass_cache
    )

@router.get("/sector/{sector}/report", summary="Sector Comprehensive Report")
async def get_sector_report(
    sector: str = Path(..., description="Sector or subsector slug e.g. financials, energy, banks"),
    sections: Optional[str] = Query(None),
    bypass_cache: bool = Query(False)
):
    endpoint = f"/subsector/report/{sector.lower()}/"
    params = {"sections": sections} if sections else None
    return await sectors_client.get(
        endpoint,
        params=params,
        ttl_seconds=settings.CACHE_TTL_REPORTS,
        bypass_cache=bypass_cache
    )

@router.get("/ipo/listing-performance", summary="Universe IPO Listing Performance")
async def get_universe_listing_performance(
    symbol: Optional[str] = Query(None, description="Optional emiten symbol"),
    bypass_cache: bool = Query(False)
):
    endpoint = f"/listing-performance/{symbol.upper()}/" if symbol else "/listing-performance/"
    return await sectors_client.get(
        endpoint,
        ttl_seconds=settings.CACHE_TTL_REPORTS,
        bypass_cache=bypass_cache
    )
