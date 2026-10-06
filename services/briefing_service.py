"""
Daily Market Briefing Generator.
Pulls Sectors API market highlights and constructs formatted WhatsApp/Portal briefing text.
"""
from typing import Dict, Any
from datetime import datetime
from core.sectors_client import sectors_client

async def generate_daily_market_briefing() -> Dict[str, Any]:
    """
    Constructs an automated morning/closing stock market summary:
    - Top 5 Gainers today
    - Top 5 Most traded stocks
    - Status & timestamp
    """
    now_str = datetime.now().strftime("%d %B %Y %H:%M WIB")

    # 1. Fetch Top Gainers (cached/fresh)
    gainers_res = await sectors_client.get(
        "/companies/top-changes/",
        params={"classifications": "top_gainers", "periods": "1d", "n_stock": 5},
        ttl_seconds=1800
    )
    gainers_data = gainers_res.get("data", [])

    # 2. Fetch Most Traded
    traded_res = await sectors_client.get(
        "/most-traded/",
        params={"n_stock": 5},
        ttl_seconds=1800
    )
    traded_data = traded_res.get("data", [])

    # Format WhatsApp Markdown Message
    msg_lines = []
    msg_lines.append("📊 *GARDA MARKET PULSE — BRIEFING PASAR SAHAM*")
    msg_lines.append(f"📅 Waktu: _{now_str}_\n")

    msg_lines.append("🚀 *Top 5 Saham Gainers Hari Ini:*")
    if isinstance(gainers_data, list) and gainers_data:
        for idx, item in enumerate(gainers_data[:5], 1):
            sym = item.get("symbol", "-")
            chg = item.get("price_change", 0)
            chg_str = f"+{chg*100:.2f}%" if isinstance(chg, (int, float)) else str(chg)
            price = item.get("last_close_price", "-")
            msg_lines.append(f"{idx}. *{sym}* | Rp {price:,} ({chg_str})" if isinstance(price, (int, float)) else f"{idx}. *{sym}* ({chg_str})")
    else:
        msg_lines.append("- _Data pasar sedang disinkronkan_")

    msg_lines.append("\n🔥 *Saham Paling Aktif (Volume Terbesar):*")
    if isinstance(traded_data, list) and traded_data:
        for idx, item in enumerate(traded_data[:5], 1):
            sym = item.get("symbol", "-")
            vol = item.get("volume", 0)
            vol_str = f"{vol:,} lot" if isinstance(vol, (int, float)) else str(vol)
            msg_lines.append(f"{idx}. *{sym}* — {vol_str}")
    else:
        msg_lines.append("- _Data volume pasar sedang diperbarui_")

    msg_lines.append("\n💡 _Disajikan otomatis oleh Garda AI Agent Gateway via Sectors API._")
    msg_lines.append("🔗 _Ketik 'analisis [TICKER]' untuk deep-dive fundamental emiten._")

    full_message = "\n".join(msg_lines)

    return {
        "timestamp": now_str,
        "message": full_message,
        "raw_gainers": gainers_data,
        "raw_traded": traded_data
    }
