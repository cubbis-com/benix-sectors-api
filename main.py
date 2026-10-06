"""
Main Application Entrypoint for Sectors Financial AI Middleware Gateway.
"""
from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from config import settings
from core.cache import cache_manager
from core.credits_tracker import credits_tracker
from core.portal_db import portal_db
from core.local_market_db import local_market_db

# Import Routers
from routers.screener import router as screener_router
from routers.companies import router as companies_router
from routers.market import router as market_router
from routers.brokers import router as brokers_router
from routers.helpers import router as helpers_router
from routers.regional import router as regional_router
from routers.mining import router as mining_router
from routers.agent import router as agent_router
from routers.notifications import router as notifications_router
from routers.metrics import router as metrics_router
from routers.portal import router as portal_router
from routers.agentic_skills import router as agentic_skills_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("sectors.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Databases & Tables
    logger.info("Initializing Sectors Gateway databases...")
    await cache_manager.init_db()
    await credits_tracker.init_db()
    await portal_db.init_db()
    await local_market_db.init_sqlite()
    from core.news_scraper import news_aggregator
    await news_aggregator.ensure_daily_scrape()
    logger.info("Gateway, Portal DB, Local Market DB & Daily News Wire initialized. Ready to serve requests.")
    yield
    # Shutdown
    logger.info("Shutting down Sectors Gateway...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
High-Performance Financial Data & AI Middleware for Sectors API v2.
Built with **Credit Shield Protocol** (Smart SQLite Caching) and **Modular Agentic AI Skills**:
- **Sectors API Skill**: Data acquisition & credit protection
- **Trader Analyst AI Skill**: Valuations, bandarmology, broker flow
- **Financial Journalist AI Skill**: Professional Indonesian financial news generation
- **Backend Dev Skill**: Query generation & pipeline architecture
- **Frontend Dev Skill**: UI blueprints, components & visual tokens
- **Garda Chief Orchestrator**: Autonomous news generation & WhatsApp broadcast
    """,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware (Allows frontend portals and dashboards)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers under /api/v1
app.include_router(screener_router, prefix="/api/v1")
app.include_router(companies_router, prefix="/api/v1")
app.include_router(market_router, prefix="/api/v1")
app.include_router(brokers_router, prefix="/api/v1")
app.include_router(helpers_router, prefix="/api/v1")
app.include_router(regional_router, prefix="/api/v1")
app.include_router(mining_router, prefix="/api/v1")
app.include_router(agent_router, prefix="/api/v1")
app.include_router(notifications_router, prefix="/api/v1")
app.include_router(metrics_router, prefix="/api/v1")
app.include_router(portal_router, prefix="/api/v1")
app.include_router(agentic_skills_router, prefix="/api/v1")

from pathlib import Path
from fastapi.staticfiles import StaticFiles

static_dir = Path(__file__).resolve().parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/", response_class=HTMLResponse, tags=["Portal News & Dashboard"])
async def root_portal():
    """Live Financial News Portal with Pitch Black Theme & Garda AI White Orb Assistant."""
    template_path = Path(__file__).resolve().parent / "templates" / "portal.html"
    if template_path.exists():
        return HTMLResponse(content=template_path.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>Portal template not found</h1>", status_code=404)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
