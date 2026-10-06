---
name: sectors-api-skill
description: >-
  Specialized skill for querying and extracting financial data from Sectors Financial API v2 (IDX, SGX, KLSE, Mining)
  with strict credit-shield caching protocols to preserve quota.
---

# Sectors Financial API Skill

## Purpose & Overview
This skill guides agents and developers to query the **Sectors Financial API v2** (`https://api.sectors.app/v2/`) with maximum efficiency, zero quota waste, and 100% adherence to API authentication and billing rules.

---

## 1. Authentication & Security Rules
- **Header**: `Authorization: <SECTORS_API_KEY>` (Raw string, **TANPA** prefix `Bearer`).
- **User-Agent**: Wajib menyertakan header `User-Agent: SectorsMiddleware/1.0` atau `Mozilla/5.0` agar tidak diblokir Cloudflare dengan 403 Forbidden.
- **Base URL**: `https://api.sectors.app/v2`

```python
import os, requests
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
```

---

## 2. Credit Shield Protocol (Aturan Proteksi Kuota)
Setiap panggilan yang tidak perlu akan membuang kredit langganan:
- **Helper Lists** (`/v2/subsectors/`, `/v2/industries/`, `/v2/tags/`): **Cache 24 Jam**. Jangan pernah panggil berulang kali dalam satu hari.
- **Company Reports & Financials** (`/v2/company/report/{symbol}/`): **Cache 6 Jam**. Gunakan parameter `sections` (misal `sections=overview,valuation`) untuk mengurangi payload.
- **Daily Prices & Top Movers** (`/v2/companies/top-changes/`, `/v2/most-traded/`): **Cache 30–60 Menit** selama jam bursa.
- **Company Screener**:
  - Gunakan structured query (`where=...`, `order_by=...`) yang hanya berbiaya **1 kredit**.
  - Hindari natural language `?q=` jika bisa diformulasikan ke SQL karena `?q=` memotong **3 kredit**.

---

## 3. Decision Matrix Pemilihan Endpoint

| Kebutuhan Data | Endpoint Rekomendasi | Biaya Kredit | Catatan Kunci |
|---|---|---|---|
| Fundamental Emiten | `GET /v2/company/report/{symbol}/` | 1 kredit/seksi | Filter `sections=overview,valuation,dividend` |
| Saham Paling Ramai | `GET /v2/most-traded/` | 2 kredit | Rentang tanggal default s/d 90 hari |
| Top Gainers/Losers | `GET /v2/companies/top-changes/` | 1-2 kredit | `classifications=top_gainers&periods=1d` |
| Arus Modal Asing | `GET /v2/foreign-flow/{symbol}/` | 1 kredit | Ambil `net_foreign_inflow` dan `foreign_share` |
| Bandarmologi / Broker | `GET /v2/broker-summary/{symbol}/top/` | 2 kredit | Menampilkan top buyer dan seller broker |
| Filter Saham Sektoral | `GET /v2/companies/?where=sub_sector='banks'` | 1 kredit | SQL-like query |
| Keuangan Kuartalan | `GET /v2/financials/quarterly/{symbol}/` | 1 kredit/kuartal | Neraca & laba-rugi per kuartal |

---

## 4. Normalisasi Simbol Ticker
Sistem mewajibkan normalisasi ticker sebelum melakukan request:
- Simbol IDX: Hilangkan `.JK` (Contoh: `BBCA.JK` -> `BBCA`, `TLKM.JK` -> `TLKM`).
- Huruf kapital standar: `bbri` -> `BBRI`.
- Simbol SGX: Hilangkan `.SI` jika ada (Contoh: `D05.SI` -> `D05`).
