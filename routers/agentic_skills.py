"""
Agentic AI Skills Execution Router.
Exposes specialized skills (Sectors API, Trader, Wartawan, Backend, Frontend, Garda Orchestrator)
as interactive web services for the frontend portal and autonomous automation workflows.
"""
from typing import Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from agents.sectors_engine import sectors_engine
from agents.trader_agent import trader_agent
from agents.journalist_agent import journalist_agent
from agents.backend_dev_agent import backend_dev_agent
from agents.frontend_dev_agent import frontend_dev_agent
from agents.orchestrator import garda_orchestrator
from core.sectors_client import normalize_ticker

router = APIRouter(prefix="/agent/skills", tags=["Agentic AI Skills (Modular)"])

# ----------------- Schemas -----------------
class TraderAnalysisRequest(BaseModel):
    symbol: str = Field(..., description="IDX ticker to analyze e.g. BBCA, BMRI")

class JournalistArticleRequest(BaseModel):
    symbol: str = Field(..., description="IDX ticker e.g. BBCA")
    auto_publish: bool = Field(True, description="Save and publish directly to portal DB")

class BackendQueryRequest(BaseModel):
    sub_sector: Optional[str] = None
    min_market_cap: Optional[int] = None
    max_pe: Optional[float] = None
    min_dividend_yield: Optional[float] = None
    sort_by: str = "-market_cap"

class OrchestratorPulseRequest(BaseModel):
    broadcast_whatsapp: bool = Field(True, description="Push summary to WhatsApp channel")

# ----------------- Skill Catalog -----------------
@router.get("/catalog", summary="List All Modular Agentic AI Skills")
async def get_skills_catalog():
    """
    Returns metadata for all available Agentic AI Skills:
    - sectors-api-skill
    - trader-analyst-skill
    - financial-journalist-skill
    - backend-dev-skill
    - frontend-dev-skill
    - garda-orchestrator-skill
    """
    return {
        "status": "ready",
        "total_skills": 6,
        "skills": [
            {
                "id": "sectors-api-skill",
                "name": "Sectors Financial API Specialist",
                "role": "Data Acquisition & Credit Shield Caching",
                "doc_ref": ".agents/skills/sectors-api-skill/SKILL.md",
                "executable": True
            },
            {
                "id": "trader-analyst-skill",
                "name": "Trader & Market Analyst AI",
                "role": "Bandarmology, Valuation & Risk-Reward Evaluation",
                "doc_ref": ".agents/skills/trader-analyst-skill/SKILL.md",
                "executable": True
            },
            {
                "id": "financial-journalist-skill",
                "name": "Financial Journalist AI (Wartawan Pasar Modal)",
                "role": "Crafting Indonesian Financial News Articles",
                "doc_ref": ".agents/skills/financial-journalist-skill/SKILL.md",
                "executable": True
            },
            {
                "id": "backend-dev-skill",
                "name": "Backend Software Engineer AI",
                "role": "API Contracts, Screener Query Architecture & Schedulers",
                "doc_ref": ".agents/skills/backend-dev-skill/SKILL.md",
                "executable": True
            },
            {
                "id": "frontend-dev-skill",
                "name": "Frontend UI/UX Engineer AI",
                "role": "Financial Portal Layouts, Tickers & Visualizations",
                "doc_ref": ".agents/skills/frontend-dev-skill/SKILL.md",
                "executable": True
            },
            {
                "id": "garda-orchestrator-skill",
                "name": "Garda Chief Orchestrator (Editor-in-Chief)",
                "role": "Multi-Agent Coordination & Autonomous Publishing",
                "doc_ref": ".agents/skills/garda-orchestrator-skill/SKILL.md",
                "executable": True
            }
        ]
    }

# ----------------- Trader Skill -----------------
@router.post("/trader/analyze", summary="Run Trader Analyst Skill on a Stock")
async def run_trader_skill(payload: TraderAnalysisRequest):
    """
    Executes Trader Skill:
    Pulls real-time Sectors data -> evaluates valuation, bandarmology, foreign flow, and pivot levels.
    """
    sym = normalize_ticker(payload.symbol)
    stock_data = await sectors_engine.fetch_stock_deepdive(sym)
    analysis = trader_agent.analyze_stock(sym, stock_data)
    return {
        "symbol": sym,
        "trader_insight": analysis,
        "credits_consumed": stock_data.get("credits_consumed", 0)
    }

# ----------------- Journalist Skill -----------------
@router.post("/journalist/write-article", summary="Run Financial Journalist Skill")
async def run_journalist_skill(payload: JournalistArticleRequest):
    """
    Executes Journalist Skill:
    Converts real market data into a full journalistic article in Indonesian.
    """
    sym = normalize_ticker(payload.symbol)
    if payload.auto_publish:
        result = await garda_orchestrator.publish_emiten_news(sym)
        return result
    else:
        stock_data = await sectors_engine.fetch_stock_deepdive(sym)
        trader_insight = trader_agent.analyze_stock(sym, stock_data)
        draft = journalist_agent.write_stock_deepdive_article(sym, stock_data, trader_insight)
        return draft

# ----------------- Backend Dev Skill -----------------
@router.post("/backend/screener-query", summary="Run Backend Dev Skill (Build Query)")
async def run_backend_dev_skill(payload: BackendQueryRequest):
    """
    Executes Backend Dev Skill:
    Builds optimized SQL-like Sectors API screener query parameters.
    """
    query_spec = backend_dev_agent.generate_screener_query(
        sub_sector=payload.sub_sector,
        min_market_cap=payload.min_market_cap,
        max_pe=payload.max_pe,
        min_dividend_yield=payload.min_dividend_yield,
        sort_by=payload.sort_by
    )
    return query_spec

# ----------------- Frontend Dev Skill -----------------
@router.get("/frontend/ui-blueprint", summary="Run Frontend Dev Skill (Get UI Blueprint)")
async def run_frontend_dev_skill():
    """
    Executes Frontend Dev Skill:
    Returns complete UI design token blueprint and component specifications for the portal.
    """
    return frontend_dev_agent.get_portal_ui_blueprint()

# ----------------- Orchestrator Skill -----------------
@router.post("/orchestrator/publish-news", summary="Run Garda Orchestrator (Autonomous News Publisher)")
async def run_orchestrator_publish_news(symbol: str = Query(..., description="Ticker e.g. BBCA, BBRI, BMRI")):
    """
    Executes Garda Orchestrator Skill:
    Autonomous multi-step pipeline: Data Pull -> Trader Evaluation -> Wartawan Writing -> DB Publication.
    """
    clean_sym = normalize_ticker(symbol)
    return await garda_orchestrator.publish_emiten_news(clean_sym)

@router.post("/orchestrator/publish-pulse", summary="Run Garda Orchestrator (Daily Market Pulse & WhatsApp)")
async def run_orchestrator_publish_pulse(payload: OrchestratorPulseRequest):
    """
    Executes Garda Orchestrator Skill for Market Wrap:
    Gathers top movers -> Evaluates market sentiment -> Publishes article -> Pushes to WhatsApp.
    """
    return await garda_orchestrator.publish_market_pulse(broadcast_whatsapp=payload.broadcast_whatsapp)
