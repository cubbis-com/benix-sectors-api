"""
Automated Test for Agentic AI Skills & Portal News Publishing.
"""
import asyncio
import logging
from core.cache import cache_manager
from core.credits_tracker import credits_tracker
from core.portal_db import portal_db
from agents.orchestrator import garda_orchestrator
from agents.trader_agent import trader_agent
from agents.sectors_engine import sectors_engine
from agents.backend_dev_agent import backend_dev_agent
from agents.frontend_dev_agent import frontend_dev_agent

logging.basicConfig(level=logging.INFO)

async def test_agentic_skills():
    print("=" * 65)
    print("🚀 PENGUJIAN MODULAR AGENTIC AI SKILLS & PORTAL PUBLISHING")
    print("=" * 65)

    # 1. Initialize databases
    print("\n[1/5] Inisialisasi Database Cache, Credits, dan Portal...")
    await cache_manager.init_db()
    await credits_tracker.init_db()
    await portal_db.init_db()
    print("✅ Seluruh database siap.")

    # 2. Test Trader Analyst Skill
    print("\n[2/5] Menjalankan Trader Analyst AI Skill (BBCA)...")
    stock_data = await sectors_engine.fetch_stock_deepdive("BBCA")
    analysis = trader_agent.analyze_stock("BBCA", stock_data)
    print("✅ Analisis Trader Selesai:")
    print(f"   Bias Sentimen: {analysis['bias']}")
    print(f"   Status Valuasi: {analysis['valuation_status']} (P/E: {analysis['pe_ratio']})")
    print(f"   Status Bandarmologi: {analysis['bandarmology_status']}")
    print(f"   Status Foreign Flow: {analysis['foreign_flow_status']}")
    print(f"   Target Price: Rp {analysis['key_levels']['target_price']:,}")

    # 3. Test Garda Orchestrator (Data -> Trader -> Wartawan -> Portal DB)
    print("\n[3/5] Menjalankan Garda Orchestrator (Otomasi Penerbitan Berita BBCA)...")
    pub_result = await garda_orchestrator.publish_emiten_news("BBCA")
    print("✅ Berita Berhasil Dipublikasikan ke Portal:")
    print(f"   Judul: {pub_result['article']['title']}")
    print(f"   Slug: {pub_result['article']['slug']}")
    print(f"   Penulis: {pub_result['article']['author']}")
    print(f"   Kategori: {pub_result['article']['category']}")

    # 4. Test Reading from Portal DB
    print("\n[4/5] Menguji Pembacaan Berita dari Portal Database...")
    articles = await portal_db.list_articles(limit=5)
    print(f"✅ Total artikel terdaftar di portal: {len(articles)}")
    for a in articles:
        print(f"   - [{a['category']}] {a['title']} (Views: {a['views']})")

    # 5. Test Frontend & Backend Helper Skills
    print("\n[5/5] Menguji Backend & Frontend Dev Skills...")
    backend_query = backend_dev_agent.generate_screener_query(sub_sector="banks", max_pe=15)
    print(f"✅ Backend Dev Generated Query: {backend_query['query_parameters']}")
    ui_blueprint = frontend_dev_agent.get_portal_ui_blueprint()
    print(f"✅ Frontend Dev UI Components: {[c['name'] for c in ui_blueprint['components']]}")

    print("\n🎉 SELURUH SKILL AGENTIC AI & PORTAL NEWS PIPELINE BERFUNGSI SEMPURNA!")

if __name__ == "__main__":
    asyncio.run(test_agentic_skills())
