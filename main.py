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

import asyncio
import json
import time
from fastapi import WebSocket, WebSocketDisconnect
from core.market_websocket import market_ws_manager

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
    broadcaster_task = asyncio.create_task(market_ws_manager.start_broadcaster_loop())
    logger.info("Gateway, Portal DB, Local Market DB & WebSocket Broadcaster initialized. Ready to serve requests.")
    yield
    # Shutdown
    logger.info("Shutting down Sectors Gateway...")
    broadcaster_task.cancel()

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
@app.get("/portal", response_class=HTMLResponse, include_in_schema=False)
async def root_portal():
    """Live Financial News Portal with Pitch Black Theme & Garda AI White Orb Assistant."""
    template_path = Path(__file__).resolve().parent / "templates" / "portal.html"
    if template_path.exists():
        return HTMLResponse(content=template_path.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>Portal template not found</h1>", status_code=404)

# ================= REALTIME WEBSOCKET MARKET ALERT FEED =================
@app.websocket("/ws/market-alerts")
async def websocket_market_alerts(websocket: WebSocket):
    """
    Realtime WebSocket streaming market shifts, price breakouts,
    unusual volume surges, and foreign accumulation alerts.
    """
    await market_ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
                action = payload.get("action")
                if action == "trigger_simulation":
                    alert = market_ws_manager.generate_random_alert()
                    await market_ws_manager.broadcast_alert(alert)
                elif action == "ping":
                    await websocket.send_json({"type": "pong", "time": time.time()})
            except Exception:
                pass
    except WebSocketDisconnect:
        market_ws_manager.disconnect(websocket)
    except Exception:
        market_ws_manager.disconnect(websocket)

@app.get("/api/v1/market/alert-history", tags=["Market Monitoring"])
async def get_market_alert_history():
    """Returns recent market alerts received via WebSocket stream."""
    return {
        "status": "success",
        "alerts": market_ws_manager.alert_history,
        "active_ws_clients": len(market_ws_manager.active_connections)
    }

@app.post("/api/v1/market/broadcast-alert", tags=["Market Monitoring"])
async def broadcast_manual_market_alert():
    """Triggers an instantaneous market alert simulation via WebSocket."""
    alert = market_ws_manager.generate_random_alert()
    broadcasted = await market_ws_manager.broadcast_alert(alert)
    return {"status": "broadcasted", "alert": broadcasted}

@app.get("/api/v1/market/screener-stocks", tags=["Market Screener"])
async def get_screener_stocks():
    """Returns enriched local stocks list for interactive screener table (0 credit)."""
    from core.local_market_db import DEFAULT_SEED_MARKET
    stocks_dict = DEFAULT_SEED_MARKET.get("stocks", {})
    stocks_list = list(stocks_dict.values())
    return {
        "status": "success",
        "total": len(stocks_list),
        "stocks": stocks_list
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
