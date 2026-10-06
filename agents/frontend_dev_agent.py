"""
Frontend Developer AI Assistant Agent.
Provides UI/UX design specifications, component schemas, and portal layouts.
"""
from typing import Dict, Any

class FrontendDevAgent:
    """Specialized agent for frontend design systems, dashboard widgets, and chart configurations."""

    @staticmethod
    def get_portal_ui_blueprint() -> Dict[str, Any]:
        """Returns standard UI/UX specifications for the Financial News Portal."""
        return {
            "theme": {
                "palette": {
                    "background": "#0f172a",
                    "surface": "#1e293b",
                    "border": "#334155",
                    "accent_primary": "#f97316",
                    "accent_secondary": "#38bdf8",
                    "positive_green": "#22c55e",
                    "negative_red": "#ef4444",
                    "text_primary": "#f8fafc",
                    "text_muted": "#94a3b8"
                },
                "typography": {
                    "heading_font": "Inter, sans-serif",
                    "body_font": "system-ui, sans-serif",
                    "numbers_font": "JetBrains Mono, monospace"
                }
            },
            "components": [
                {
                    "name": "MarketTickerRibbon",
                    "endpoint": "/api/v1/market/top-movers",
                    "description": "Continuous horizontal ticker displaying top IDX gainers and losers"
                },
                {
                    "name": "BreakingNewsHero",
                    "endpoint": "/api/v1/portal/articles?category=market-pulse&limit=1",
                    "description": "Main featured editorial article with sentiment badge and key stats"
                },
                {
                    "name": "StockDeepdiveCard",
                    "endpoint": "/api/v1/companies/{symbol}",
                    "description": "Fundamental snapshot card showing P/E, Market Cap, Dividend, and Broker Flow"
                },
                {
                    "name": "GardaChatDrawer",
                    "endpoint": "/api/v1/agent/query",
                    "description": "Interactive AI Assistant drawer for investor conversational Q&A"
                }
            ]
        }

frontend_dev_agent = FrontendDevAgent()
