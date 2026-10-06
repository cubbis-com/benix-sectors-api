"""
Local Market Database & Cache Layer (Zero-Setup Middleware Persistence).
Checks SQLite (gateway.db) and auto-generated local JSON/TXT snapshots FIRST
before ever hitting the upstream Sectors API, guaranteeing zero quota waste.
"""
import os
import json
import time
import logging
from pathlib import Path
from typing import Optional, Dict, Any

from core.aiosqlite_compat import aiosqlite
from config import settings
from core.cache import cache_manager, make_cache_key

logger = logging.getLogger("sectors.local_db")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
LOCAL_JSON_PATH = DATA_DIR / "local_market_store.json"

# Seed data for UMKM, Hospitality (Perhotelan/Pariwisata), and Bluechip IDX
DEFAULT_SEED_MARKET = {
    "market_overview": {
        "index_name": "IHSG (Indeks Harga Saham Gabungan)",
        "last_price": 7421.10,
        "daily_change_pct": "+0.48%",
        "status": "BULLISH",
        "top_sectors": [
            {"sector": "Financials", "change": "+1.12%", "status": "Strong Accumulation"},
            {"sector": "Consumer Cyclicals & Tourism", "change": "+0.85%", "status": "Rebounding"},
            {"sector": "Infrastructure & Telco", "change": "-0.24%", "status": "Consolidation"}
        ],
        "regional_indices": [
            {"market": "Indonesia (IDX / IHSG)", "symbol": "IHSG", "value": 7421.10, "change": "+0.48%", "status": "BULLISH"},
            {"market": "Singapore (SGX / STI)", "symbol": "STI", "value": 3588.20, "change": "+0.32%", "status": "STEADY"},
            {"market": "Malaysia (Bursa / KLCI)", "symbol": "KLCI", "value": 1632.10, "change": "+0.25%", "status": "POSITIVE"},
            {"market": "Japan (TSE / Nikkei 225)", "symbol": "NIKKEI", "value": 39120.00, "change": "+0.65%", "status": "BULLISH"}
        ],
        "umkm_signal": "Sentimen belanja konsumen domestik dan pariwisata stabil meningkat, likuiditas perbankan untuk UMKM terjaga baik."
    },
    "stocks": {
        "BBCA": {
            "symbol": "BBCA",
            "company_name": "PT Bank Central Asia Tbk",
            "sector": "Financials (Perbankan)",
            "last_price": 10125,
            "change_pct": "+1.76%",
            "market_cap_trillion": 1248.5,
            "pe_ratio": 21.5,
            "dividend_yield": "2.8%",
            "net_foreign_flow_1d": "+245 Miliar IDR",
            "smart_money_status": "Akumulasi Asing & Institusi",
            "umkm_insight": "BCA mencatatkan pertumbuhan penyaluran kredit konsumsi dan merchant EDC UMKM yang solid. Likuiditas perbankan sangat sehat."
        },
        "BBRI": {
            "symbol": "BBRI",
            "company_name": "PT Bank Rakyat Indonesia (Persero) Tbk",
            "sector": "Financials (Perbankan & Mikro)",
            "last_price": 4980,
            "change_pct": "+1.22%",
            "market_cap_trillion": 754.2,
            "pe_ratio": 12.8,
            "dividend_yield": "6.4%",
            "net_foreign_flow_1d": "+180 Miliar IDR",
            "smart_money_status": "Akumulasi Bertahap Broker Domestik & Asing",
            "umkm_insight": "Kinerja BBRI adalah barometer utama denyut ekonomi UMKM di Indonesia melalui jaringan ultra-mikro (Holding UMi bersama Pegadaian & PNM)."
        },
        "BMRI": {
            "symbol": "BMRI",
            "company_name": "PT Bank Mandiri (Persero) Tbk",
            "sector": "Financials (Perbankan Korporasi & Komersial)",
            "last_price": 6850,
            "change_pct": "+0.74%",
            "market_cap_trillion": 639.3,
            "pe_ratio": 11.4,
            "dividend_yield": "5.2%",
            "net_foreign_flow_1d": "+92 Miliar IDR",
            "smart_money_status": "Fair Valuation & Akumulasi Institusi",
            "umkm_insight": "Digitalisasi Livin' Merchant mendorong transaksi pelaku usaha menengah ke atas dan ekosistem rantai pasok korporasi."
        },
        "TLKM": {
            "symbol": "TLKM",
            "company_name": "PT Telkom Indonesia (Persero) Tbk",
            "sector": "Telecommunication & Digital Infrastructure",
            "last_price": 3010,
            "change_pct": "-0.66%",
            "market_cap_trillion": 298.1,
            "pe_ratio": 12.3,
            "dividend_yield": "5.6%",
            "debt_to_equity": "0.85 (Sangat Sehat)",
            "operating_cash_flow": "Rp 54.2 Triliun (Positif Kuat)",
            "net_foreign_flow_1d": "-35 Miliar IDR",
            "smart_money_status": "Konsolidasi di Area Support",
            "vendor_due_diligence": "Risiko gagal bayar sangat rendah. Rasio utang (DER 0.85) terkendali dengan arus kas operasional jumbo, menjadikannya mitra kontrak kerja sama jangka panjang yang sangat terpercaya bagi UMKM vendor infrastruktur & digital.",
            "umkm_insight": "Penetrasi internet IndiHome dan infrastruktur cloud Telkomsel adalah tulang punggung operasional dan adopsi e-commerce toko UMKM di daerah."
        },
        "ICBP": {
            "symbol": "ICBP",
            "company_name": "PT Indofood CBP Sukses Makmur Tbk",
            "sector": "Consumer Non-Cyclicals (Makanan & Minuman Olahan)",
            "last_price": 11200,
            "change_pct": "+1.13%",
            "market_cap_trillion": 130.6,
            "pe_ratio": 14.2,
            "dividend_yield": "3.8%",
            "net_profit_margin": "12.8%",
            "debt_to_equity": "0.78 (Rendah & Sehat)",
            "operating_cash_flow": "Rp 14.8 Triliun (Sangat Kuat)",
            "vendor_due_diligence": "Mitra tier-1 dengan arus kas operasional tinggi dan rasio utang sehat (DER 0.78). UMKM logistik dan supplier bahan pangan kemasan aman menjalin kontrak suplai jangka panjang.",
            "umkm_insight": "Pertumbuhan volume penjualan mie instan dan dairy mengindikasikan ketahanan daya beli masyarakat lapisan menengah-bawah untuk kebutuhan pokok tetap prima."
        },
        "MYOR": {
            "symbol": "MYOR",
            "company_name": "PT Mayora Indah Tbk",
            "sector": "Consumer Non-Cyclicals (Biskuit, Kopi, & Olahan Makanan)",
            "last_price": 2450,
            "change_pct": "+2.08%",
            "market_cap_trillion": 54.8,
            "pe_ratio": 16.5,
            "dividend_yield": "2.9%",
            "net_profit_margin": "10.4%",
            "umkm_insight": "Kenaikan penjualan biskuit dan kopi kemasan menjadi barometer bahwa belanja harian konsumen ritel dan warung kelontong terus bergerak dinamis."
        },
        "UNVR": {
            "symbol": "UNVR",
            "company_name": "PT Unilever Indonesia Tbk",
            "sector": "Consumer Non-Cyclicals (Barang Konsumsi Rumah Tangga & Personal Care)",
            "last_price": 2340,
            "change_pct": "+0.43%",
            "market_cap_trillion": 89.3,
            "pe_ratio": 18.2,
            "dividend_yield": "5.1%",
            "net_profit_margin": "13.6%",
            "umkm_insight": "Margin laba bersih rata-rata industri FMCG di kisaran 11-14% menjadi standar acuan (benchmarking) bagi pengusaha ritel dan brand lokal UMKM."
        },
        "CPIN": {
            "symbol": "CPIN",
            "company_name": "PT Charoen Pokphand Indonesia Tbk",
            "sector": "Consumer Non-Cyclicals (Pakan Ternak & Perunggasan)",
            "last_price": 5050,
            "change_pct": "+1.51%",
            "market_cap_trillion": 82.8,
            "pe_ratio": 22.1,
            "dividend_yield": "2.2%",
            "gross_profit_margin": "14.2%",
            "umkm_insight": "Pergerakan beban pokok penjualan (COGS) CPIN mencerminkan stabilitas harga impor jagung dan bungkil kedelai global. Mengindikasikan biaya pakan bagi peternak ayam UMKM relatif terkendali."
        },
        "JPFA": {
            "symbol": "JPFA",
            "company_name": "PT Japfa Comfeed Indonesia Tbk",
            "sector": "Consumer Non-Cyclicals (Pakan Ternak & Agribisnis)",
            "last_price": 1420,
            "change_pct": "+2.16%",
            "market_cap_trillion": 16.6,
            "pe_ratio": 10.8,
            "dividend_yield": "4.5%",
            "gross_profit_margin": "15.1%",
            "umkm_insight": "Kenaikan margin kotor perunggasan JPFA mengonfirmasi pemulihan harga karkas ayam di tingkat peternak rakyat dan kestabilan rantai pasok agribisnis."
        },
        "SMGR": {
            "symbol": "SMGR",
            "company_name": "PT Semen Indonesia (Persero) Tbk",
            "sector": "Basic Materials (Semen & Bahan Bangunan)",
            "last_price": 3890,
            "change_pct": "+1.83%",
            "market_cap_trillion": 26.2,
            "pe_ratio": 13.5,
            "dividend_yield": "5.8%",
            "umkm_insight": "Kenaikan volume pengiriman semen kantong nasional mengindikasikan geliat renovasi rumah dan proyek toko material UMKM di kota-kota tier-2 dan tier-3."
        },
        "CTRA": {
            "symbol": "CTRA",
            "company_name": "PT Ciputra Development Tbk",
            "sector": "Real Estate & Properti Residensial",
            "last_price": 1180,
            "change_pct": "+1.72%",
            "market_cap_trillion": 21.9,
            "pe_ratio": 10.2,
            "dividend_yield": "3.2%",
            "marketing_sales_growth": "+12.4%",
            "umkm_insight": "Penjualan rumah residensial subsidi dan segmen menengah (< Rp 1 Miliar) tumbuh 12% didorong insentif PPN DTP, menjadi angin segar bagi toko bahan bangunan dan kontraktor interior lokal."
        },
        "BSDE": {
            "symbol": "BSDE",
            "company_name": "PT Bumi Serpong Damai Tbk",
            "sector": "Real Estate & Kawasan Mandiri",
            "last_price": 1060,
            "change_pct": "+0.95%",
            "market_cap_trillion": 22.4,
            "pe_ratio": 8.7,
            "dividend_yield": "2.4%",
            "umkm_insight": "Ekspansi ruko komersial dan klaster perumahan baru membuka peluang pasar baru bagi penyedia jasa renovasi, material, dan kedai kuliner lokal."
        },
        "ASII": {
            "symbol": "ASII",
            "company_name": "PT Astra International Tbk",
            "sector": "Industrials & Konglomerasi Otomotif",
            "last_price": 4890,
            "change_pct": "+0.62%",
            "market_cap_trillion": 197.9,
            "pe_ratio": 6.8,
            "dividend_yield": "8.2%",
            "roe": "14.8%",
            "smart_money_status": "Undervalued Cash Cow Play",
            "umkm_insight": "Saham defensif dengan yield dividen tinggi (8.2%) dan rasio utang sangat konservatif, cocok untuk alokasi dana cadangan kas jangka panjang pengusaha UMKM."
        },
        "SHID": {
            "symbol": "SHID",
            "company_name": "PT Hotel Sahid Jaya International Tbk",
            "sector": "Consumer Cyclicals (Perhotelan & Pariwisata)",
            "last_price": 1240,
            "change_pct": "+2.48%",
            "market_cap_trillion": 1.4,
            "pe_ratio": 28.6,
            "dividend_yield": "1.2%",
            "net_foreign_flow_1d": "+1.8 Miliar IDR",
            "smart_money_status": "Akumulasi Ritel & Rebound Pariwisata",
            "umkm_insight": "Sinyal pemulihan tingkat keterisian kamar (okupansi) hotel pasca musim liburan dan kenaikan kegiatan MICE korporasi."
        },
        "PANR": {
            "symbol": "PANR",
            "company_name": "PT Panorama Sentrawisata Tbk",
            "sector": "Consumer Cyclicals (Biro Perjalanan & Wisata)",
            "last_price": 420,
            "change_pct": "+1.94%",
            "market_cap_trillion": 0.5,
            "pe_ratio": 15.2,
            "dividend_yield": "1.5%",
            "net_foreign_flow_1d": "+850 Juta IDR",
            "smart_money_status": "Momentum Positif Travel",
            "umkm_insight": "Lonjakan pesanan paket wisata inbound dan outbound memberikan sentimen positif pada bisnis F&B serta cinderamata lokal penunjang pariwisata."
        },
        "EAST": {
            "symbol": "EAST",
            "company_name": "PT Eastparc Hotel Tbk",
            "sector": "Consumer Cyclicals (Hotel & Hospitality Yogyakarta)",
            "last_price": 138,
            "change_pct": "+0.73%",
            "market_cap_trillion": 0.57,
            "pe_ratio": 14.1,
            "dividend_yield": "7.8%",
            "net_foreign_flow_1d": "+320 Juta IDR",
            "smart_money_status": "High Dividend Yield Hotel Play",
            "umkm_insight": "Hotel butik ramah keluarga di destinasi wisata utama dengan yield dividen tinggi, menjadi acuan daya beli turis domestik segmen menengah."
        },
        "D05": {
            "symbol": "D05",
            "company_name": "DBS Group Holdings Ltd",
            "sector": "Financials (Perbankan Singapura & Regional ASEAN)",
            "last_price": 37.80,
            "currency": "SGD",
            "change_pct": "+0.53%",
            "market_cap_sgd_billion": 97.4,
            "pe_ratio": 10.8,
            "dividend_yield": "5.4%",
            "net_foreign_flow_1d": "+38 Juta SGD",
            "smart_money_status": "Akumulasi Institusi Global",
            "umkm_insight": "Bank terbesar di Asia Tenggara, jangkar likuiditas regional, dan mitra kunci transaksi ekspor-impor pengusaha Indonesia ke pasar global."
        },
        "O39": {
            "symbol": "O39",
            "company_name": "Oversea-Chinese Banking Corp (OCBC)",
            "sector": "Financials (Perbankan Regional)",
            "last_price": 14.50,
            "currency": "SGD",
            "change_pct": "+0.42%",
            "market_cap_sgd_billion": 65.2,
            "pe_ratio": 9.8,
            "dividend_yield": "5.8%",
            "smart_money_status": "Valuasi Murah & Dividen Tinggi",
            "umkm_insight": "Melalui OCBC Indonesia, bank ini aktif membiayai fasilitas modal kerja dan pembiayaan hijau (ESG) untuk bisnis menengah."
        },
        "U11": {
            "symbol": "U11",
            "company_name": "United Overseas Bank Ltd (UOB)",
            "sector": "Financials (Perbankan Komersial & UMKM)",
            "last_price": 31.20,
            "currency": "SGD",
            "change_pct": "+0.65%",
            "market_cap_sgd_billion": 52.1,
            "pe_ratio": 9.5,
            "dividend_yield": "5.6%",
            "smart_money_status": "Akumulasi Dana Pensiun Regional",
            "umkm_insight": "UOB memiliki fokus kuat pada pembiayaan perdagangan lintas batas ASEAN dan rantai pasok korporasi Indonesia."
        },
        "Z74": {
            "symbol": "Z74",
            "company_name": "Singapore Telecommunications Ltd (Singtel)",
            "sector": "Telecommunications & Digital Infrastructure",
            "last_price": 2.95,
            "currency": "SGD",
            "change_pct": "+0.34%",
            "market_cap_sgd_billion": 48.7,
            "pe_ratio": 14.2,
            "dividend_yield": "5.1%",
            "smart_money_status": "Portfolio Optimization & Data Center Play",
            "umkm_insight": "Pemegang 30.1% saham Telkomsel Indonesia, ekspansi data center regional Singtel memperkuat konektivitas digital cloud di Asia Tenggara."
        },
        "C6L": {
            "symbol": "C6L",
            "company_name": "Singapore Airlines Ltd (SIA)",
            "sector": "Industrials & Aviation (Penerbangan & Kargo)",
            "last_price": 6.45,
            "currency": "SGD",
            "change_pct": "+0.78%",
            "market_cap_sgd_billion": 19.3,
            "pe_ratio": 8.4,
            "dividend_yield": "6.2%",
            "smart_money_status": "Rebound Pariwisata & Yield Tinggi",
            "umkm_insight": "Barometer utama arus wisatawan mancanegara ke Bali dan kota-kota wisata Indonesia serta kapasitas logistik kargo udara Asia Tenggara."
        },
        "G13": {
            "symbol": "G13",
            "company_name": "Genting Singapore Ltd",
            "sector": "Consumer Cyclicals (Resorts World Sentosa & Hospitality)",
            "last_price": 0.88,
            "currency": "SGD",
            "change_pct": "+1.15%",
            "market_cap_sgd_billion": 10.6,
            "pe_ratio": 12.1,
            "dividend_yield": "4.5%",
            "smart_money_status": "Waterfront RWS 2.0 Catalyst",
            "umkm_insight": "Pengelola destinasi wisata ikonik terintegrasi di Singapura. Menjadi indikator sentimen belanja rekreasi dan hiburan konsumen kelas atas Asia."
        },
        "A17U": {
            "symbol": "A17U",
            "company_name": "CapitaLand Integrated Commercial Trust (CICT)",
            "sector": "Real Estate / Commercial REIT",
            "last_price": 2.08,
            "currency": "SGD",
            "change_pct": "+0.48%",
            "market_cap_sgd_billion": 14.1,
            "pe_ratio": 15.6,
            "dividend_yield": "5.3%",
            "smart_money_status": "Defensive Prime Retail & Office Yield",
            "umkm_insight": "Pengelola mall ritel utama di Singapura. Tingkat okupansi 97% membuktikan ketahanan konsumsi ritel fisik di kawasan perkotaan modern."
        }
    },
    "umkm_topics": {
        "vendor_due_diligence": {
            "title": "Vendor & Partner Due Diligence (Pengecekan Kesehatan Bisnis Mitra)",
            "summary": "Analisis solvabilitas mitra bisnis besar (misal TLKM, ICBP) menggunakan rasio utang (DER) dan Arus Kas Operasional (OCF) untuk mencegah risiko gagal bayar pada kontrak jangka panjang bernilai ratusan juta hingga miliaran rupiah.",
            "metrics": {
                "TLKM": {"der": 0.85, "ocf": "Rp 54.2 T", "status": "Sangat Sehat / Risiko Sangat Rendah"},
                "ICBP": {"der": 0.78, "ocf": "Rp 14.8 T", "status": "Solven / Arus Kas Jumbo"}
            },
            "panduan_umkm": "Pastikan rasio DER mitra < 1.5 dan OCF positif berturut-turut dalam 3 tahun terakhir sebelum menandatangani termin pembayaran kredit di atas 60 hari."
        },
        "retail_fnb_trend": {
            "title": "Tren Industri Ritel & Kuliner F&B (Industry Benchmarking)",
            "summary": "Mengukur tren daya beli konsumen Indonesia melalui agregat sektor Consumer Non-Cyclicals (ICBP, MYOR, UNVR) dengan rata-rata laba bersih dan margin industri.",
            "benchmarks": {
                "rata_rata_net_profit_margin": "11.5% - 13.5%",
                "pertumbuhan_pendapatan_industri": "+7.8% YoY",
                "emiten_barometer": ["ICBP", "MYOR", "UNVR"]
            },
            "panduan_umkm": "Gunakan Net Profit Margin 11-13% sebagai standar efisiensi operasional bagi restoran atau brand makanan kemasan UMKM Anda."
        },
        "supply_chain_feed": {
            "title": "Pemantauan Rantai Pasok Pakan Ternak & Biaya Bahan Baku",
            "summary": "Memantau pergerakan harga komoditas impor (jagung & kedelai) dan stabilitas margin kotor emiten pakan CPIN dan JPFA untuk deteksi dini lonjakan modal peternak ayam & UMKM agribisnis.",
            "benchmarks": {
                "margin_kotor_cpin": "14.2%",
                "margin_kotor_jpfa": "15.1%",
                "status_rantai_pasok": "Stabil, tidak terindikasi kelangkaan pakan"
            },
            "panduan_umkm": "Jika margin kotor emiten pakan tertekan di bawah 12%, segera lakukan lindung nilai atau pengadaan bahan baku pakan 2 bulan lebih awal."
        },
        "dividend_screening": {
            "title": "Penyaringan Saham Tabungan / Cadangan Kas Bisnis UMKM",
            "summary": "Screener saham dividen tunai aman dengan kriteria ketat: Dividend Yield > 5%, P/E < 15, ROE > 10%, dan rasio utang rendah untuk alokasi dana darurat atau laba ditahan UMKM.",
            "screened_stocks": [
                {"symbol": "ASII", "yield": "8.2%", "pe": 6.8, "roe": "14.8%", "alasan": "Konglomerasi kas kuat, valuasi diskon"},
                {"symbol": "BBRI", "yield": "6.4%", "pe": 12.8, "roe": "18.2%", "alasan": "Dividen rutin, fundamental ultra-mikro kokoh"},
                {"symbol": "SMGR", "yield": "5.8%", "pe": 13.5, "roe": "11.2%", "alasan": "Pemimpin pasar semen nasional"},
                {"symbol": "TLKM", "yield": "5.6%", "pe": 12.3, "roe": "16.5%", "alasan": "Monopoli infrastruktur digital nasional"}
            ]
        },
        "property_construction": {
            "title": "Kondisi Industri Properti & Konstruksi Indonesia",
            "summary": "Analisis permintaan bahan bangunan, semen kantong, dan hunian subsidi bagi pengusaha toko bangunan, kontraktor, dan interior.",
            "indicators": {
                "pertumbuhan_marketing_sales_ctra": "+12.4% YoY",
                "tren_semen_kantong_smgr": "Tumbuh stabil di kota berkembang",
                "katalis": "Insentif PPN DTP pemerintah dan permintaan rumah pertama keluarga muda"
            },
            "panduan_umkm": "Industri perumahan sedang mengalami momentum ekspansi yang sehat. Permintaan semen, cat, keramik, dan baja ringan berpeluang naik stabil 8-10% semester ini."
        }
    }
}

