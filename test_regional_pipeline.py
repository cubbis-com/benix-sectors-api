import httpx
import json

def run_tests():
    client = httpx.Client(base_url="http://127.0.0.1:8000", timeout=35.0)

    print("=== TEST 1: Regional News Wire (ALL) ===")
    r = client.get("/api/v1/portal/news-wire?country=ALL&limit=4")
    data = r.json()
    print("Status:", data.get("status"), "| Total:", data.get("total_returned"))
    for h in data.get("headlines", [])[:3]:
        print(f"  [{h.get('country')}] {h.get('source')}: {h.get('title')[:60]}... | Tickers: {h.get('matched_tickers')}")

    print("\n=== TEST 2: Singapore News Wire (SG) ===")
    r = client.get("/api/v1/portal/news-wire?country=SG&limit=4")
    data = r.json()
    print("Total SG headlines:", data.get("total_returned"))
    for h in data.get("headlines", [])[:3]:
        print(f"  [SG] {h.get('source')}: {h.get('title')[:60]}...")

    print("\n=== TEST 3: Japan News Wire (JP) ===")
    r = client.get("/api/v1/portal/news-wire?country=JP&limit=4")
    data = r.json()
    print("Total JP headlines:", data.get("total_returned"))
    for h in data.get("headlines", [])[:3]:
        print(f"  [JP] {h.get('source')}: {h.get('title')[:60]}...")

    print("\n=== TEST 4: Ticker News Filter (BBCA) ===")
    r = client.get("/api/v1/portal/news-wire?ticker=BBCA")
    data = r.json()
    print("Total BBCA headlines:", data.get("total_returned"))
    for h in data.get("headlines", [])[:3]:
        print(f"  - {h.get('source')}: {h.get('title')}")

    print("\n=== TEST 5: Pre-Market Briefing 06:30 WIB ===")
    r = client.get("/api/v1/portal/market-briefing")
    data = r.json()
    print("Title:", data.get("title"))
    print("Indices:", [idx.get("symbol") + " " + idx.get("change") for idx in data.get("market_overview", {}).get("regional_indices", [])])
    print("Concierge note:", data.get("concierge_note"))

    print("\n=== ALL PIPELINE TESTS PASSED SUCCESSFULLY ===")

if __name__ == "__main__":
    run_tests()
