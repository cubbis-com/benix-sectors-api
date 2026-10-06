"""
Financial Journalist AI Agent (Wartawan Pasar Modal).
Transforms raw financial data and analyst models into professional Indonesian financial news articles.
"""
from datetime import datetime
from typing import Dict, Any, List
import re

class FinancialJournalistAgent:
    """Specialized Journalist Agent adhering to Indonesian financial journalism standards (Kontan/Bisnis/CNBC)."""

    @staticmethod
    def _create_slug(title: str) -> str:
        s = title.lower()
        s = re.sub(r"[^a-z0-9\s-]", "", s)
        s = re.sub(r"[\s-]+", "-", s).strip("-")
        date_str = datetime.now().strftime("%Y%m%d%H%M")
        return f"{s}-{date_str}"

    @classmethod
    def write_stock_deepdive_article(
        cls,
        symbol: str,
        stock_data: Dict[str, Any],
        trader_insight: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Crafts a comprehensive editorial deep-dive article for an individual IDX stock."""
        now = datetime.now().strftime("%d %B %Y")
        company_name = trader_insight.get("company_name", symbol)
        last_price = trader_insight.get("last_price", 0)
        market_cap = trader_insight.get("market_cap", 0)
        bias = trader_insight.get("bias", "NEUTRAL")
        bandar = trader_insight.get("bandarmology_status", "BALANCED")
        foreign_idr = trader_insight.get("foreign_flow_net_idr", 0)
        levels = trader_insight.get("key_levels", {})

        mcap_trillion = round(market_cap / 1_000_000_000_000, 2) if market_cap else 0
        foreign_billion = round(foreign_idr / 1_000_000_000, 2) if foreign_idr else 0

        # Dynamic Headline
        if bias == "BULLISH":
            headline = f"Akumulasi Asing & Smart Money Menguat, Valuasi Saham {symbol} ({company_name}) Kian Menarik"
            tone_word = "menunjukkan tren penguatan signifikan"
        elif bias == "BEARISH":
            headline = f"Tekanan Distribusi Membayangi {symbol} ({company_name}), Investor Cermati Level Support"
            tone_word = "berada dalam fase konsolidasi tertekan"
        else:
            headline = f"Membedah Prospek Fundamental dan Pergerakan Arus Dana Saham {symbol} ({company_name})"
            tone_word = "bergerak cenderung defensif dan stabil"

        slug = cls._create_slug(f"analisis-saham-{symbol}-{bias.lower()}")

        # Content Assembly
        content_lines = []
        content_lines.append(f"# {headline}\n")
        content_lines.append(f"**JAKARTA, {now} — GARDA FINANCIAL DESK** — Pergerakan saham {company_name} (IDX: `{symbol}`) {tone_word} di tengah dinamika bursa saham domestik. Berdasarkan kompilasi data analitik dari Sectors Financial API, emiten ini membukukan kapitalisasi pasar sebesar **Rp {mcap_trillion:,.2f} Triliun** dengan harga penutupan terakhir di level **Rp {last_price:,}** per lembar saham.\n")

        content_lines.append("### 📊 Sorotan Fundamental & Rasio Valuasi")
        content_lines.append(f"Emiten yang bergerak di sektor strategis ini menawarkan profil keuangan yang dicermati para investor:")
        pe = trader_insight.get("pe_ratio")
        pe_str = f"{pe:.2f}x" if pe else "N/A"
        yield_pct = trader_insight.get("dividend_yield_pct", 0)
        content_lines.append(f"- **Rasio Price to Earnings (P/E)**: {pe_str}")
        content_lines.append(f"- **Estimasi Imbal Hasil Dividen (Dividend Yield)**: {yield_pct}%")
        content_lines.append(f"- **Status Penilaian Valuasi**: `{trader_insight.get('valuation_status', 'FAIR_VALUE')}`")
        content_lines.append(f"- **Total Kapitalisasi Pasar**: Rp {mcap_trillion:,.2f} Triliun\n")

        content_lines.append("### 💼 Analisis Bandarmologi & Arus Modal Investor Asing")
        if foreign_billion > 0:
            content_lines.append(f"Dari sisi arus modal investor asing (*foreign flow*), tercatat akumulasi bersih (*net foreign inflow*) positif sebesar **Rp {foreign_billion:,.2f} Miliar** dalam beberapa sesi perdagangan terakhir. Arus modal masuk ini memberikan bantalan likuiditas yang solid bagi pergerakan harga.")
        elif foreign_billion < 0:
            content_lines.append(f"Investor asing mencatatkan aksi jual bersih (*net foreign outflow*) sekitar **Rp {abs(foreign_billion):,.2f} Miliar**, menandakan adanya penyesuaian portofolio jangka pendek oleh institusi global.")
        else:
            content_lines.append("Arus dana investor asing terpantau berimbang tanpa tekanan akumulasi atau distribusi ekstrem.")

        acc_brokers = trader_insight.get("top_accumulating_brokers", [])
        if acc_brokers:
            content_lines.append(f"Aktivitas perantara pedagang efek memperlihatkan broker dominan di sisi beli: **{', '.join(acc_brokers)}**, dengan status pergerakan *smart money*: `{bandar}`.\n")

        content_lines.append("### 🎯 Skenario Perdagangan & Level Kunci")
        content_lines.append("Bagi pelaku pasar dan pemodal dengan strategi *swing trading*, analis memetakan level teknikal berikut:")
        if levels.get("support_1"):
            content_lines.append(f"- **Area Penopang (Support 1 & 2)**: Rp {levels['support_1']:,} / Rp {levels['support_2']:,}")
            content_lines.append(f"- **Titik Uji Tekanan (Resistance 1)**: Rp {levels['resistance_1']:,}")
            content_lines.append(f"- **Target Kenaikan Konservatif**: Rp {levels['target_price']:,}\n")

        content_lines.append("### Kesimpulan Redaksi")
        content_lines.append(f"Dengan mempertimbangkan fundamental yang kokoh dan konfirmasi transaksi bursa terkini, saham {symbol} memiliki daya tarik tersendiri bagi portofolio investasi. Pelaku pasar disarankan tetap memantau rilis kinerja laporan keuangan kuartalan berikutnya.\n")
        content_lines.append("---")
        content_lines.append("*Disclaimer: Informasi ini disusun secara otomatis oleh be.n.ix menggunakan data terverifikasi Sectors Financial API. Berita ini bertujuan sebagai edukasi dan analisis pasar, bukan ajakan untuk membeli atau menjual efek tertentu. Keputusan investasi sepenuhnya berada di tangan investor.*")

        full_content = "\n".join(content_lines)
        summary = f"Analisis mendalam saham {symbol} ({company_name}): Kapitalisasi Rp {mcap_trillion:,.2f}T, evaluasi rasio P/E {pe_str}, dinamika foreign flow, dan peta level support/resistance."

        return {
            "title": headline,
            "slug": slug,
            "summary": summary,
            "content": full_content,
            "category": "emiten-focus",
            "tickers": [symbol],
            "author": "be.n.ix",
            "sentiment": bias,
            "sectors_data": stock_data
        }

    @classmethod
    def write_market_pulse_article(
        cls,
        pulse_data: Dict[str, Any],
        market_insight: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Crafts a daily market wrap / morning pulse article."""
        from agents.trader_agent import trader_agent
        now = datetime.now().strftime("%d %B %Y")
        sentiment = market_insight.get("market_sentiment", "NEUTRAL")
        gainers = trader_agent._extract_list(pulse_data.get("top_gainers"), "top_gainers")
        traded = trader_agent._extract_list(pulse_data.get("most_traded"))

        if sentiment == "BULLISH_DOMINANT":
            headline = f"IHSG Bergairah: Sektor Unggulan Memimpin Kenaikan, Cek Saham Top Gainers Hari Ini"
        elif sentiment == "BEARISH_CORRECTION":
            headline = f"Bursa Saham Konsolidasi: Investor Asing Selektif, Saham Berkapitalisasi Besar Jadi Penopang"
        else:
            headline = f"Rangkuman Pasar Saham: Indeks Bergerak Stabil, Transaksi Terfokus di Emiten Likuid"

        slug = cls._create_slug("market-pulse-ihsg")

        content_lines = []
        content_lines.append(f"# {headline}\n")
        content_lines.append(f"**JAKARTA, {now} — GARDA MARKET BEAT** — Dinamika Indeks Harga Saham Gabungan (IHSG) hari ini memperlihatkan pergerakan pasar yang dinamis. Berdasarkan data agregasi terkini dari Sectors Financial API, aktivitas transaksi bursa mencatatkan rotasi sektoral yang menarik dicermati oleh para pelaku pasar.\n")

        content_lines.append("### 🚀 Jajaran Saham Top Gainers Hari Ini")
        content_lines.append("Berikut adalah deretan saham yang mencatatkan lonjakan harga paling signifikan dalam rentang perdagangan harian:")
        if isinstance(gainers, list) and gainers:
            for idx, g in enumerate(gainers[:5], 1):
                sym = g.get("symbol", "-")
                chg = g.get("price_change", 0)
                chg_str = f"+{chg*100:.2f}%" if isinstance(chg, (int, float)) else str(chg)
                price = g.get("last_close_price", "-")
                content_lines.append(f"{idx}. **{sym}** — Menguat **{chg_str}** ke level Rp {price:,}" if isinstance(price, (int, float)) else f"{idx}. **{sym}** ({chg_str})")
        else:
            content_lines.append("- *Data sedang dalam proses sinkronisasi bursa.*")

        content_lines.append("\n### 💼 Saham Paling Ramai Ditransaksikan (Volume Terbesar)")
        content_lines.append("Likuiditas bursa terkonsentrasi pada emiten-emiten dengan perputaran saham tertinggi:")
        if isinstance(traded, list) and traded:
            for idx, t in enumerate(traded[:5], 1):
                sym = t.get("symbol", "-")
                vol = t.get("volume", 0)
                vol_str = f"{vol:,} lembar" if isinstance(vol, (int, float)) else str(vol)
                content_lines.append(f"{idx}. **{sym}** — Total volume: **{vol_str}**")
        else:
            content_lines.append("- *Data volume harian sedang diperbarui.*")

        content_lines.append("\n### 🧭 Catatan Redaksi untuk Investor")
        content_lines.append("Para pengamat pasar menyarankan investor untuk tetap berpegang pada disiplin manajemen risiko dan fokus pada saham-saham dengan fundamental laba bersih bertumbuh serta likuiditas harian yang memadai.\n")
        content_lines.append("---")
        content_lines.append("*Disclaimer: Diterbitkan oleh be.n.ix berdasarkan analitik data Sectors Financial API. Bukan merupakan rekomendasi finansial terikat.*")

        full_content = "\n".join(content_lines)
        summary = f"Rangkuman komprehensif pasar saham hari ini: Deretan saham top gainers, emiten paling aktif diperdagangkan, dan arah likuiditas bursa."

        # Extract tickers
        tickers = [g.get("symbol") for g in gainers[:5] if g.get("symbol")]

        return {
            "title": headline,
            "slug": slug,
            "summary": summary,
            "content": full_content,
            "category": "market-pulse",
            "tickers": tickers,
            "author": "be.n.ix",
            "sentiment": "BULLISH" if "BULLISH" in sentiment else "BEARISH" if "BEARISH" in sentiment else "NEUTRAL",
            "sectors_data": pulse_data
        }

journalist_agent = FinancialJournalistAgent()