class LocalMarketDB:
    def __init__(self, db_path: str = settings.DATABASE_PATH, json_path: Path = LOCAL_JSON_PATH):
        self.db_path = db_path
        self.json_path = json_path
        self._ensure_storage()

    def _ensure_storage(self):
        """Build local directory and JSON store automatically without user installation."""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if not self.json_path.exists():
            with open(self.json_path, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_SEED_MARKET, f, indent=2, ensure_ascii=False)
            logger.info("Initialized local JSON market database at %s", self.json_path)

    async def init_sqlite(self):
        """Create local market entities table in SQLite if not exists."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS local_market_entities (
                    entity_key TEXT PRIMARY KEY,
                    category TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    updated_at REAL NOT NULL
                )
            """)
            await db.commit()

            # Seed SQLite if empty (use INSERT OR IGNORE so live Sectors API data is never wiped)
            now = time.time()
            for sym, data in DEFAULT_SEED_MARKET["stocks"].items():
                await db.execute(
                    "INSERT OR IGNORE INTO local_market_entities VALUES (?, ?, ?, ?)",
                    (f"stock:{sym}", "stock", json.dumps(data), now)
                )
            await db.execute(
                "INSERT OR IGNORE INTO local_market_entities VALUES (?, ?, ?, ?)",
                ("market:overview", "overview", json.dumps(DEFAULT_SEED_MARKET["market_overview"]), now)
            )
            for top_key, top_data in DEFAULT_SEED_MARKET.get("umkm_topics", {}).items():
                await db.execute(
                    "INSERT OR IGNORE INTO local_market_entities VALUES (?, ?, ?, ?)",
                    (f"topic:{top_key}", "topic", json.dumps(top_data), now)
                )
            await db.commit()
            logger.info("Synchronized local SQLite market entities with UMKM intelligence")

    async def get_umkm_topic_locally(self, topic_key: str) -> Optional[Dict[str, Any]]:
        """Retrieve UMKM business scenario insight locally (0 credits)."""
        clean_key = topic_key.strip().lower()
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute(
                    "SELECT payload_json FROM local_market_entities WHERE entity_key = ?",
                    (f"topic:{clean_key}",)
                ) as cur:
                    row = await cur.fetchone()
                    if row:
                        return {"source": "local_sqlite_db", "data": json.loads(row[0]), "credits": 0}
        except Exception:
            pass

        # Fallback to local JSON
        if self.json_path.exists():
            try:
                with open(self.json_path, "r", encoding="utf-8") as f:
                    store = json.load(f)
                    topics = store.get("umkm_topics", {})
                    if clean_key in topics:
                        return {"source": "local_json_file", "data": topics[clean_key], "credits": 0}
            except Exception:
                pass

        return None

    async def get_stock_locally(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        1. Check SQLite api_cache (from previous Sectors calls for company report & flow)
        2. Check SQLite local_market_entities
        3. Check local JSON file
        Returns immediately with 0 credit cost.
        """
        sym = symbol.strip().upper()

        # Step 1: Check SQLite api_cache for any cached report of this symbol
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute(
                    "SELECT response_json FROM api_cache WHERE (cache_key LIKE ? OR endpoint LIKE ?) AND expires_at > ? ORDER BY updated_at DESC LIMIT 1",
                    (f"%company/report/{sym}%", f"%company/report/{sym}%", time.time())
                ) as cur:
                    row = await cur.fetchone()
                    if row:
                        cached_rep = json.loads(row[0])
                        # Check foreign flow in cache as well
                        flow_data = None
                        async with db.execute(
                            "SELECT response_json FROM api_cache WHERE (cache_key LIKE ? OR endpoint LIKE ?) AND expires_at > ? ORDER BY updated_at DESC LIMIT 1",
                            (f"%foreign-flow/{sym}%", f"%foreign-flow/{sym}%", time.time())
                        ) as f_cur:
                            f_row = await f_cur.fetchone()
                            if f_row:
                                flow_data = json.loads(f_row[0])

                        logger.info("⚡ [LOCAL SQLITE HIT] Retrieved %s from api_cache", sym)
                        return {
                            "source": "local_sqlite_cache",
                            "data": {
                                "symbol": sym,
                                "company_report": cached_rep,
                                "foreign_flow": flow_data
                            },
                            "credits": 0
                        }
        except Exception as e:
            logger.debug("api_cache lookup error: %s", e)

        # Step 2: Check SQLite local_market_entities
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute(
                    "SELECT payload_json FROM local_market_entities WHERE entity_key = ?",
                    (f"stock:{sym}",)
                ) as cur:
                    row = await cur.fetchone()
                    if row:
                        logger.info("⚡ [LOCAL SQLITE HIT] Retrieved %s from local_market_entities", sym)
                        return {"source": "local_sqlite_db", "data": json.loads(row[0]), "credits": 0}
        except Exception as e:
            logger.warning("Error reading local_market_entities: %s", e)

        # Step 3: Check local JSON snapshot
        if self.json_path.exists():
            try:
                with open(self.json_path, "r", encoding="utf-8") as f:
                    store = json.load(f)
                    stocks = store.get("stocks", {})
                    if sym in stocks:
                        logger.info("⚡ [LOCAL JSON HIT] Retrieved %s from local_market_store.json", sym)
                        return {"source": "local_json_file", "data": stocks[sym], "credits": 0}
            except Exception as e:
                logger.warning("Error reading local JSON store: %s", e)

        return None

    async def get_market_overview_locally(self) -> Optional[Dict[str, Any]]:
        """Retrieve market overview from local SQLite or JSON store."""
        # Check SQLite
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute(
                    "SELECT payload_json FROM local_market_entities WHERE entity_key = 'market:overview'"
                ) as cur:
                    row = await cur.fetchone()
                    if row:
                        return {"source": "local_sqlite_db", "data": json.loads(row[0]), "credits": 0}
        except Exception:
            pass

        # Check JSON
        if self.json_path.exists():
            try:
                with open(self.json_path, "r", encoding="utf-8") as f:
                    store = json.load(f)
                    if "market_overview" in store:
                        return {"source": "local_json_file", "data": store["market_overview"], "credits": 0}
            except Exception:
                pass

        return None

    async def save_stock_locally(self, symbol: str, data: Dict[str, Any]):
        """Persist newly retrieved stock data to local SQLite and JSON to prevent future API calls."""
        sym = symbol.strip().upper()
        now = time.time()
        # 1. Save SQLite
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "INSERT OR REPLACE INTO local_market_entities VALUES (?, ?, ?, ?)",
                    (f"stock:{sym}", "stock", json.dumps(data), now)
                )
                await db.commit()
        except Exception as e:
            logger.warning("Failed to save to local_market_entities: %s", e)

        # 2. Save JSON file
        try:
            store = {}
            if self.json_path.exists():
                with open(self.json_path, "r", encoding="utf-8") as f:
                    store = json.load(f)
            if "stocks" not in store:
                store["stocks"] = {}
            store["stocks"][sym] = data
            with open(self.json_path, "w", encoding="utf-8") as f:
                json.dump(store, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning("Failed to save to local_market_store.json: %s", e)

    async def get_all_stocks_locally(self) -> Dict[str, Any]:
        """Retrieve all companies/stocks in local store with zero credit cost."""
        all_stocks = dict(DEFAULT_SEED_MARKET.get("stocks", {}))
        
        # Merge SQLite local entities
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute(
                    "SELECT entity_key, payload_json FROM local_market_entities WHERE category = 'stock'"
                ) as cur:
                    rows = await cur.fetchall()
                    for key, payload in rows:
                        sym = key.replace("stock:", "")
                        try:
                            all_stocks[sym] = json.loads(payload)
                        except Exception:
                            pass
        except Exception as e:
            logger.warning("Error loading all stocks from SQLite: %s", e)

        # Merge local JSON store
        if self.json_path.exists():
            try:
                with open(self.json_path, "r", encoding="utf-8") as f:
                    store = json.load(f)
                    for sym, item in store.get("stocks", {}).items():
                        all_stocks[sym] = item
            except Exception as e:
                logger.warning("Error loading all stocks from JSON store: %s", e)

        return all_stocks

local_market_db = LocalMarketDB()
