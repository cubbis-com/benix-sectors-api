# BE.N.IX — Anvieo Trading Analytics (Sectors AI Portal & Gateway)

Gateway dan Middleware API Python berkinerja tinggi untuk **Sectors Financial API v2** yang dirancang khusus untuk Hackathon Sectors (Track 1: AI Agents & Assistants / Track 2: Automation & Workflows).

Dilengkapi dengan protokol **Credit Shield** (Smart SQLite Caching) untuk melindungi kuota kredit API yang terbatas, serta **Tim Modular Agentic AI Skills** terpisah untuk koding dan eksekusi web dalam membangun **Portal Berita & Informasi Pasar Modal Indonesia**.

---

## 🌟 Arsitektur Tim Modular Agentic AI Skills

Sistem Agentic AI dipisahkan menjadi dua layer:
1. **Layer Koding (Skill Definitions / Cheatsheets)** di `.agents/skills/` dan `~/.gemini/config/skills/`: Berisi prompt persona, aturan jurnalisme, dan panduan kode untuk AI assistant (Antigravity & Gemini Agents).
2. **Layer Eksekusi Web & Backend** di `agents/` & `routers/`: Modul Python asinkron yang dapat dipanggil langsung melalui HTTP API oleh web portal atau scheduler otomatis.

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        Web Portal Frontend                             │
│   (Running Ticker, Hero News, Analisis Emiten, Chat Garda AI)          │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                       (REST API: /api/v1/...)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   Garda Chief Orchestrator                             │
│      (/api/v1/agent/skills/orchestrator/publish-news & publish-pulse)  │
└───────┬───────────────────────────┬────────────────────────────┬───────┘
        │                           │                            │
        ▼                           ▼                            ▼
┌──────────────────┐    ┌──────────────────────┐    ┌────────────────────┐
│ Sectors API      │    │ Trader Analyst AI    │    │ Financial          │
│ Specialist       │    │ Skill                │    │ Journalist AI      │
│ (Data & Cache)   │    │ (Valuasi/Bandarmologi│    │ (Wartawan Portal)  │
└───────┬──────────┘    └───────────┬──────────┘    └────────────┬───────┘
        │                           │                            │
        └───────────────────────────┼────────────────────────────┘
                                    ▼
                    ┌──────────────────────────────┐
                    │    Portal Database (SQLite)  │
                    │      (portal_articles)       │
                    └───────────────┬──────────────┘
                                    │ (Broadcast Alert)
                                    ▼
                    ┌──────────────────────────────┐
                    │    WhatsApp Gateway API      │
                    │    (wa.inovasiuitjbt.uk)     │
                    └──────────────────────────────┘
```

---

## 🤖 6 Spesialisasi Agentic AI Skills (Gemini / Antigravity Registered)

| No | Nama Skill | Direktori Skill (Gemini / Antigravity) | Endpoint Eksekusi Web | Deskripsi & Tugas Utama |
|---|---|---|---|---|
| 1 | **Sectors API Specialist** | `.agents/skills/sectors-api-skill/SKILL.md` | `/api/v1/helpers/...`, `/api/v1/screener` | Pengambilan data bursa, normalisasi simbol, dan proteksi kuota kredit (Credit Shield). |
| 2 | **Trader & Market Analyst** | `.agents/skills/trader-analyst-skill/SKILL.md` | `POST /api/v1/agent/skills/trader/analyze` | Analisis valuasi (P/E, Dividend), bandarmologi broker, foreign flow, dan penentuan level support/resistance. |
| 3 | **Financial Journalist (Wartawan)** | `.agents/skills/financial-journalist-skill/SKILL.md` | `POST /api/v1/agent/skills/journalist/write-article` | Menulis artikel berita pasar modal berstandar jurnalisme ekonomi Indonesia (Kontan/Bisnis/CNBC). |
| 4 | **Garda Chief Orchestrator** | `.agents/skills/garda-orchestrator-skill/SKILL.md` | `POST /api/v1/agent/skills/orchestrator/publish-news` | Otomasi end-to-end: Ambil data -> Analisis trader -> Tulis berita -> Terbitkan ke DB -> Push WhatsApp. |
| 5 | **Backend Developer AI** | `.agents/skills/backend-dev-skill/SKILL.md` | `POST /api/v1/agent/skills/backend/screener-query` | Pembuatan API contracts, query builder teroptimasi, skema database, dan cron schedulers. |
| 6 | **Frontend Developer AI** | `.agents/skills/frontend-dev-skill/SKILL.md` | `GET /api/v1/agent/skills/frontend/ui-blueprint` | Desain token UI dark mode, layout berita portal, ribbon running ticker, dan widget emiten. |

---

## 🚀 Panduan Memulai Cepat

### 1. Prasyarat
- Python 3.10+
- Dependensi: `fastapi`, `uvicorn`, `httpx`, `pydantic`, `pydantic-settings`, `python-dotenv`, `aiosqlite`

### 2. Instalasi Dependensi
```bash
cd API
pip install -r requirements.txt
```

### 3. Konfigurasi Environment (`.env`)
```env
SECTORS_API_KEY=your_sectors_api_key_here
SECTORS_BASE_URL=https://api.sectors.app/v2
SECTORS_MCP_URL=https://sectors-mcp.supertype.ai/mcp

WA_GATEWAY_URL=https://wa.inovasiuitjbt.uk/api/instances/6285717905851/send
WA_TOKEN=your_wa_token_here
WA_DEFAULT_TARGET=6281805040354

PORT=8000
HOST=0.0.0.0
```

### 4. Menjalankan Server Middleware & Portal
```bash
python3 main.py
```

Akses layanan di browser:
- **Interactive Dashboard & Portal Feed**: `http://localhost:8000/`
- **Swagger Interactive API Docs**: `http://localhost:8000/docs`
- **Skills Catalog**: `http://localhost:8000/api/v1/agent/skills/catalog`
- **Portal Articles Feed**: `http://localhost:8000/api/v1/portal/articles`
- **Live Credit Metrics**: `http://localhost:8000/api/v1/metrics/credits`

---

## 🧪 Menjalankan Pengujian Otomatis

1. **Uji Konektivitas API & Credit Shield Cache**:
   ```bash
   python3 test_client.py
   ```
2. **Uji Tim Agentic AI & Penerbitan Berita Otomatis**:
   ```bash
   python3 test_agentic_pipeline.py
   ```

---

## 📡 Contoh Pemanggilan API untuk Web Portal

### 1. Menerbitkan Berita Emiten Otomatis via Garda Orchestrator
```bash
curl -X POST "http://localhost:8000/api/v1/agent/skills/orchestrator/publish-news?symbol=BBCA"
```

### 2. Mengambil Feed Berita untuk Frontend Portal
```bash
curl "http://localhost:8000/api/v1/portal/articles?category=emiten-focus&limit=5"
```

### 3. Menjalankan Analisis Trader AI untuk Halaman Detail Saham
```bash
curl -X POST "http://localhost:8000/api/v1/agent/skills/trader/analyze" \
     -H "Content-Type: application/json" \
     -d '{"symbol": "BMRI"}'
```

### 4. Mengambil UI Blueprint & Token Desain untuk Frontend
```bash
curl "http://localhost:8000/api/v1/agent/skills/frontend/ui-blueprint"
```

---

## 📚 Dokumentasi Lengkap 74 Endpoint
Dokumentasi teknis lengkap seluruh 74 endpoint Sectors API v2 tersedia di:
- `../api-sectors.md` (Root Workspace)
- `./docs/SECTORS_API_DOCUMENTATION.md` (Direktori API)
