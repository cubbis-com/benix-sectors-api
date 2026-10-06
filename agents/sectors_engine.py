"""
Sectors API Data Skills Engine.
Executes targeted, credit-conscious data queries across Sectors Financial API v2.
"""
from typing import Dict, Any, List, Optional
from core.sectors_client import sectors_client, normalize_ticker
from config import settings

class SectorsDataEngine:
    """Specialized engine for fetching and aggregating financial data from Sectors API."""

    @staticmethod
    async def fetch_stock_deepdive(symbol: str) -> Dict[str, Any]:
        """
        Gathers comprehensive data for a single stock:
        - Company Overview & Valuation & Dividend (via /company/report/{symbol}/)
        - Net Foreign Flow (via /foreign-flow/{symbol}/)
        - Top Brokers accumulation (via /broker-summary/{symbol}/top/)
        """
        clean_sym = normalize_ticker(symbol)

        # 1. Company Report (Sections: overview, valuation, dividend, peers)
        report_res = await sectors_client.get(
            f"/company/report/{clean_sym}/",
            params={"sections": "overview,valuation,dividend,peers"},
            ttl_seconds=settings.CACHE_TTL_REPORTS
        )

        # 2. Foreign Flow (Recent 14 days)
        foreign_res = await sectors_client.get(
            f"/foreign-flow/{clean_sym}/",
            ttl_seconds=settings.CACHE_TTL_BROKERS
        )

        # 3. Top Brokers (Accumulations/Distributions)
        brokers_res = await sectors_client.get(
            f"/broker-summary/{clean_sym}/top/",
            params={"n_brokers": 5},
            ttl_seconds=settings.CACHE_TTL_BROKERS
        )

        return {
            "symbol": clean_sym,
            "report": report_res.get("data", {}),
            "foreign_flow": foreign_res.get("data", []),
            "top_brokers": brokers_res.get("data", {}),
            "credits_consumed": (
                report_res.get("_meta", {}).get("credits_consumed", 0) +
                foreign_res.get("_meta", {}).get("credits_consumed", 0) +
                brokers_res.get("_meta", {}).get("credits_consumed", 0)
            )
        }

    @staticmethod
    async def fetch_market_pulse() -> Dict[str, Any]:
        """
        Gathers broad market data:
        - Top gainers (1d)
        - Top losers (1d)
        - Most traded stocks (volume)
        - IDX Total Market Cap
        """
        gainers_res = await sectors_client.get(
            "/companies/top-changes/",
            params={"classifications": "top_gainers", "periods": "1d", "n_stock": 5},
            ttl_seconds=1800
        )
        losers_res = await sectors_client.get(
            "/companies/top-changes/",
            params={"classifications": "top_losers", "periods": "1d", "n_stock": 5},
            ttl_seconds=1800
        )
        traded_res = await sectors_client.get(
            "/most-traded/",
            params={"n_stock": 5},
            ttl_seconds=1800
        )
        total_mc_res = await sectors_client.get(
            "/idx-total/",
            ttl_seconds=settings.CACHE_TTL_DAILY
        )

        return {
            "top_gainers": gainers_res.get("data", []),
            "top_losers": losers_res.get("data", []),
            "most_traded": traded_res.get("data", []),
            "market_summary": total_mc_res.get("data", []),
            "credits_consumed": (
                gainers_res.get("_meta", {}).get("credits_consumed", 0) +
                losers_res.get("_meta", {}).get("credits_consumed", 0) +
                traded_res.get("_meta", {}).get("credits_consumed", 0) +
                total_mc_res.get("_meta", {}).get("credits_consumed", 0)
            )
        }

    @staticmethod
    async def fetch_sector_deepdive(sub_sector: str) -> Dict[str, Any]:
        """
        Fetches subsector report and constituent companies.
        """
        sec_res = await sectors_client.get(
            f"/subsector/report/{sub_sector.lower()}/",
            ttl_seconds=settings.CACHE_TTL_REPORTS
        )
        return {
            "sub_sector": sub_sector,
            "data": sec_res.get("data", {}),
            "credits_consumed": sec_res.get("_meta", {}).get("credits_consumed", 0)
        }

sectors_engine = SectorsDataEngine()
