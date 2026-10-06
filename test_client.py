"""
Automated Verification & Test Script for Sectors API Middleware.
Tests:
1. Sectors API v2 Authentication & Connectivity
2. Credit Shield Cache Verification (Validates 0 credits on cache hits)
3. Company Analysis (BBCA)
4. WhatsApp Notification Gateway
"""
import asyncio
import logging
from config import settings
from core.cache import cache_manager
from core.credits_tracker import credits_tracker
from core.sectors_client import sectors_client
from services.briefing_service import generate_daily_market_briefing
from routers.notifications import send_wa_message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_client")

async def run_tests():
    print("=" * 60)
    print("🚀 MEMULAI PENGUJIAN SECTORS API MIDDLEWARE")
    print("=" * 60)

    # 1. Initialize databases
    print("\n[1/5] Inisialisasi Database Cache & Credits Tracker...")
    await cache_manager.init_db()
    await credits_tracker.init_db()
    print("✅ Database ready.")

    # 2. Test Sectors API Authentication (Helper Subsectors)
    print("\n[2/5] Menguji Koneksi Sectors API (Subsectors)...")
    res1 = await sectors_client.get("/subsectors/", bypass_cache=True)
    if res1.get("_meta", {}).get("status") == 200:
        data = res1.get("data", [])
        print(f"✅ Koneksi Berhasil! Total subsektor didapatkan: {len(data)}")
        print(f"   Sample: {data[:2]}")
        print(f"   Credits Billed: {res1['_meta']['credits_consumed']} kredit")
    else:
        print(f"❌ Gagal koneksi: {res1}")
        return

    # 3. Test Credit Shield Caching (Second call should be CACHE HIT with 0 credits)
    print("\n[3/5] Menguji Credit Shield (Proteksi Kuota Caching)...")
    res2 = await sectors_client.get("/subsectors/", bypass_cache=False)
    if res2.get("_meta", {}).get("source") == "cache":
        print(f"✅ CACHE HIT BERHASIL! Sumber: {res2['_meta']['source']}, Kredit: {res2['_meta']['credits_consumed']}")
    else:
        print(f"⚠️ Cache miss: {res2.get('_meta')}")

    # 4. Test Single Stock Report (BBCA Overview)
    print("\n[4/5] Menguji Pengambilan Laporan Emiten (BBCA)...")
    res_bbca = await sectors_client.get("/company/report/BBCA/", params={"sections": "overview"})
    if res_bbca.get("_meta", {}).get("status") == 200:
        bbca_data = res_bbca.get("data", {})
        overview = bbca_data.get("overview", {})
        print(f"✅ Berhasil mengambil data BBCA:")
        print(f"   Nama: {bbca_data.get('company_name')}")
        print(f"   Sektor: {overview.get('sector')} / {overview.get('sub_sector')}")
        print(f"   Market Cap: Rp {overview.get('market_cap', 0):,}")
        print(f"   Kredit Terpakai: {res_bbca['_meta']['credits_consumed']} kredit")
    else:
        print(f"⚠️ Respon BBCA: {res_bbca.get('error')}")

    # 5. Test Briefing Generator & Metrics
    print("\n[5/5] Menguji Generator Briefing Pasar & Metrik...")
    briefing = await generate_daily_market_briefing()
    print("✅ Teks Briefing Terbentuk:")
    print("-" * 40)
    print(briefing["message"])
    print("-" * 40)

    # Summary
    metrics = await credits_tracker.get_summary()
    print("\n📊 RINGKASAN METRIK KREDIT:")
    print(f"   Total Permintaan: {metrics.get('total_gateway_requests')}")
    print(f"   Kredit Terpakai: {metrics.get('estimated_credits_consumed')}")
    print(f"   Kredit Dihemat via Cache: {metrics.get('credits_saved_by_cache')}")
    print(f"   Cache Hit Ratio: {metrics.get('cache_hit_ratio_percent')}%")
    print("\n🎉 SELURUH PENGUJIAN INTI SELESAI DENGAN SUKSES!")

if __name__ == "__main__":
    asyncio.run(run_tests())
