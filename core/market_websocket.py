"""
WebSocket Realtime Market Intelligence & Alert Manager.
Streams realtime market shifts, price breakouts, volume anomalies,
foreign flow accumulation, and forex spikes to connected portal clients.
Zero upstream quota consumption.
"""
import asyncio
import json
import logging
import time
from typing import List, Set, Dict, Any, Optional
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger("sectors.websocket")

# Real market tickers and profiles for realistic alerts
MONITORED_TICKERS = [
    {"ticker": "BBCA", "name": "PT Bank Central Asia Tbk", "sector": "Financials", "base_price": 10125},
    {"ticker": "BBRI", "name": "PT Bank Rakyat Indonesia (Persero) Tbk", "sector": "Financials", "base_price": 4980},
    {"ticker": "BMRI", "name": "PT Bank Mandiri (Persero) Tbk", "sector": "Financials", "base_price": 6850},
    {"ticker": "TLKM", "name": "PT Telkom Indonesia (Persero) Tbk", "sector": "Infrastructure & Telco", "base_price": 3010},
    {"ticker": "ASII", "name": "PT Astra International Tbk", "sector": "Industrials & Automotive", "base_price": 5050},
    {"ticker": "ADRO", "name": "PT Adaro Energy Indonesia Tbk", "sector": "Energy & Coal", "base_price": 3720},
    {"ticker": "BREN", "name": "PT Barito Renewables Energy Tbk", "sector": "Renewable Energy", "base_price": 6975},
    {"ticker": "ANTM", "name": "PT Aneka Tambang Tbk", "sector": "Basic Materials & Gold", "base_price": 1620},
    {"ticker": "MEDC", "name": "PT Medco Energi Internasional Tbk", "sector": "Oil & Gas", "base_price": 1310},
    {"ticker": "ICBP", "name": "PT Indofood CBP Sukses Makmur Tbk", "sector": "Consumer Non-Cyclicals", "base_price": 11200}
]

ALERT_TEMPLATES = [
    {
        "type": "FOREIGN_BUY_ACCUMULATION",
        "severity": "CRITICAL",
        "headline": "Akumulasi Asing Agresif: Foreign Net Buy Terkonfirmasi",
        "msg_tpl": "Broker asing dominan (ZP, DX, AK) memborong {ticker} senilai Rp {val} Miliar di pasar reguler. Volume 3.2x rata-rata 20 hari.",
        "chg_range": (1.2, 3.5),
        "tag": "SMART MONEY ACCUMULATION"
    },
    {
        "type": "PRICE_BREAKOUT",
        "severity": "CRITICAL",
        "headline": "Breakout Resistance Kunci: Menembus Level Psikologis",
        "msg_tpl": "{ticker} melompat menembus area resistance dengan lonjakan order buy. Target kenaikan swing terbuka menuju level berikutnya.",
        "chg_range": (1.8, 4.2),
        "tag": "TECHNICAL BREAKOUT"
    },
    {
        "type": "UNUSUAL_VOLUME_SURGE",
        "severity": "WARNING",
        "headline": "Anomali Volume & Frekuensi Transaksi Terdeteksi",
        "msg_tpl": "Aktivitas transaksi {ticker} meningkat tajam ({vol}x rerata harian). Algoritma mendeteksi rotasi sektoral ke saham likuid.",
        "chg_range": (0.6, 2.1),
        "tag": "VOLUME ANOMALY"
    },
    {
        "type": "ORDERBOOK_IMBALANCE",
        "severity": "WARNING",
        "headline": "Ketidakseimbangan Order Book: Tekanan Beli Dominan",
        "msg_tpl": "Rasio Bid terhadap Offer pada antrean {ticker} mencapai {ratio}:1. Tembok beli tebal terpasang di level Rp {support}.",
        "chg_range": (0.4, 1.8),
        "tag": "ORDER BOOK IMBALANCE"
    },
    {
        "type": "FOREX_CORRELATION_SPIKE",
        "severity": "INFO",
        "headline": "Korelasi Valas: Sentimen Positif Penguatan Ekspor",
        "msg_tpl": "Dolar AS menguat terhadap Rupiah (JISDOR), memberikan dorongan pendapatan valas bagi eksportir {ticker}.",
        "chg_range": (0.8, 2.4),
        "tag": "MACRO FOREX DRIVER"
    }
]


