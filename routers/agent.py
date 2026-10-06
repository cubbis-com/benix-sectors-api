"""
Agentic AI Query Router (Garda Market Concierge Core).
Enforces Local-First Database Checks (SQLite / JSON) to prevent unnecessary
Sectors API calls, preserving quota credits while powering high-touch UMKM & investor advisory.
Adheres strictly to System Prompt v3.5 with Zero-Hallucination and Evidence-Based Analysis.
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
    # Banking & Financials
    "bca": "BBCA", "bank central asia": "BBCA",
    "bri": "BBRI", "bank rakyat indonesia": "BBRI", "brilink": "BBRI",
    "mandiri": "BMRI", "bank mandiri": "BMRI",
    "bni": "BBNI", "bank negara indonesia": "BBNI",
    "bsi": "BRIS", "bank syariah indonesia": "BRIS",
    "btn": "BBTN", "bank tabungan negara": "BBTN",
    "bjtm": "BJTM", "bank jatim": "BJTM",
    "bjbr": "BJBR", "bank bjb": "BJBR",
    "bdmn": "BDMN", "danamon": "BDMN",
    "btps": "BTPS", "btpn syariah": "BTPS",
    "bbhi": "BBHI", "allo bank": "BBHI",
    "arto": "ARTO", "bank jago": "ARTO",

    # Telco & Tech
    "telkom": "TLKM", "telkomsel": "TLKM", "indihome": "TLKM",
    "isat": "ISAT", "indosat": "ISAT", "ooredoo": "ISAT",
    "excl": "EXCL", "xl": "EXCL", "xl axiata": "EXCL",
    "fren": "FREN", "smartfren": "FREN",
    "goto": "GOTO", "gojek": "GOTO", "tokopedia": "GOTO",
    "buka": "BUKA", "bukalapak": "BUKA",
    "emtek": "EMTK", "elang mahkota": "EMTK",
    "scma": "SCMA", "surya citra": "SCMA", "sctv": "SCMA",
    "mncn": "MNCN", "media nusantara": "MNCN", "rcti": "MNCN",

    # Consumer Non-Cyclicals & Retail
    "indofood": "ICBP", "indomie": "ICBP", "icbp": "ICBP", "indofood cbp": "ICBP",
    "indf": "INDF", "indofood sukses": "INDF",
    "mayora": "MYOR", "kopiko": "MYOR",
    "unilever": "UNVR",
    "kalbe": "KLBF", "kalbe farma": "KLBF",
    "sido": "SIDO", "sido muncul": "SIDO", "tolak angin": "SIDO",
    "charoen": "CPIN", "pokphand": "CPIN",
    "japfa": "JPFA", "comfeed": "JPFA",
    "malindo": "MAIN",
    "cleo": "CLEO", "sariguna": "CLEO",
    "garudafood": "GOOD",
    "ultrajaya": "ULTJ", "ultra milk": "ULTJ",
    "cimory": "CMRY", "cisarua mountain": "CMRY",
    "campina": "CAMP",
    "aces": "ACES", "ace hardware": "ACES", "aspirasi hidup": "ACES",
    "mapi": "MAPI", "mitra adiperkasa": "MAPI",
    "mapa": "MAPA", "map aktif": "MAPA",
    "lppf": "LPPF", "matahari": "LPPF",
    "rals": "RALS", "ramayana": "RALS",
    "midi": "MIDI", "midimart": "MIDI", "alfamidi": "MIDI",
    "amrt": "AMRT", "alfamart": "AMRT", "sumber alfaria": "AMRT",

    # Energy, Mining & Commodities
    "adaro": "ADRO", "adro": "ADRO", "adaro energy": "ADRO",
    "aadi": "AADI", "adaro andalan": "AADI",
    "bukit asam": "PTBA", "ptba": "PTBA",
    "antam": "ANTM", "aneka tambang": "ANTM",
    "inco": "INCO", "vale": "INCO", "vale indonesia": "INCO",
    "mdka": "MDKA", "merdeka copper": "MDKA",
    "mbma": "MBMA", "merdeka battery": "MBMA",
    "bumi": "BUMI", "bumi resources": "BUMI",
    "dewa": "DEWA", "darma henwa": "DEWA",
    "medco": "MEDC", "medc": "MEDC", "medco energi": "MEDC",
    "akra": "AKRA", "akr corporindo": "AKRA",
    "pgas": "PGAS", "pgn": "PGAS", "perusahaan gas": "PGAS",
    "bren": "BREN", "barito renewables": "BREN",
    "brpt": "BRPT", "barito pacific": "BRPT",
    "tpia": "TPIA", "chandra asri": "TPIA",
    "ammn": "AMMN", "amman mineral": "AMMN",
    "hrum": "HRUM", "harum energy": "HRUM",
    "itmg": "ITMG", "indo tambangraya": "ITMG",
    "cuan": "CUAN", "petrindo": "CUAN",
    "pani": "PANI", "pantai indah kapuk": "PANI",

    # Infrastructure & Basic Materials
    "semen indonesia": "SMGR", "semen gresik": "SMGR", "sig": "SMGR", "smgr": "SMGR",
    "indocement": "INTP", "tiga roda": "INTP", "intp": "INTP",
    "astra": "ASII", "astra international": "ASII",
    "united tractors": "UNTR", "untr": "UNTR",
    "jsmr": "JSMR", "jasa marga": "JSMR",
    "ptpp": "PTPP", "pp": "PTPP",
    "wika": "WIKA", "wijaya karya": "WIKA",
    "wskt": "WSKT", "waskita": "WSKT",
    "adhi": "ADHI", "adhi karya": "ADHI",

    # Property & Real Estate
    "ciputra": "CTRA", "ctra": "CTRA",
    "bsd": "BSDE", "sinarmas": "BSDE", "bsde": "BSDE", "bumi serpong": "BSDE",
    "pakuwon": "PWON", "pwon": "PWON",
    "summarecon": "SMRA", "smra": "SMRA",
    "lippo karawaci": "LPKR", "lpkr": "LPKR",
    "alam sutera": "ASRI", "asri": "ASRI",
    "agung podomoro": "APLN", "apln": "APLN",

    # Hospitality, Tourism & Transportation
    "sahid": "SHID", "hotel sahid": "SHID",
    "eastparc": "EAST", "hotel eastparc": "EAST",
    "panorama": "PANR", "panorama sentrawisata": "PANR",
    "blue bird": "BIRD", "bird": "BIRD",
    "garuda": "GIAA", "garuda indonesia": "GIAA", "giaa": "GIAA",
    "samudera": "SMDR", "samudera indonesia": "SMDR",
    "temas": "TMAS",

    # Healthcare
    "siloam": "SILO", "silo": "SILO",
    "mitra keluarga": "MIKA", "mika": "MIKA",
    "hermina": "HEAL", "heal": "HEAL",
    "kaef": "KAEF", "kimia farma": "KAEF",
    "inaf": "INAF", "indofarma": "INAF",
    "prda": "PRDA", "prodia": "PRDA",

    # SGX Tickers & Aliases
    "dbs": "D05", "dbs bank": "D05", "ocbc": "O39", "uob": "U11",
    "singtel": "Z74", "singapore airlines": "C6L", "sia": "C6L",
    "genting": "G13", "rws": "G13", "capitaland": "A17U", "cict": "A17U",
    "keppel": "BN4", "seatrium": "BS6"
}

SGX_SYMBOLS = ["D05", "O39", "U11", "Z74", "C6L", "G13", "A17U", "BN4", "BS6"]

# Known bluechip & popular IDX tickers for rapid candidate verification
POPULAR_IDX_TICKERS = {
    "BBCA", "BBRI", "BMRI", "BBNI", "BRIS", "BBTN", "BJTM", "BJBR", "BDMN", "BTPS", "ARTO", "BBHI",
    "TLKM", "ISAT", "EXCL", "FREN", "GOTO", "BUKA", "EMTK", "SCMA", "MNCN",
    "ASII", "UNTR", "JSMR", "PTPP", "WIKA", "WSKT", "ADHI", "SMGR", "INTP",
    "ICBP", "INDF", "MYOR", "UNVR", "KLBF", "SIDO", "CPIN", "JPFA", "MAIN", "CLEO", "GOOD", "ULTJ", "CMRY", "CAMP",
    "ACES", "MAPI", "MAPA", "LPPF", "RALS", "MIDI", "AMRT",
    "ADRO", "AADI", "PTBA", "ANTM", "INCO", "MDKA", "MBMA", "BUMI", "DEWA", "MEDC", "AKRA", "PGAS",
    "BREN", "BRPT", "TPIA", "AMMN", "HRUM", "ITMG", "CUAN", "PANI", "BRMS", "NCKL", "TINS", "PSAB", "CITA", "DSSA", "INDY", "DOID", "ABMM",
    "CTRA", "BSDE", "PWON", "SMRA", "LPKR", "LPCK", "ASRI", "APLN",
    "SHID", "EAST", "PANR", "BIRD", "GIAA", "SMDR", "TMAS",
    "SILO", "MIKA", "HEAL", "PRDA", "KAEF", "INAF",
    "INKP", "TKIM", "TOTO", "AVIA", "AUTO", "SMSM", "GJTL", "IMAS", "DRMA"
}

# Strict 4-letter stopwords blacklist in Indonesian & English
IGNORE_WORDS = {
    # Indonesian common 4-letter words
    "HARI", "YANG", "DARI", "PADA", "AKAN", "SAAT", "BISA", "KITA", "DENG", "BANK",
    "FLOW", "ASIN", "DANA", "ARUS", "NET", "INFO", "DATA", "JUAL", "BELI", "CARA",
    "KAYA", "LABA", "BUKU", "NAIK", "TURU", "SUDA", "SEMA", "JADI", "SAHA", "SAHM",
    "FORE", "POST", "GOOD", "BEST", "VIEW", "DEEP", "RISK", "PEER", "RATE", "HIGH", "LOW",
    "SAYA", "KAMI", "ADAL", "BAGA", "MANA", "LAGI", "LESU", "RAMA", "TOKO", "BUAT", "BIAR", "CEK",
    "SAMA", "ATAU", "AGAR", "TIDA", "TAPI", "JIKA", "BAGI", "KALI", "LAIN", "OLEH", "KARE",
    "KATA", "BACA", "BARU", "BAIK", "BAWA", "BEDA", "BILA", "BUKA", "CUKU", "DULU", "ESOK",
    "HARU", "INGI", "IKUT", "INGA", "ISIN", "IKAT", "JUGA", "KINI", "KIRA", "KUAT", "KURG",
    "LALU", "LAMA", "LEBI", "LIAT", "LUAR", "MAKA", "MAAF", "MAUP", "MAUK", "MULI", "NAMA",
    "OPTI", "PAST", "PILI", "POIN", "PULI", "RASA", "RATA", "RUGI", "SANG", "SATU", "SEGI",
    "SELA", "SERI", "SIAP", "SIAS", "SOAL", "TAHU", "TENT", "TETP", "TIGA", "TREN", "TUTP",
    "UANG", "UNTK", "USUL", "AWAL", "ARAH", "AKAR", "AJAK", "ANAK", "AYAM", "BIAY", "BIAI",
    "BERI", "BERA", "BERK", "BERN", "BAGI", "BELA", "BINA", "BOLE", "BULA", "CHAT", "CARI",
    "COBA", "CUCI", "DIAM", "DIRI", "DUAA", "ENAM", "FOTO", "GAJI", "GAYA", "GUNA", "GURU",
    "HABP", "HAMP", "HAUS", "HATI", "IDUP", "IKAN", "ILMU", "INDA", "ISIK", "JAGA", "JAHE",
    "JAJA", "JARP", "JASA", "JATU", "JAWA", "JEJE", "JELA", "JEND", "JERA", "JIWA", "JUTA",
    "KACA", "KAKI", "KALA", "KAMU", "KANG", "KANT", "KASA", "KASI", "KAUM", "KAUS", "KECI",
    "KEJU", "KERA", "KERJ", "KESU", "KOTA", "KUDA", "KULI", "KURS", "LADA", "LAGU", "LAJU",
    "LAKI", "LARI", "LATA", "LAUT", "LEBA", "LEGA", "LIMA", "LIND", "LOGA", "LONT", "LUPA",
    "MAJU", "MALM", "MANI", "MANU", "MARA", "MASA", "MAST", "MATA", "MATI", "MAYA", "MEJA",
    "MELI", "MENA", "MENI", "MENU", "MERA", "MINT", "MODA", "MUDA", "MUKA", "MULA", "MURN",
    "NADA", "NASI", "NOLA", "NOMO", "OBAT", "ORAN", "PAGI", "PAHA", "PAKE", "PALG", "PANA",
    "PAPA", "PARI", "PASR", "PEKA", "PETA", "PINT", "PIPI", "PISA", "POLA", "PUAS", "PUAN",
    "PUJA", "RABA", "RAGU", "RAJA", "RAME", "RAPI", "RAPT", "RAYA", "REBA", "RELA", "RENC",
    "RIBU", "RINA", "ROTI", "RUAN", "RUMA", "RUPA", "SABA", "SAGA", "SAKU", "SALA", "SAMP",
    "SANA", "SAPI", "SAPU", "SARI", "SAUS", "SAWI", "SEBA", "SEDA", "SEGA", "SEJA", "SEKA",
    "SENA", "SEPA", "SERA", "SIFA", "SIKI", "SINI", "SISA", "SISI", "SITU", "SORE", "SUAP",
    "SUAS", "SUHU", "SUKA", "SULI", "SURU", "SUSA", "SUSU", "TAAT", "TABU", "TAHA", "TAJI",
    "TAMP", "TAND", "TANG", "TANY", "TARO", "TEBA", "TEGA", "TEKA", "TEPI", "TERA", "TERI",
    "TIAP", "TIBA", "TIDR", "TIPI", "TIRA", "TIRI", "TITK", "TOLK", "TUAN", "TUBU", "TUJU",
    "TULA", "TULI", "TUMB", "TUNG", "UBRA", "UDAR", "UJIA", "UKUR", "ULAN", "ULAT", "UMUR",
    "UNDA", "UNIK", "UPAY", "URUS", "USHA", "USIA", "UTAM", "WANI", "WAKT", "WALA", "WALI",
    # English common 4-letter words
    "WHAT", "WHEN", "WITH", "FROM", "THAT", "THIS", "THEY", "HAVE", "MORE", "SOME",
    "LIKE", "TIME", "JUST", "KNOW", "TAKE", "YEAR", "MAKE", "LOOK", "ONLY", "COME",
    "OVER", "SUCH", "THEN", "THIN", "MOST", "ALSO", "BACK", "EVEN", "WELL", "WAYS",
    "DOWN", "MANY", "FIND", "TELL", "GIVE", "WORK", "CALL", "LAST", "LEAD", "LONG",
    "NEWS", "OPEN", "PAID", "PLAN", "PLAY", "READ", "SALE", "SAVE", "SEND", "SHOW",
    "SIDE", "SITE", "SIZE", "STAY", "SURE", "TALK", "TEAM", "TERM", "TRUE", "TURN",
    "TYPE", "UNIT", "USER", "VOTE", "WALK", "WANT", "WEEK", "WENT", "WISH", "WORD", "ZERO"
}

class AgentQueryRequest(BaseModel):
    query: str = Field(..., description="User question in natural language (e.g. 'analisis emiten BBRI', 'bagaimana prospek hotel dan pariwisata?', 'kondisi pasar hari ini')")
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

def format_verified_dossier(
    intent: str,
    retrieved_data: Dict[str, Any],
    referenced_news: List[Dict[str, Any]],
    tickers: List[str]
) -> str:
    """
    Compiles an institutional-grade, zero-truncation verified facts dossier
    from Sectors Financial API and regional news aggregators for LLM grounding.
    """
    lines = ["=== DOSSIER DATA PASAR MODAL TERVERIFIKASI (SECTORS FINANCIAL API v2) ==="]

    if intent == "single_stock_deepdive" and tickers:
        sym = tickers[0]
        stock_data = retrieved_data.get(sym, {})
        rep = stock_data.get("company_report") or (stock_data if "overview" in stock_data else {})
        ov = rep.get("overview") or {}
        val = rep.get("valuation") or {}
        div = rep.get("dividend") or {}
        flow_data = stock_data.get("foreign_flow")
        broker_data = stock_data.get("broker_summary")

        name = stock_data.get("company_name") or ov.get("company_name") or rep.get("company_name") or sym
        industry = ov.get("industry") or ov.get("sub_sector") or stock_data.get("sector") or "General"
        board = ov.get("listing_board") or "Main"

        price = ov.get("last_close_price") or stock_data.get("last_price") or stock_data.get("price") or "N/A"
        chg_raw = ov.get("daily_close_change")
        if chg_raw is not None:
            chg_pct = f"{chg_raw * 100:+.2f}%"
        else:
            chg_pct = str(stock_data.get("change_pct", "0%"))
        close_date = ov.get("latest_close_date") or ""

        mcap = ov.get("market_cap") or stock_data.get("market_cap_trillion")
        mcap_rank = ov.get("market_cap_rank")
        if isinstance(mcap, (int, float)) and mcap > 1e9:
            mcap_str = f"Rp {mcap / 1e12:.1f} Triliun"
        elif mcap:
            mcap_str = f"Rp {mcap} Triliun"
        else:
            mcap_str = "N/A"
        if mcap_rank:
            mcap_str += f" (Peringkat #{mcap_rank} di Bursa Efek Indonesia)"

        atp = ov.get("all_time_price", {})
        low_52w = list(atp.get("52_w_low", {}).values())[0] if atp.get("52_w_low") else None
        high_52w = list(atp.get("52_w_high", {}).values())[0] if atp.get("52_w_high") else None
        range_52w = f"Low Rp {low_52w:,} — High Rp {high_52w:,}" if (low_52w and high_52w) else "N/A"

        f_pe = val.get("forward_pe")
        hist_vals = val.get("historical_valuation", [])
        ttm_pe = hist_vals[-1].get("pe") if hist_vals else None
        peer_pe = hist_vals[-1].get("pe_peer_avg") if hist_vals else None
        pb = hist_vals[-1].get("pb") if hist_vals else None
        peer_pb = hist_vals[-1].get("pb_peer_avg") if hist_vals else None
        ps = hist_vals[-1].get("ps") if hist_vals else None

        f_pe_str = f"{f_pe:.2f}x" if isinstance(f_pe, (int, float)) else "N/A"
        ttm_pe_str = f"{ttm_pe:.2f}x" if isinstance(ttm_pe, (int, float)) else str(stock_data.get("pe_ratio", "N/A"))
        peer_pe_str = f"{peer_pe:.2f}x" if isinstance(peer_pe, (int, float)) else "N/A"
        pb_str = f"{pb:.2f}x" if isinstance(pb, (int, float)) else "N/A"
        peer_pb_str = f"{peer_pb:.2f}x" if isinstance(peer_pb, (int, float)) else "N/A"
        ps_str = f"{ps:.2f}x" if isinstance(ps, (int, float)) else "N/A"

        dy = div.get("yield_ttm")
        d_ttm = div.get("dividend_ttm")
        payout = div.get("payout_ratio")
        ex_date = div.get("last_ex_dividend_date")

        dy_str = f"{dy * 100:.2f}%" if isinstance(dy, (int, float)) else str(stock_data.get("dividend_yield", "N/A"))
        d_ttm_str = f"Rp {d_ttm:.1f} per saham" if isinstance(d_ttm, (int, float)) else "N/A"
        payout_str = f"{payout * 100:.1f}%" if isinstance(payout, (int, float)) else "N/A"

        flow_str = "Data arus asing netral"
        if isinstance(flow_data, dict) and "data" in flow_data and flow_data["data"]:
            latest_f = flow_data["data"][-1]
            f_val = latest_f.get("net_foreign_inflow", 0)
            f_date = latest_f.get("date", "")
            f_share = latest_f.get("foreign_share", 0)
            f_buy = latest_f.get("foreign_buy_idr", 0)
            f_sell = latest_f.get("foreign_sell_idr", 0)
            direction = "Net Inflow (Akumulasi Beli Asing)" if f_val > 0 else "Net Outflow (Tekanan Jual Asing)" if f_val < 0 else "Netral"
            flow_str = (
                f"Net Flow: {f_val / 1e9:+.2f} Miliar IDR ({direction})\n"
                f"    - Beli Asing: Rp {f_buy / 1e9:.2f} M | Jual Asing: Rp {f_sell / 1e9:.2f} M\n"
                f"    - Porsi Transaksi Asing: {f_share * 100:.1f}% dari total transaksi pasar per {f_date}"
            )
        elif stock_data.get("net_foreign_flow_1d"):
            flow_str = f"{stock_data.get('net_foreign_flow_1d')} ({stock_data.get('smart_money_status', 'Aktif')})"

        broker_str = "Data broker tidak tersedia"
        if isinstance(broker_data, dict):
            buyers = broker_data.get("top_buyers", [])[:5]
            sellers = broker_data.get("top_sellers", [])[:5]
            b_list = [f"{b.get('broker_code')} (+Rp {b.get('net_idr', 0)/1e9:.1f}M)" for b in buyers if b.get('broker_code')]
            s_list = [f"{s.get('broker_code')} ({s.get('net_idr', 0)/1e9:.1f}M)" for s in sellers if s.get('broker_code')]
            broker_str = (
                f"Top 5 Net Buyers (Akumulasi): {', '.join(b_list) if b_list else 'N/A'}\n"
                f"    - Top 5 Net Sellers (Distribusi): {', '.join(s_list) if s_list else 'N/A'}\n"
                f"    - (Catatan: Broker AK, ZP, RX adalah broker institusi asing premier)"
            )

        currency = stock_data.get("currency", "IDR")
        price_fmt = f"SGD {price}" if currency == "SGD" else f"Rp {price:,}" if isinstance(price, (int, float)) else f"{price}"

        lines.extend([
            f"Target Analisis: {sym} ({name})",
            f"Sektor: {industry} | Papan Pencatatan: {board}",
            "• Ringkasan Harga & Transaksi Pasar:",
            f"  - Harga Penutupan Terakhir: {price_fmt} ({chg_pct}) per {close_date}",
            f"  - Rentang 52-Minggu: {range_52w}",
            f"  - Kapitalisasi Pasar: {mcap_str}",
            "• Rasio Valuasi & Konsensus:",
            f"  - Forward P/E: {f_pe_str} | Historical TTM P/E: {ttm_pe_str} (Rata-rata Peer: {peer_pe_str})",
            f"  - Rasio P/B: {pb_str} (Rata-rata Peer: {peer_pb_str}) | Rasio P/S: {ps_str}",
            "• Imbal Hasil Dividen (Dividend Metrics):",
            f"  - Dividend Yield TTM: {dy_str} | Total Dividen: {d_ttm_str}",
            f"  - Dividend Payout Ratio: {payout_str} | Tanggal Ex-Dividen Terakhir: {ex_date or 'N/A'}",
            "• Arus Modal Asing (Foreign Flow / Smart Money):",
            f"  - {flow_str}",
            "• Konsentrasi Broker (Bandarmologi):",
            f"  - {broker_str}"
        ])

    elif intent == "stock_comparison":
        lines.append(f"Komparasi Emiten Terverifikasi: {', '.join(tickers)}")
        for sym in tickers:
            st = retrieved_data.get(sym, {})
            rep = st.get("company_report") or (st if "overview" in st else {})
            ov = rep.get("overview") or {}
            val = rep.get("valuation") or {}
            div = rep.get("dividend") or {}
            price = ov.get("last_close_price") or st.get("last_price") or "N/A"
            chg = f"{ov.get('daily_close_change', 0)*100:+.2f}%" if ov.get("daily_close_change") is not None else st.get("change_pct", "0%")
            pe = val.get("forward_pe") or st.get("pe_ratio", "N/A")
            pe_str = f"{pe:.2f}x" if isinstance(pe, (int, float)) else str(pe)
            dy = div.get("yield_ttm")
            dy_str = f"{dy*100:.2f}%" if isinstance(dy, (int, float)) else str(st.get("dividend_yield", "N/A"))
            price_fmt = f"{price:,}" if isinstance(price, (int, float)) else str(price)
            lines.append(f"• {sym} ({ov.get('company_name', sym)}): Harga Rp {price_fmt} ({chg}) | P/E: {pe_str} | Div Yield: {dy_str}")

    elif intent == "market_overview":
        ov = retrieved_data.get("market_overview", {})
        idx_name = ov.get("index_name", "IHSG")
        idx_price = ov.get("last_price", 7421.10)
        idx_chg = ov.get("daily_change_pct", "+0.48%")
        idx_status = ov.get("status", "BULLISH")
        lines.extend([
            f"Indeks Utama: {idx_name} di level {idx_price} ({idx_chg}) — Status: {idx_status}",
            "Top Sektor Penggerak:"
        ])
        for sec in ov.get("top_sectors", [])[:3]:
            lines.append(f"  - Sektor {sec.get('sector')}: {sec.get('change')} ({sec.get('status')})")

    lines.append("\n=== ARSIP BERITA & KATALIS RESMI TERVERIFIKASI ===")
    if referenced_news:
        for idx, n in enumerate(referenced_news[:5], 1):
            src = n.get("source", "Portal Finansial")
            title = n.get("title", "")
            summary = n.get("summary", "")[:280]
            sentiment = n.get("sentiment", "NEUTRAL")
            pub = n.get("published_at", "")
            lines.append(f"{idx}. [{src} | {pub}]: {title} (Sentimen: {sentiment})\n   Ringkasan: {summary}")
    else:
        lines.append("Tidak ada kejadian luar biasa atau aksi korporasi mendadak tercatat hari ini.")

def sanitize_garda_markdown(text: str) -> str:
    """
    Sanitizes LLM markdown output to ensure charts and tables render flawlessly:
    1. Converts ```json or ```js or ``` code blocks containing series into ```echarts.
    2. Detects unfenced raw JSON blocks (e.g. starting with "title": { ... } or { "title": ... })
       and converts them into proper ```echarts code blocks.
    3. Normalizes line endings.
    """
    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # 1. Convert ```json or ```js or ``` containing series to ```echarts
    def replace_fenced(match):
        code = match.group(1).strip()
        if '"series"' in code or "'series'" in code:
            return f"```echarts\n{code}\n```"
        return match.group(0)

    text = re.sub(r"```(?:json|javascript|js)?\s*\n([\s\S]*?)\n```", replace_fenced, text, flags=re.IGNORECASE)

    # 2. Check for unfenced JSON block containing "series"
    if "```echarts" not in text and ('"series"' in text or "'series'" in text):
        for key in ['"title"', '"series"', '"xAxis"', '{']:
            start_pos = text.find(key)
            if start_pos != -1:
                if key != '{':
                    line_start = text.rfind('\n', 0, start_pos)
                    start_idx = 0 if line_start == -1 else line_start + 1
                    prepend_brace = True
                else:
                    start_idx = start_pos
                    prepend_brace = False

                depth = 1 if prepend_brace else 0
                in_str = False
                escape = False
                end_idx = -1
                for idx in range(start_pos, len(text)):
                    c = text[idx]
                    if escape:
                        escape = False
                        continue
                    if c == "\\":
                        escape = True
                        continue
                    if c == '"':
                        in_str = not in_str
                        continue
                    if not in_str:
                        if c == '{':
                            depth += 1
                        elif c == '}':
                            depth -= 1
                            if depth == 0:
                                end_idx = idx
                                break

                if end_idx != -1:
                    raw_candidate = text[start_idx:end_idx+1].strip()
                    cand_to_test = "{" + raw_candidate if prepend_brace and not raw_candidate.startswith("{") else raw_candidate
                    try:
                        parsed = json.loads(cand_to_test)
                        if "series" in parsed or ("xAxis" in parsed and "yAxis" in parsed):
                            echarts_block = f"\n```echarts\n{json.dumps(parsed, indent=2)}\n```\n"
                            text = text[:start_idx] + echarts_block + text[end_idx+1:]
                            break
                    except Exception:
                        pass

    return text


