# Analisis Kompetitor 1: Sentinel Flow (Oky Kurnia Wicaksono)

> **Sectors Hackathon 2026** — Track 2: Automation & Workflows  
> **Repository:** [https://github.com/OkyWoww/sentinel-flow](https://github.com/OkyWoww/sentinel-flow)  
> **Demo Video:** [https://youtu.be/BMVROfameSM](https://youtu.be/BMVROfameSM)  
> **Author:** Oky Kurnia Wicaksono

---

## 1. Ringkasan Proyek & Value Proposition

**Sentinel Flow** adalah pipeline *market watchdog* dan otomasi integritas data pasar modal IDX yang beroperasi secara deterministik (100% *rule-based*, tanpa model ML/LLM). 

Tujuan utamanya adalah memantau keabsahan feed data Sectors API, mendeteksi anomali volume transaksi, pergerakan harga ekstrem, dan pembalikan aliran dana asing (*foreign flow reversal*) secara terus-menerus, lalu mengirimkan notifikasi instan langsung ke kanal **Telegram**.

> **Slogan:** *"Automation that knows when to be suspicious — of abnormal market movements, and of its own data feed."*

---

## 2. Arsitektur & Tech Stack

```text
 ┌───────────────┐   ┌─────────────────┐     ┌──────────────────┐     ┌─────────────────────┐     ┌──────────────────┐
 │ Data Priming  │-->│  Sectors API    │ --> │ Integrity Check  │ --> │ Anomaly Engine      │ --> │ Telegram         │
 │ (one-time,    │   │  (Client & SDK) │     │ (Staleness*,     │     │ (3 Deterministic    │     │ Dispatcher       │
 │  on startup)  │   │                 │     │  Missing/Broken) │     │  Statistical Rules) │     │ + Anti-Spam      │
 └───────────────┘   └─────────────────┘     └──────────────────┘     └─────────────────────┘     └──────────────────┘
                              │                        │                          │                          │
                              └────────────────────────┴──────────────────────────┴──────────────────────────┘
                                              Structured Logger (clean, grep-friendly stdout)
```

- **Backend / Daemon Core:** Python 3.10+ (daemon loop mandiri berbasis CLI)
- **Frontend Dashboard:** React + Vite (opsional, untuk visualisasi status live dan kuota API)
- **Notifikasi & Dispatcher:** Telegram Bot API (`dispatcher.py`)
- **Testing:** Python `unittest` standard library (`test_sentinel.py`, 9 unit tests)
- **Logging:** Structured single-line stdout logging (mudah di-grep)

---

## 3. Fitur Utama yang Dibangun

1. **Cold Start / Data Priming:**
   - Saat aplikasi pertama kali dijalankan, sistem langsung melakukan *pre-seeding* histori 30 hari untuk saham-saham dalam universe (default: LQ45).
   - Tujuannya agar perhitungan indikator teknikal seperti **20-day Simple Moving Average (SMA-20)** langsung siap digunakan sejak siklus pertama tanpa perlu menunggu hari-hari berikutnya.
2. **Smart Staleness Check (IDX Session-Aware):**
   - Mengetahui jadwal jam bursa BEI secara presisi: Sesi 1 (09:00–11:30 WIB), Sesi 2 (13:30–15:00 WIB), jeda istirahat siang, akhir pekan, dan hari libur bursa.
   - Pengecekan *stale data* dinonaktifkan otomatis saat bursa tutup, sehingga tidak membanjiri log atau menimbulkan *false alarm*.
3. **Engine Anomali Statistik Deterministik (3 Aturan):**
   - **Volume Spurt:** Mendeteksi lonjakan volume jika `volume_hari_ini > 3.0 × SMA-20 Volume`.
   - **Sector Outlier:** Mendeteksi saham yang melonjak/anjlok ekstrem (`|perubahan_harga| > 5.0%`) padahal indeks industrinya tenang (`perubahan_sektor ≤ 0.5%`).
   - **Foreign Flow Reversal:** Memberikan sinyal awal ketika akumulasi/distribusi asing berlawanan dengan arah harga (net buy/sell asing `> Rp 5 Miliar` berlawanan tren harga).
4. **Anti-Spam Cooldown Lock:**
   - Setiap pasangan `(ticker, rule)` yang sudah terpicu sekali akan dikunci (*locked*) selama sisa hari perdagangan tersebut guna mencegah *alert fatigue* bagi trader di Telegram.
5. **Manajemen Kuota API (Credit Budgeting):**
   - Dibatasi strictly `< 1.000 panggilan/hari`.
   - Menggunakan *batch concurrency* dan *exponential backoff retry* (maksimal 3 kali percobaan) saat menerima respon HTTP 429 (*Too Many Requests*).

---

## 4. Pemanfaatan Data Sectors API

Sentinel Flow berinteraksi dengan Sectors Financial API melalui modul `sectors_client.py` dengan endpoint spesifik:

| Endpoint Sectors | Data yang Diambil | Kegunaan dalam Sentinel Flow |
| :--- | :--- | :--- |
| `GET /v1/daily/{ticker}/` | Harga penutupan terkini, volume harian, dan `% price change`. | Input perhitungan *Volume Spurt* dan *Sector Outlier*. |
| `GET /v1/foreign-flow/{ticker}/` | Net foreign buy / net foreign sell harian. | Menghitung anomali *Foreign Flow Reversal* (> Rp 5M). |
| `GET /v1/company/report/{ticker}/?days=30` | Data historis 30 hari perdagangan terakhir. | *Cold-start baseline priming* untuk membentuk nilai SMA-20. |

### Strategi Optimasi Kuota Sectors:
- **Universe Terbatas:** Fokus pada saham liquid (LQ45), bukan seluruh 900+ emiten IHSG, guna menghemat kuota API harian.
- **Polling Cadence:** Interval polling default diatur 300 detik (5 menit).
- **Proactive 429 Handling:** Pembacaan response header dan penundaan otomatis jika kuota mendekati batas limit.

---

## 5. Kelebihan & Kekurangan (SWOT vs Garda)

### Kelebihan:
- **Reliabilitas Tinggi:** 100% deterministik, zero halusinasi, zero latency LLM.
- **Kepatuhan Jam Bursa:** Logika waktu bursa Indonesia diimplementasikan dengan sangat rapi (`market_hours.py`).
- **Alert Langsung ke Telegram:** Sangat praktis untuk trader aktif yang tidak ingin membuka dashboard web terus-menerus.

### Kelemahan:
- **Tanpa Konteks Kualitatif (No News / Narrative):** Sentinel Flow hanya bisa memberi tahu *"BBCA volume 4.2x SMA"*, tetapi **tidak tahu alasan fundamental/berita di baliknya** (apakah karena rilis laporan keuangan, aksi korporasi dividen, atau sentimen suku bunga).
- **Cakupan Terbatas:** Hanya pasar saham Indonesia (IDX LQ45), tidak ada multi-pasar (seperti SGX) atau multi-sektor UMKM.
- **Tidak Interaktif:** Tidak ada asisten AI untuk tanya jawab, konsultasi strategi, atau eksplorasi data lebih lanjut.

---

## 6. Posisi Strategis Garda (BE.N.IX) terhadap Sentinel Flow

| Aspek | Sentinel Flow | Garda (BE.N.IX) |
| :--- | :--- | :--- |
| **Pendekatan Analisis** | Hanya kuantitatif statistik | **Kuantitatif Sectors + Kualitatif Berita Regional (20 Portal)** |
| **Output Insight** | Baris sinyal singkat di Telegram | **Rangkuman Eksekutif Koncierge + Audio Suara TTS + Portal Web Interaktif** |
| **Sumber Berita** | Tidak ada | **Agregator Berita Real-Time (Indonesia, Singapura, Malaysia, Jepang)** |
| **Cakupan Pasar** | IDX (LQ45 saja) | **Multi-Sektor IDX + SGX + Komparasi Regional** |
| **Model AI** | Tanpa AI / Tanpa LLM | **Gemma 4 AI Market Concierge dengan Memory & Reasoning** |