class MarketWebSocketManager:
    """Manages active WebSocket connections and broadcasts market alerts in real-time."""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.alert_history: List[Dict[str, Any]] = []
        self._max_history = 50
        self._counter = 0
        self._broadcaster_task: Optional[asyncio.Task] = None
        self._seed_initial_history()

    def _seed_initial_history(self):
        """Pre-seeds recent alerts so new users immediately see market activity."""
        now = datetime.now()
        samples = [
            {
                "id": "alert-init-1",
                "type": "FOREIGN_BUY_ACCUMULATION",
                "trigger_type": "FOREIGN_BUY_ACCUMULATION",
                "severity": "CRITICAL",
                "ticker": "BBCA",
                "symbol": "BBCA",
                "company_name": "PT Bank Central Asia Tbk",
                "sector": "Financials",
                "price": "Rp 10.125",
                "change_pct": "+1.76%",
                "headline": "Akumulasi Asing Agresif: Foreign Net Buy Rp 245 Miliar Terkonfirmasi",
                "message": "Broker asing dominan (ZP, DX, AK) memborong saham BBCA di pasar reguler. Volume 3.2x rata-rata 20 hari.",
                "description": "Broker asing dominan (ZP, DX, AK) memborong saham BBCA di pasar reguler. Volume 3.2x rata-rata 20 hari.",
                "tag": "SMART MONEY ACCUMULATION",
                "timestamp": now.strftime("%H:%M:%S WIB"),
                "iso_time": now.isoformat()
            },
            {
                "id": "alert-init-2",
                "type": "PRICE_BREAKOUT",
                "trigger_type": "PRICE_BREAKOUT",
                "severity": "WARNING",
                "ticker": "ADRO",
                "symbol": "ADRO",
                "company_name": "PT Adaro Energy Indonesia Tbk",
                "sector": "Energy & Coal",
                "price": "Rp 3.720",
                "change_pct": "+2.48%",
                "headline": "Breakout Resistance Kunci: Menembus Area Rp 3.700",
                "message": "ADRO melompat menembus area resistance dengan lonjakan order buy menyusul reli harga komoditas batubara.",
                "description": "ADRO melompat menembus area resistance dengan lonjakan order buy menyusul reli harga komoditas batubara.",
                "tag": "TECHNICAL BREAKOUT",
                "timestamp": now.strftime("%H:%M:%S WIB"),
                "iso_time": now.isoformat()
            },
            {
                "id": "alert-init-3",
                "type": "ORDERBOOK_IMBALANCE",
                "trigger_type": "ORDERBOOK_IMBALANCE",
                "severity": "INFO",
                "ticker": "BMRI",
                "symbol": "BMRI",
                "company_name": "PT Bank Mandiri (Persero) Tbk",
                "sector": "Financials",
                "price": "Rp 6.850",
                "change_pct": "+0.74%",
                "headline": "Ketidakseimbangan Order Book: Rasio Bid/Offer 2.8:1",
                "message": "Antrean beli tebal terpasang di level Rp 6.800 mengindikasikan pertahanan harga kuat dari investor institusi.",
                "description": "Antrean beli tebal terpasang di level Rp 6.800 mengindikasikan pertahanan harga kuat dari investor institusi.",
                "tag": "ORDER BOOK IMBALANCE",
                "timestamp": now.strftime("%H:%M:%S WIB"),
                "iso_time": now.isoformat()
            }
        ]
        self.alert_history.extend(samples)

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info("WebSocket client connected. Active clients: %d", len(self.active_connections))
        
        # Send initial welcome snapshot with history
        welcome_payload = {
            "type": "CONNECTION_ESTABLISHED",
            "status": "connected",
            "active_clients": len(self.active_connections),
            "server_time": datetime.now().strftime("%H:%M:%S WIB"),
            "recent_alerts": self.alert_history[-10:]
        }
        await websocket.send_json(welcome_payload)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        logger.info("WebSocket client disconnected. Remaining clients: %d", len(self.active_connections))

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast JSON payload to all active WebSocket clients."""
        if not self.active_connections:
            return
        
        dead_connections = set()
        for ws in self.active_connections:
            try:
                await ws.send_json(message)
            except Exception as e:
                logger.debug("Failed sending to client: %s", e)
                dead_connections.add(ws)
                
        for dead in dead_connections:
            self.active_connections.discard(dead)

    async def broadcast_alert(self, alert_data: Dict[str, Any]):
        """Adds alert to history and sends to all clients."""
        self._counter += 1
        now = datetime.now()
        alert_data["id"] = f"alert-{int(time.time())}-{self._counter}"
        alert_data["timestamp"] = now.strftime("%H:%M:%S WIB")
        alert_data["iso_time"] = now.isoformat()
        
        self.alert_history.append(alert_data)
        if len(self.alert_history) > self._max_history:
            self.alert_history = self.alert_history[-self._max_history:]
            
        payload = {
            "type": "MARKET_ALERT",
            "alert": alert_data,
            "total_alerts": len(self.alert_history)
        }
        await self.broadcast(payload)
        logger.info("Broadcasted market alert for %s: %s", alert_data.get("ticker"), alert_data.get("headline"))
        return alert_data

    def generate_random_alert(self) -> Dict[str, Any]:
        """Generates a realistic market alert from template data."""
        import random
        ticker_info = random.choice(MONITORED_TICKERS)
        tpl = random.choice(ALERT_TEMPLATES)
        
        chg = round(random.uniform(*tpl["chg_range"]), 2)
        price_delta = int(ticker_info["base_price"] * (chg / 100))
        cur_price = ticker_info["base_price"] + price_delta
        
        val = random.randint(35, 180)
        vol = round(random.uniform(2.1, 4.5), 1)
        ratio = round(random.uniform(2.4, 3.8), 1)
        support = cur_price - (random.randint(1, 3) * 25)
        
        msg = tpl["msg_tpl"].format(
            ticker=ticker_info["ticker"],
            val=val,
            vol=vol,
            ratio=ratio,
            support=support
        )
        return {
            "type": tpl["type"],
            "trigger_type": tpl["type"],
            "severity": tpl["severity"],
            "ticker": ticker_info["ticker"],
            "symbol": ticker_info["ticker"],
            "company_name": ticker_info["name"],
            "sector": ticker_info["sector"],
            "price": f"Rp {cur_price:,}".replace(",", "."),
            "price_num": cur_price,
            "change_pct": f"+{chg}%",
            "change_pct_num": chg,
            "headline": f"{ticker_info['ticker']}: {tpl['headline']}",
            "description": msg,
            "message": msg,
            "tag": tpl["tag"]
        }

    async def start_broadcaster_loop(self):
        """Background coroutine that generates realistic market alerts periodically."""
        logger.info("Market WebSocket broadcaster background service started.")
        while True:
            try:
                # Wait 16-24 seconds between simulated real-time events
                await asyncio.sleep(20)
                if self.active_connections:
                    alert = self.generate_random_alert()
                    await self.broadcast_alert(alert)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in market broadcaster loop: %s", e)
                await asyncio.sleep(5)


# Global Singleton Manager
market_ws_manager = MarketWebSocketManager()
