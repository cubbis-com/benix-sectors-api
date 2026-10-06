---
name: news-scraper-nlp-skill
description: >-
  Specialized skill for Web Scraping and Financial NLP across 20 portals per country
  (Indonesia, Singapore, Malaysia, Japan), matching headlines to stocks/sectors with zero credit consumption.
---

# Web Scraper & Financial NLP Engineer Skill

## 1. Domain Overview
This skill governs the automated extraction, deduplication, ticker matching, and sentiment classification of financial news across 80 portals (20 per country: Indonesia, Singapore, Malaysia, Japan).

## 2. Core Capabilities
1. **Zero-Credit Aggregation**:
   - Queries public RSS & web news endpoints at 0 Sectors API credit cost.
   - Automatically caches items locally in SQLite (`news_headlines`) and JSON (`data/daily_news_store.json`).
2. **Daily Execution Safeguard**:
   - Checks if today already has >= 10 records. If missing, automatically triggers scraping on startup or on schedule.
3. **Multilingual Keyword & Entity Matching**:
   - Matches tickers (`BBCA`, `TLKM`, `D05`, `Z74`, `ASII`, `SMGR`, `CPIN`, `JPFA`, etc.) across Indonesian, English, Malay, and Japanese headlines.
4. **Sentiment & Market Relevance Tagging**:
   - Categorizes news into `BULLISH`, `BEARISH`, or `NEUTRAL` based on financial linguistic tokens.
   - Attaches relevant sector tags (`Financials`, `Telecommunications`, `Agribusiness`, `Consumer Goods`, `Regional Macro`).

## 3. Covered Portals (20 Per Country)
- **Indonesia (ID)**: CNBC Indonesia, Bisnis.com, Kontan, Kompas Money, Detik Finance, Antara News, Tempo Bisnis, Investor Daily, Katadata, Kumparan Bisnis, Liputan6 Bisnis, Media Indonesia, IDN Times, Sindo News, Okezone, Warta Ekonomi, Bareksa, Beritasatu, Inilah.com, Suara Bisnis.
- **Singapore (SG)**: The Business Times, CNA Business, The Straits Times, AsiaOne Business, Today Online, Singapore Business Review, Vulcan Post SG, Yahoo Finance SG, Fintechnews SG, Seedly, DollarsAndSense, The Independent SG, Mothership, Rice Media, DealStreetAsia, e27, Tech in Asia SG, Hubbis, WealthBriefingAsia, EdgeProp SG.
- **Malaysia (MY)**: The Star Business, The Edge Malaysia, Free Malaysia Today (FMT), Malay Mail Money, Bernama, New Straits Times, Focus Malaysia, SoyaCincau, RinggitPlus, The Malaysian Reserve, Astro Awani, Berita Harian, Utusan Bisnes, Vulcan Post MY, Fintech News MY, Sin Chew Daily, Oriental Daily, Dagang News, Business Today MY, Nanyang Siang Pau.
- **Japan (JP)**: Nikkei Asia, NHK World-Japan Business, The Japan Times, Mainichi Business, Kyodo News, Asahi Shimbun, Tokyo Reporter, Japan Today, Nippon.com Economy, Jiji Press, Tech in Asia JP, The Bridge JP, NewsPicks, Diamond Online, Toyo Keizai, President Online, Nikkei Veritas, ITmedia Business, ASCII.jp, Yahoo Japan Finance.

## 4. Operational Commands
- Endpoint: `GET /api/v1/portal/news-wire?country=ALL|ID|SG|MY|JP&limit=30`
- Scrape Trigger: `POST /api/v1/portal/trigger-scrape?force=true`
- Pre-Market Briefing: `GET /api/v1/portal/market-briefing`
