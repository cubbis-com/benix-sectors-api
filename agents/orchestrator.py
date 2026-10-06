"""
Garda Chief Orchestrator (Editor-in-Chief AI).
Coordinates data extraction, financial analysis, journalistic writing, and portal publication.
"""
import logging
from typing import Dict, Any, Optional
from agents.sectors_engine import sectors_engine
from agents.trader_agent import trader_agent
from agents.journalist_agent import journalist_agent
from core.portal_db import portal_db
from routers.notifications import send_wa_message
from config import settings

logger = logging.getLogger("sectors.orchestrator")

class GardaChiefOrchestrator:
    """Autonomous Orchestrator for Portal News and Market Intelligence."""

    @staticmethod
    async def publish_emiten_news(symbol: str) -> Dict[str, Any]:
        """
        End-to-End Pipeline for Single Stock:
        1. Sectors Engine pulls verified data (Overview, Valuation, Foreign Flow, Brokers)
        2. Trader AI evaluates technical, valuation, and bandarmology signals
        3. Wartawan AI crafts professional Indonesian news article
        4. Portal DB saves and publishes article immediately
        """
        logger.info("🎬 [ORCHESTRATOR] Starting news generation for ticker %s...", symbol)

        # Step 1: Data Acquisition
        stock_data = await sectors_engine.fetch_stock_deepdive(symbol)

        # Step 2: Analyst Reasoning
        trader_insight = trader_agent.analyze_stock(symbol, stock_data)

        # Step 3: Journalistic Composition
        article_draft = journalist_agent.write_stock_deepdive_article(
            symbol=symbol,
            stock_data=stock_data,
            trader_insight=trader_insight
        )

        # Step 4: Portal DB Publication
        saved = await portal_db.save_article(
            title=article_draft["title"],
            slug=article_draft["slug"],
            summary=article_draft["summary"],
            content=article_draft["content"],
            category=article_draft["category"],
            tickers=article_draft["tickers"],
            author=article_draft["author"],
            sentiment=article_draft["sentiment"],
            sectors_data=article_draft["sectors_data"]
        )

        logger.info("✅ [ORCHESTRATOR] Article published successfully: %s", saved["slug"])

        return {
            "status": "published",
            "article": saved,
            "full_content": article_draft["content"],
            "trader_insight": trader_insight,
            "credits_consumed": stock_data.get("credits_consumed", 0)
        }

    @staticmethod
    async def publish_market_pulse(broadcast_whatsapp: bool = True) -> Dict[str, Any]:
        """
        End-to-End Pipeline for Daily Market Pulse:
        1. Sectors Engine pulls Top Movers, Most Traded, and IDX Total
        2. Trader AI evaluates market regime & sentiment
        3. Wartawan AI crafts daily market pulse article
        4. Portal DB saves and publishes article
        5. Optionally pushes executive summary to WhatsApp
        """
        logger.info("🎬 [ORCHESTRATOR] Starting Daily Market Pulse generation...")

        # Step 1: Data Acquisition
        pulse_data = await sectors_engine.fetch_market_pulse()

        # Step 2: Analyst Reasoning
        market_insight = trader_agent.analyze_market_overview(pulse_data)

        # Step 3: Journalistic Composition
        article_draft = journalist_agent.write_market_pulse_article(
            pulse_data=pulse_data,
            market_insight=market_insight
        )

        # Step 4: Portal DB Publication
        saved = await portal_db.save_article(
            title=article_draft["title"],
            slug=article_draft["slug"],
            summary=article_draft["summary"],
            content=article_draft["content"],
            category=article_draft["category"],
            tickers=article_draft["tickers"],
            author=article_draft["author"],
            sentiment=article_draft["sentiment"],
            sectors_data=article_draft["sectors_data"]
        )

        # Step 5: WhatsApp Notification
        wa_response = None
        if broadcast_whatsapp:
            wa_text = f"📰 *{saved['title']}*\n\n{saved['summary']}\n\n🔗 _Baca selengkapnya di Garda Financial Portal._"
            try:
                wa_response = await send_wa_message(to=settings.WA_DEFAULT_TARGET, message=wa_text)
            except Exception as e:
                logger.warning("WhatsApp push warning: %s", e)

        logger.info("✅ [ORCHESTRATOR] Market Pulse published: %s", saved["slug"])

        return {
            "status": "published",
            "article": saved,
            "whatsapp_sent": broadcast_whatsapp,
            "whatsapp_response": wa_response,
            "credits_consumed": pulse_data.get("credits_consumed", 0)
        }

garda_orchestrator = GardaChiefOrchestrator()
