"""
Indonesian Mining Sector Extension Router.
Covers commodities, operational sites, production, reserves, and concessions.
"""
from typing import Optional
from fastapi import APIRouter, Query, Path
from core.sectors_client import sectors_client
from config import settings

router = APIRouter(prefix="/mining", tags=["Mining Sector (Extension)"])

@router.get("/companies", summary="List Mining Companies")
async def list_mining_companies(
    keyword: Optional[str] = Query(None),
    commodity_type: Optional[str] = Query(None),
    company_type: Optional[str] = Query(None),
    bypass_cache: bool = Query(False)
):
    params = {"keyword": keyword, "commodity_type": commodity_type, "company_type": company_type}
    return await sectors_client.get(
        "/mining/companies/",
        params=params,
        ttl_seconds=settings.CACHE_TTL_HELPERS,
        bypass_cache=bypass_cache
    )

@router.get("/companies/{slug}", summary="Mining Company Operational Detail")
async def get_mining_company_detail(
    slug: str = Path(..., description="Mining company slug e.g. pt-vale-indonesia-tbk"),
    bypass_cache: bool = Query(False)
):
    return await sectors_client.get(
        f"/mining/companies/{slug}/",
        ttl_seconds=settings.CACHE_TTL_REPORTS,
        bypass_cache=bypass_cache
    )

@router.get("/companies/{slug}/financials", summary="Mining Company Financials (USD M)")
async def get_mining_financials(
    slug: str = Path(...),
    year: Optional[int] = Query(None),
    bypass_cache: bool = Query(False)
):
    params = {"year": year} if year else None
    return await sectors_client.get(
        f"/mining/companies/financials/{slug}/",
        params=params,
        ttl_seconds=settings.CACHE_TTL_REPORTS,
        bypass_cache=bypass_cache
    )

@router.get("/companies/{slug}/performance", summary="Mining Company Production & Performance")
async def get_mining_performance(
    slug: str = Path(...),
    commodity_type: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    bypass_cache: bool = Query(False)
):
    params = {"commodity_type": commodity_type, "year": year}
    return await sectors_client.get(
        f"/mining/companies/performance/{slug}/",
        params=params,
        ttl_seconds=settings.CACHE_TTL_REPORTS,
        bypass_cache=bypass_cache
    )

@router.get("/commodities", summary="List All Mining Commodities")
async def list_commodities(bypass_cache: bool = Query(False)):
    return await sectors_client.get(
        "/mining/commodities/",
        ttl_seconds=settings.CACHE_TTL_HELPERS,
        bypass_cache=bypass_cache
    )

@router.get("/commodities/{commodity_name}/price", summary="Commodity Price History")
async def get_commodity_price_history(
    commodity_name: str = Path(..., description="e.g. coal, nickel, gold, copper"),
    start_year: Optional[int] = Query(None),
    end_year: Optional[int] = Query(None),
    bypass_cache: bool = Query(False)
):
    params = {"start_year": start_year, "end_year": end_year}
    return await sectors_client.get(
        f"/mining/commodities/{commodity_name.lower()}/price/",
        params=params,
        ttl_seconds=settings.CACHE_TTL_DAILY,
        bypass_cache=bypass_cache
    )

@router.get("/sites", summary="List Mining Sites")
async def list_mining_sites(
    commodity_type: Optional[str] = Query(None),
    province: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    min_production: Optional[float] = Query(None),
    bypass_cache: bool = Query(False)
):
    params = {
        "commodity_type": commodity_type,
        "province": province,
        "year": year,
        "min_production": min_production
    }
    return await sectors_client.get(
        "/mining/sites/",
        params=params,
        ttl_seconds=settings.CACHE_TTL_HELPERS,
        bypass_cache=bypass_cache
    )

@router.get("/total-production", summary="Total National Commodity Production")
async def get_total_production(
    commodity_type: str = Query(..., description="e.g. coal, nickel"),
    bypass_cache: bool = Query(False)
):
    params = {"commodity_type": commodity_type}
    return await sectors_client.get(
        "/mining/total-production/",
        params=params,
        ttl_seconds=settings.CACHE_TTL_DAILY,
        bypass_cache=bypass_cache
    )

@router.get("/global-commodity", summary="Global Commodity Worldwide Statistics")
async def get_global_commodity_data(
    commodity: Optional[str] = Query(None, description="e.g. nickel, coal, bauxite, copper, tin"),
    bypass_cache: bool = Query(False)
):
    params = {"commodity": commodity} if commodity else None
    return await sectors_client.get(
        "/mining/global-commodity/",
        params=params,
        ttl_seconds=settings.CACHE_TTL_DAILY,
        bypass_cache=bypass_cache
    )

@router.get("/sales-destination/{slug}", summary="Mining Company Sales by Destination")
async def get_company_sales_destinations(
    slug: str = Path(..., description="Mining emiten slug e.g. pt-vale-indonesia-tbk, pt-adaro-energy-indonesia-tbk"),
    bypass_cache: bool = Query(False)
):
    return await sectors_client.get(
        f"/mining/sales-destination/{slug}/",
        ttl_seconds=settings.CACHE_TTL_REPORTS,
        bypass_cache=bypass_cache
    )

@router.get("/exports", summary="Top Export Destinations for Commodities")
async def get_commodity_exports(
    commodity: Optional[str] = Query(None, description="e.g. coal, nickel"),
    bypass_cache: bool = Query(False)
):
    params = {"commodity": commodity} if commodity else None
    return await sectors_client.get(
        "/mining/exports/",
        params=params,
        ttl_seconds=settings.CACHE_TTL_DAILY,
        bypass_cache=bypass_cache
    )

@router.get("/license-auctions", summary="Mining License Auctions & Rights (WIUPK)")
async def get_mining_license_auctions(
    commodity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    bypass_cache: bool = Query(False)
):
    params = {"commodity": commodity, "status": status}
    return await sectors_client.get(
        "/mining/license-auctions/",
        params=params,
        ttl_seconds=settings.CACHE_TTL_DAILY,
        bypass_cache=bypass_cache
    )

@router.get("/license-auctions/{wiup_code}", summary="Mining License Auction Detail")
async def get_mining_license_auction_detail(
    wiup_code: str = Path(..., description="WIUP auction code"),
    bypass_cache: bool = Query(False)
):
    return await sectors_client.get(
        f"/mining/license-auctions/{wiup_code}/",
        ttl_seconds=settings.CACHE_TTL_DAILY,
        bypass_cache=bypass_cache
    )

@router.get("/resources-reserves", summary="Mining Resources & Reserves Index")
async def get_resources_reserves(
    commodity: Optional[str] = Query(None),
    bypass_cache: bool = Query(False)
):
    params = {"commodity": commodity} if commodity else None
    return await sectors_client.get(
        "/mining/resources-reserves/",
        params=params,
        ttl_seconds=settings.CACHE_TTL_HELPERS,
        bypass_cache=bypass_cache
    )
