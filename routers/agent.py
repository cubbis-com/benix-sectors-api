"""
Agentic AI Query Router (Garda Market Concierge Core).
Enforces Local-First Database Checks (SQLite / JSON) to prevent unnecessary
Sectors API calls, preserving quota credits while powering high-touch UMKM advisory.
"""
import re
import json
import logging
from typing import Optional, List, Dict, Any
from fastapi import APIRouter
from pydantic import BaseModel, Field

from core.sectors_client import sectors_client, normalize_ticker
from core.garda_client import garda_llm_client, GARDA_SYSTEM_PROMPT
from core.local_market_db import local_market_db
from core.news_scraper import news_aggregator

logger = logging.getLogger("sectors.agent_router")

router = APIRouter(prefix="/agent", tags=["AI Agent (Garda Reasoning)"])

COMPANY_NAME_TO_TICKER = {
    "bca": "BBCA", "bri": "BBRI", "mandiri": "BMRI", "bni": "BBNI",
    "telkom": "TLKM", "telkomsel": "TLKM", "astra": "ASII",
    "indofood": "ICBP", "indomie": "ICBP", "mayora": "MYOR", "unilever": "UNVR",
    "charoen": "CPIN", "pokphand": "CPIN", "japfa": "JPFA",
    "semen indonesia": "SMGR", "semen gresik": "SMGR", "sig": "SMGR",
    "ciputra": "CTRA", "bsd": "BSDE", "sinarmas": "BSDE", "pakuwon": "PWON",
    "sahid": "SHID", "eastparc": "EAST", "panorama": "PANR",
    # SGX Tickers & Aliases
    "dbs": "D05", "dbs bank": "D05", "ocbc": "O39", "uob": "U11",
    "singtel": "Z74", "singapore airlines": "C6L", "sia": "C6L",
    "genting": "G13", "rws": "G13", "capitaland": "A17U", "cict": "A17U"
}

SGX_SYMBOLS = ["D05", "O39", "U11", "Z74", "C6L", "G13", "A17U", "BN4", "BS6"]

class AgentQueryRequest(BaseModel):
    query: str = Field(..., description="User question in natural language (e.g. 'analisis emiten BBCA', 'bagaimana prospek hotel dan pariwisata?', 'kondisi pasar hari ini')")
    tickers: Optional[List[str]] = Field(None, description="Optional explicit tickers")
    sub_sector: Optional[str] = Field(None, description="Optional subsector filter")
    user_industry: Optional[str] = Field("UMKM / Bisnis Menengah", description="Industry context of the user (e.g. Perhotelan, Ritel, F&B, Perdagangan)")
    include_raw_data: bool = Field(True, description="Include raw data payloads in response")

class AgentQueryResponse(BaseModel):
    intent: str
    summary_insight: str
    target_entities: List[str]
    data_retrieved: Dict[str, Any]
    news_referenced: List[Dict[str, Any]] = Field(default_factory=list, description="Cross-referenced financial news headlines")
    total_credits_used: int
    data_sources: List[str]