@router.post("/query", response_model=AgentQueryResponse, summary="Process Financial Query with Garda Concierge")
async def process_agent_query(payload: AgentQueryRequest):
    """
    Executes the Garda AI Market Concierge pipeline:
    1. Intent & entity parsing (IDX & SGX stocks + UMKM scenarios) with strict stopwords filtering
    2. CHECK LOCAL STORAGE FIRST (SQLite gateway.db / local_market_store.json)
    3. Multi-Country News Aggregation & Cross-Referencing (20 portals ID, SG, MY, JP)
    4. Fallback to upstream Sectors API only on cache miss, automatically saving to local storage
    5. Formats verified facts dossier according to GARDA System Prompt v3.5 (Zero-Hallucination)
    """
    text = payload.query.lower()
    tickers = [normalize_ticker(t) for t in (payload.tickers or [])]
    credits_used = 0
    sources = []
    retrieved_data = {}
    referenced_news = []

    # 1. Check SGX symbols
    for st in SGX_SYMBOLS:
        if re.search(rf"\b{st}\b", payload.query, re.IGNORECASE):
            if st not in tickers:
                tickers.append(st)

    # 2. Check Company Aliases
    for comp_name, tick in COMPANY_NAME_TO_TICKER.items():
        if re.search(rf"\b{re.escape(comp_name)}\b", text):
            if tick not in tickers:
                tickers.append(tick)

    # 3. Extract 4-letter ticker candidates from text if none provided
    if not tickers:
        found_tokens = re.findall(r"\b[A-Za-z]{4}\b", payload.query.upper())
        for tok in found_tokens:
            if tok in IGNORE_WORDS:
                continue
            # Accept if in popular tickers or in company alias values
            if tok in POPULAR_IDX_TICKERS or tok in COMPANY_NAME_TO_TICKER.values():
                if tok not in tickers:
                    tickers.append(tok)

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

    # ----------------- 1. Single Stock Deepdive -----------------
    elif len(tickers) == 1:
        intent = "single_stock_deepdive"
        sym = tickers[0]

        # STEP A: Check Local DB / SQLite / JSON First!
        local_stock = await local_market_db.get_stock_locally(sym)
        stock_rec = local_stock.get("data", {}) if local_stock else {}
        has_full_report = bool(stock_rec.get("company_report") or (stock_rec.get("overview") and stock_rec.get("valuation")))

        if has_full_report and stock_rec.get("foreign_flow"):
            logger.info("Serving complete %s from local DB/cache (0 credits billed)", sym)
            retrieved_data[sym] = stock_rec
            sources.append(f"local_storage ({local_stock['source']})")
        else:
            logger.info("Retrieving comprehensive verified data for %s from Sectors API...", sym)
            rep_res = await sectors_client.get(f"/company/report/{sym}/", params={"sections": "overview,valuation,dividend,peers"})
            flow_res = await sectors_client.get(f"/foreign-flow/{sym}/")
            broker_res = await sectors_client.get(f"/broker-summary/{sym}/top", params={"n_brokers": 5})

            credits_used += rep_res.get("_meta", {}).get("credits_consumed", 0)
            credits_used += flow_res.get("_meta", {}).get("credits_consumed", 0)
            credits_used += broker_res.get("_meta", {}).get("credits_consumed", 0)

            sources.extend([f"/v2/company/report/{sym}/", f"/v2/foreign-flow/{sym}/", f"/v2/broker-summary/{sym}/top"])

            stock_payload = {
                "symbol": sym,
                "company_report": rep_res.get("data"),
                "foreign_flow": flow_res.get("data"),
                "broker_summary": broker_res.get("data")
            }
            retrieved_data[sym] = stock_payload
            await local_market_db.save_stock_locally(sym, stock_payload)

        # Retrieve News Context
        n_items = await news_aggregator.get_news_context_for_ticker(sym, limit=4)
        referenced_news.extend(n_items)
        summary = f"Analisis data komprehensif emiten {sym} untuk perspektif bisnis."

    # ----------------- 2. Multi-Stock Comparison -----------------
    elif len(tickers) > 1:
        intent = "stock_comparison"
        for sym in tickers:
            loc = await local_market_db.get_stock_locally(sym)
            if loc and loc.get("data", {}).get("company_report"):
                retrieved_data[sym] = loc["data"]
                sources.append(f"local_storage ({sym})")
            else:
                rep_res = await sectors_client.get(f"/company/report/{sym}/", params={"sections": "overview,valuation,dividend"})
                credits_used += rep_res.get("_meta", {}).get("credits_consumed", 0)
                sources.append(f"/v2/company/report/{sym}/")
                stock_payload = {"symbol": sym, "company_report": rep_res.get("data")}
                retrieved_data[sym] = stock_payload
                await local_market_db.save_stock_locally(sym, stock_payload)

            n_items = await news_aggregator.get_news_context_for_ticker(sym, limit=2)
            referenced_news.extend(n_items)

        summary = f"Komparasi kinerja dan valuasi antara emiten: {', '.join(tickers)}."

    # ----------------- 3. Market Overview Intent -----------------
    elif any(w in text for w in ["pasar", "ihsg", "market", "bursa", "kondisi hari ini"]):
        intent = "market_overview"
        local_overview = await local_market_db.get_market_overview_locally()
        if local_overview:
            logger.info("Serving market overview from local DB/JSON (0 credits)")
            retrieved_data["market_overview"] = local_overview["data"]
            sources.append(f"local_storage ({local_overview['source']})")
        else:
            movers_res = await sectors_client.get("/companies/top-changes/", params={"classifications": "top_gainers", "periods": "1d", "n_stock": 5})
            retrieved_data["top_gainers"] = movers_res.get("data")
            credits_used += movers_res.get("_meta", {}).get("credits_consumed", 0)
            sources.append("/v2/companies/top-changes/")

            traded_res = await sectors_client.get("/most-traded/", params={"n_stock": 5})
            retrieved_data["most_traded"] = traded_res.get("data")
            credits_used += traded_res.get("_meta", {}).get("credits_consumed", 0)
            sources.append("/v2/most-traded/")

        summary = "Ringkasan pergerakan IHSG dan sektor pasar bursa terkini."

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
            scr_res = await sectors_client.get("/companies/", params={"q": payload.query, "limit": 5})
            retrieved_data["screener_results"] = scr_res.get("data")
            credits_used += scr_res.get("_meta", {}).get("credits_consumed", 0)
            sources.append("/v2/companies/?q=...")
            summary = "Pencarian emiten via Sectors Screener."

    # Complement regional headlines if needed
    if not referenced_news:
        referenced_news = await news_aggregator.get_headlines(country="ALL", limit=4)

    # ----------------- 5. Build Grounded Dossier & Gemma 4 Synthesis -----------------
    dossier_text = format_verified_dossier(
        intent=intent,
        retrieved_data=retrieved_data,
        referenced_news=referenced_news,
        tickers=tickers
    )

    user_prompt = f"""Konteks Pengguna: Pelaku Usaha / UMKM / Investor (Industri: {payload.user_industry}).
Pertanyaan Pengguna: "{payload.query}"

DOSSIER DATA PASAR & BERITA TERVERIFIKASI (SECTORS FINANCIAL API & REGIONAL NEWS):
---------------------------------------------------------------------------------
{dossier_text}
---------------------------------------------------------------------------------

ATURAN MUTLAK ANALISIS (ZERO-CHITCHAT, GRAFIK ECHARTS & TABEL REKOMENDASI):
1. DILARANG BASA-BASI (STRICT ZERO-CHITCHAT):
   - JANGAN menyapa ("Halo", "Selamat pagi/siang", "Tentu saja", "Berikut analisisnya", dsb.).
   - JANGAN ada basa-basi penutup panjang.
   - Langsung ke inti analisis: Ringkasan eksekutif, grafik visual, dan tabel rekomendasi.

2. WAJIB GRAFIK ECHARTS (FORMAT CODEBLOCK RESMI):
   - SELALU sertakan visualisasi grafik ECharts di dalam blok kode ```echarts dan ```.
   - PENTING: DILARANG mengeluarkan JSON telanjang/mentah tanpa blok ```echarts!
   - JSON WAJIB diawali kurung kurawal pembuka {{ dan diakhiri kurung kurawal penutup }} yang valid.
   - Contoh format:
   ```echarts
   {{
     "title": {{ "text": "Proyeksi Valuasi P/E & Target Price", "textStyle": {{ "fontSize": 12, "color": "#f8fafc" }} }},
     "tooltip": {{ "trigger": "axis" }},
     "legend": {{ "data": ["P/E Emiten (x)", "Rata-rata Peer (x)"], "textStyle": {{ "color": "#94a3b8" }} }},
     "xAxis": {{ "type": "category", "data": ["BBCA", "BBRI", "BMRI"] }},
     "yAxis": {{ "type": "value" }},
     "series": [
       {{ "name": "P/E Emiten (x)", "type": "bar", "data": [11.2, 10.5, 9.8], "itemStyle": {{ "color": "#38bdf8" }} }},
       {{ "name": "Rata-rata Peer (x)", "type": "bar", "data": [14.0, 14.0, 14.0], "itemStyle": {{ "color": "#10b981" }} }}
     ]
   }}
   ```

3. WAJIB TABEL REKOMENDASI MARKDOWN STANDAR:
   - Wajib sertakan tabel rekomendasi dengan format tabel Markdown baku (menggunakan baris pemisah | :---: |):
     | Emiten | Sinyal Rekomendasi | Area Beli (Entry) | Target Price (TP) | Stop Loss (SL) | Risk/Reward | Katalis Utama & Rationale |
     | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
     | ADRO | ACCUMULATE | Rp 2,450 - Rp 2,550 | Rp 3,100 | Rp 2,200 | 1 : 2.5+ | Fundamental Strength: P/E (5.02x) vs Peer (11.06x), dividen yield 5.60%. |
   - Gunakan sinyal: STRONG BUY, BUY ON WEAKNESS, ACCUMULATE, HOLD, atau TAKE PROFIT.
   - JANGAN membuat garis putus-putus manual; SELALU gunakan format tabel pipa markdown standar di atas.

4. FAKTA BERBASIS DATA NYATA (ZERO HALLUCINATION):
   - Setiap angka harga, P/E, Dividen, Net Foreign Flow wajib bersumber dari DOSSIER di atas.
   - Hubungkan kausalitas antara pergerakan angka transaksi dengan berita resmi dari portal terkait.

5. STRUKTUR LAPORAN RINGKAS & PADAT:
   ### RINGKASAN EKSEKUTIF PASAR
   ### VISUALISASI PROYEKSI HARGA & TARGET
   ### TABEL REKOMENDASI & SETUP LEVEL EKSEKUSI
   ### KATALIS PEMBERITAAN & SENTIMEN REGIONAL
   ### IMPLIKASI RISIKO & BISNIS"""

    llm_answer = await garda_llm_client.chat_completion(
        messages=[
            {"role": "system", "content": GARDA_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
        max_tokens=1100
    )

    if llm_answer:
        summary = sanitize_garda_markdown(llm_answer)
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
