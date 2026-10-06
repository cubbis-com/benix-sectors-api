"""
Backend Developer AI Assistant Agent.
Assists developers in generating API contracts, SQL-like screener queries, and integration templates.
"""
from typing import Dict, Any, List

class BackendDevAgent:
    """Specialized agent for backend engineering tasks, API contracts, and pipeline architecture."""

    @staticmethod
    def generate_screener_query(
        sub_sector: str = None,
        min_market_cap: int = None,
        max_pe: float = None,
        min_dividend_yield: float = None,
        sort_by: str = "-market_cap"
    ) -> Dict[str, Any]:
        """Generates a valid Sectors API v2 structured screener query."""
        conditions = []
        if sub_sector:
            conditions.append(f"sub_sector = '{sub_sector.lower()}'")
        if min_market_cap:
            conditions.append(f"market_cap >= {min_market_cap}")
        if max_pe:
            conditions.append(f"pe_ttm <= {max_pe}")
        if min_dividend_yield:
            conditions.append(f"yield_ttm >= {min_dividend_yield}")

        where_clause = " and ".join(conditions) if conditions else None

        return {
            "endpoint": "/v2/companies/",
            "method": "GET",
            "query_parameters": {
                "where": where_clause,
                "order_by": sort_by,
                "limit": 50
            },
            "estimated_credits": 1,
            "curl_example": f'curl -H "Authorization: $SECTORS_API_KEY" "https://api.sectors.app/v2/companies/?where={where_clause or ""}&order_by={sort_by}"'
        }

    @staticmethod
    def get_api_catalog() -> List[Dict[str, Any]]:
        """Returns the high-level API specifications available in the middleware."""
        return [
            {"route": "/api/v1/screener", "category": "Screener", "desc": "Filter IDX companies via SQL or NL"},
            {"route": "/api/v1/companies/{symbol}", "category": "Reports", "desc": "Comprehensive company report"},
            {"route": "/api/v1/market/top-movers", "category": "Movers", "desc": "Top gainers and losers"},
            {"route": "/api/v1/brokers/foreign-flow", "category": "Flow", "desc": "Universe and symbol foreign flow"},
            {"route": "/api/v1/portal/articles", "category": "Portal", "desc": "Read published financial articles"},
            {"route": "/api/v1/agent/orchestrator/publish-news", "category": "Agentic", "desc": "Autonomous news pipeline"}
        ]

backend_dev_agent = BackendDevAgent()