@router.post("/query", response_model=AgentQueryResponse, summary="Process Financial Query with Garda Concierge")
async def process_agent_query(payload: AgentQueryRequest):
    """
    Executes the Garda AI Market Concierge pipeline:
    1. Intent & entity parsing (IDX & SGX stocks + UMKM scenarios)
    2. CHECK LOCAL STORAGE FIRST (SQLite gateway.db / local_market_store.json)
    3. Multi-Country News Aggregation & Cross-Referencing (20 portals ID, SG, MY, JP)
    4. Fallback to upstream Sectors API only on cache miss, automatically saving to local storage
    5. Formats insight according to GARDA Concierge System Prompt v2.0
    """
    text = payload.query.lower()
    tickers = [normalize_ticker(t) for t in (payload.tickers or [])]
    credits_used = 0
    sources = []
    retrieved_data = {}
    referenced_news = []

    # Check SGX symbols
    for st in SGX_SYMBOLS:
        if re.search(rf"\b{st}\b", payload.query, re.IGNORECASE):
            if st not in tickers:
                tickers.append(st)

    # Check Company Aliases
    for comp_name, tick in COMPANY_NAME_TO_TICKER.items():
        if re.search(rf"\b{re.escape(comp_name)}\b", text):
            if tick not in tickers:
                tickers.append(tick)

    # Extract 4-letter ticker candidates from text if none provided
    if not tickers:
        found = re.findall(r"\b[A-Za-z]{4}\b", payload.query.upper())
        ignore = {
            "HARI", "YANG", "DARI", "PADA", "AKAN", "SAAT", "BISA", "KITA", "DENG", "BANK",
            "FLOW", "ASIN", "DANA", "ARUS", "NET", "INFO", "DATA", "JUAL", "BELI", "CARA",
            "KAYA", "LABA", "BUKU", "NAIK", "TURU", "SUDA", "SEMA", "JADI", "SAHA", "SAHM",
            "FORE", "POST", "GOOD", "BEST", "VIEW", "DEEP", "RISK", "PEER", "RATE", "HIGH", "LOW",
            "SAYA", "KAMI", "ADAL", "BAGA", "MANA", "LAGI", "LESU", "RAMA", "TOKO", "BUAT", "BIAR", "CEK",
            "SAMA", "ATAU", "AGAR", "TIDA", "TAPI", "JIKA", "BAGI", "KALI", "LAIN", "OLEH", "KARE"
        }
        tickers = [t for t in found if t not in ignore]

    # Map hospitality & tourism queries to representative tickers if user mentions hotel/wisata
    if any(w in text for w in ["hotel", "pariwisata", "turis", "okupansi", "travel"]):
        if not tickers:
            tickers = ["SHID", "PANR", "EAST"]

    # ----------------- 0. UMKM Business Scenarios (brief.md Direct Matching) -----------------
    if any(w in text for w in ["mitra", "vendor", "due diligence", "kesehatan bisnis", "gagal bayar"]):
        intent = "umkm_vendor_due_diligence"
        topic_res = await local_market_db.get_umkm_topic_locally("vendor_due_diligence")
        if topic_res:
            retrieved_data["umkm_due_diligence"] = topic_res["data"]
            sources.append("local_storage (umkm_topics:vendor_due_diligence)")
        # Load TLKM & ICBP data locally
        for sym in ["TLKM", "ICBP"]:
            loc = await local_market_db.get_stock_locally(sym)
            if loc:
                retrieved_data[sym] = loc["data"]
        summary = "Pengecekan kesehatan bisnis mitra kerja sama (Vendor Due Diligence) untuk mencegah risiko gagal bayar."

    elif any(w in text for w in ["ritel", "retail", "f&b", "kuliner", "makanan", "restoran", "daya beli"]):
        intent = "umkm_retail_fnb_trend"
        topic_res = await local_market_db.get_umkm_topic_locally("retail_fnb_trend")
        if topic_res:
            retrieved_data["retail_fnb_trend"] = topic_res["data"]
            sources.append("local_storage (umkm_topics:retail_fnb_trend)")
        for sym in ["ICBP", "MYOR", "UNVR"]:
            loc = await local_market_db.get_stock_locally(sym)
            if loc:
                retrieved_data[sym] = loc["data"]
        summary = "Analisis tren daya beli konsumen ritel & kuliner serta benchmark margin industri FMCG."

    elif any(w in text for w in ["pakan", "ternak", "ayam", "jagung", "kedelai", "rantai pasok", "supply chain"]):
        intent = "umkm_supply_chain_feed"
        topic_res = await local_market_db.get_umkm_topic_locally("supply_chain_feed")
        if topic_res:
            retrieved_data["supply_chain_feed"] = topic_res["data"]
            sources.append("local_storage (umkm_topics:supply_chain_feed)")
        for sym in ["CPIN", "JPFA"]:
            loc = await local_market_db.get_stock_locally(sym)
            if loc:
                retrieved_data[sym] = loc["data"]
        summary = "Deteksi dini risiko rantai pasok dan beban biaya bahan baku pakan jagung/kedelai."

    elif any(w in text for w in ["bahan bangunan", "properti", "konstruksi", "semen", "material bangunan", "toko bangunan"]):
        intent = "umkm_property_construction"
        topic_res = await local_market_db.get_umkm_topic_locally("property_construction")
        if topic_res:
            retrieved_data["property_construction"] = topic_res["data"]
            sources.append("local_storage (umkm_topics:property_construction)")
        for sym in ["SMGR", "CTRA", "BSDE"]:
            loc = await local_market_db.get_stock_locally(sym)
            if loc:
                retrieved_data[sym] = loc["data"]
        summary = "Analisis prospek permintaan bahan bangunan dan sektor properti perumahan residensial."

    elif any(w in text for w in ["skrining dividen", "tabungan saham", "dividen aman", "cadangan kas", "dana darurat"]) or ("dividen" in text and not tickers):
        intent = "umkm_dividend_screener"
        topic_res = await local_market_db.get_umkm_topic_locally("dividend_screening")
        if topic_res:
            retrieved_data["dividend_screening"] = topic_res["data"]
            sources.append("local_storage (umkm_topics:dividend_screening)")
        summary = "Penyaringan saham dividen yield tinggi, valuasi wajar, dan utang rendah untuk dana cadangan UMKM."

    # ----------------- 1. Market Overview Intent -----------------
    elif any(w in text for w in ["pasar", "ihsg", "market", "bursa", "kondisi hari ini"]):
        intent = "market_overview"
        # Check Local Storage First
        local_overview = await local_market_db.get_market_overview_locally()
        if local_overview:
            logger.info("Serving market overview from local DB/JSON (0 credits)")
            retrieved_data["market_overview"] = local_overview["data"]
            sources.append(f"local_storage ({local_overview['source']})")
        else:
            # Fallback to Sectors API
            movers_res = await sectors_client.get("/companies/top-changes/", params={"classifications": "top_gainers", "periods": "1d", "n_stock": 5})
            retrieved_data["top_gainers"] = movers_res.get("data")
            credits_used += movers_res.get("_meta", {}).get("credits_consumed", 0)
            sources.append("/v2/companies/top-changes/")

            traded_res = await sectors_client.get("/most-traded/", params={"n_stock": 5})
            retrieved_data["most_traded"] = traded_res.get("data")
            credits_used += traded_res.get("_meta", {}).get("credits_consumed", 0)
            sources.append("/v2/most-traded/")

        summary = "Ringkasan pergerakan IHSG dan sektor pasar bursa terkini."

    # ----------------- 2. Single Stock Deepdive -----------------
    elif len(tickers) == 1:
        intent = "single_stock_deepdive"
        sym = tickers[0]

        # STEP A: Check Local DB / SQLite / JSON First!
        local_stock = await local_market_db.get_stock_locally(sym)
        if local_stock:
            logger.info("Serving %s from local DB/JSON (0 credits billed)", sym)
            retrieved_data[sym] = local_stock["data"]
            sources.append(f"local_storage ({local_stock['source']})")
        else:
            # STEP B: Missing locally -> Query Sectors API
            logger.info("Cache miss for %s. Querying Sectors API v2...", sym)
            rep_res = await sectors_client.get(f"/company/report/{sym}/", params={"sections": "overview,valuation,dividend"})
            retrieved_data["company_report"] = rep_res.get("data")
            credits_used += rep_res.get("_meta", {}).get("credits_consumed", 0)
            sources.append(f"/v2/company/report/{sym}/")

            flow_res = await sectors_client.get(f"/foreign-flow/{sym}/")
            retrieved_data["foreign_flow"] = flow_res.get("data")
            credits_used += flow_res.get("_meta", {}).get("credits_consumed", 0)
            sources.append(f"/v2/foreign-flow/{sym}/")

            # Persist newly fetched data to local DB & JSON store
            stock_record = {
                "symbol": sym,
                "company_report": rep_res.get("data"),
                "foreign_flow": flow_res.get("data")
            }
            await local_market_db.save_stock_locally(sym, stock_record)

        summary = f"Analisis data komprehensif emiten {sym} untuk perspektif bisnis."

    # ----------------- 3. Multi-Stock Comparison -----------------
    elif len(tickers) > 1:
        intent = "stock_comparison"
        all_found = True
        comp_data = {}

        # Check each stock locally first
        for sym in tickers:
            loc = await local_market_db.get_stock_locally(sym)
            if loc:
                comp_data[sym] = loc["data"]
            else:
                all_found = False

        if all_found and comp_data:
            logger.info("Serving comparison %s entirely from local DB", tickers)
            retrieved_data["comparison"] = comp_data
            sources.append("local_storage (sqlite/json)")
        else:
            symbols_str = ", ".join(f"'{t}'" for t in tickers)
            where_clause = f"symbol in [{symbols_str}]"
            comp_res = await sectors_client.get("/companies/", params={"where": where_clause})
            retrieved_data["comparison"] = comp_res.get("data")
            credits_used += comp_res.get("_meta", {}).get("credits_consumed", 0)
            sources.append("/v2/companies/")

        summary = f"Komparasi kinerja dan valuasi antara emiten: {', '.join(tickers)}."

    # ----------------- 4. Sector or Screener -----------------
    else:
        intent = "sector_screener"
        sub = payload.sub_sector or ("banks" if "bank" in text else "telecommunication" if "telko" in text else "consumer" if "konsumsi" in text else None)

        if sub:
            sec_res = await sectors_client.get(f"/subsector/report/{sub}/")
            retrieved_data["subsector_report"] = sec_res.get("data")
            credits_used += sec_res.get("_meta", {}).get("credits_consumed", 0)
            sources.append(f"/v2/subsector/report/{sub}/")
            summary = f"Riset mendalam subsektor '{sub}'."
        else:
            # Fallback natural language search
            scr_res = await sectors_client.get("/companies/", params={"q": payload.query, "limit": 5})
            retrieved_data["screener_results"] = scr_res.get("data")
            credits_used += scr_res.get("_meta", {}).get("credits_consumed", 0)
            sources.append("/v2/companies/?q=...")
            summary = "Pencarian emiten via Sectors Screener."

    # ----------------- 4.5 Multi-Country News Aggregation & Cross-Referencing -----------------
    if tickers:
        for t in tickers[:3]:
            n_items = await news_aggregator.get_news_context_for_ticker(t, limit=2)
            referenced_news.extend(n_items)
    if not referenced_news:
        referenced_news = await news_aggregator.get_headlines(country="ALL", limit=4)

    news_context_lines = []
    for n in referenced_news[:5]:
        news_context_lines.append(f"- [{n.get('source')} ({n.get('country')})] {n.get('title')} (Sentimen: {n.get('sentiment', 'NEUTRAL')})")
    news_context_str = "\n".join(news_context_lines) if news_context_lines else "Tidak ada headline langsung hari ini."

    # ----------------- 5. Garda AI Gemma 4 Concierge Synthesis -----------------
    user_prompt = f"""Konteks Pengguna: Pelaku usaha / UMKM / Investor (Industri: {payload.user_industry}).
Pertanyaan Pengguna: "{payload.query}"

LAPISAN 1: Data Pasar Modal Terverifikasi (Local Storage / Sectors Financial API):
{json.dumps(retrieved_data, indent=2, ensure_ascii=False)[:3000]}

LAPISAN 2: Berita Finansial Regional Terkini (20 Portal ID, SG, MY, JP):
{news_context_str}

Instruksi Concierge Garda (Sintesis Multi-Langkah: Hubungkan Data Pasar x Konteks Berita):
[GREETING]
Sapa pengguna secara hangat dan profesional ala concierge perbankan privat bintang lima.

[CONTEXT]
Jelaskan konteks industri atau saham yang dianalisis.

[INSIGHT]
Sajikan analisis data fundamental dan pergerakan harga dari Sectors API, lalu KORELASIKAN langsung dengan berita dari portal terkait (sebutkan nama portal: misal CNBC Indonesia, Bisnis.com, The Business Times, Nikkei Asia). Jelaskan hubungan sebab-akibat jika ada pergerakan pasar.

[BUSINESS & UMKM TAKEAWAY]
Jelaskan makna praktisnya bagi operasional bisnis/UMKM pengguna (daya beli, kesehatan mitra kerja, biaya bahan baku, atau cadangan dana).

[RECOMMENDATION / NEXT STEP]
Tawarkan opsi proaktif eksplorasi lanjutan (selalu berikan opsi, jangan rekomendasi beli/jual).

[CLOSING]
Penutup ramah concierge."""

    llm_answer = await garda_llm_client.chat_completion(
        messages=[
            {"role": "system", "content": GARDA_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.5,
        max_tokens=950
    )

    if llm_answer:
        summary = llm_answer
    else:
        summary = garda_llm_client.generate_concierge_fallback(
            query=payload.query,
            user_industry=payload.user_industry,
            retrieved_data=retrieved_data,
            referenced_news=referenced_news,
            tickers=tickers
        )


    return AgentQueryResponse(
        intent=intent,
        summary_insight=summary,
        target_entities=tickers,
        data_retrieved=retrieved_data if payload.include_raw_data else {},
        news_referenced=referenced_news,
        total_credits_used=credits_used,
        data_sources=sources
    )
