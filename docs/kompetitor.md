# Matriks Analisis Kompetitor — Sectors Hackathon 2026

Dokumen ini memuat rangkuman komparatif dari tiga proyek kompetitor di **Sectors Hackathon 2026**, apa saja yang mereka bangun, endpoint dan data apa saja yang mereka manfaatkan dari Sectors API, serta perbandingannya terhadap **Garda (BE.N.IX — Anvieo Trading Analytics)**.

Detail mendalam untuk masing-masing kompetitor telah disusun dalam dokumen terpisah:
1. 📄 **[Analisis Mendalam 1: Sentinel Flow](./kompetitor_1_sentinel_flow.md)**
2. 📄 **[Analisis Mendalam 2: RowletAI](./kompetitor_2_rowlet_ai.md)**
3. 📄 **[Analisis Mendalam 3: Scriffle](./kompetitor_3_scriffle.md)**

---

## 1. Matriks Komparasi 3 Kompetitor vs Garda (BE.N.IX)

| Kategori Analisis | Sentinel Flow | RowletAI | Scriffle | Garda (BE.N.IX) |
| :--- | :--- | :--- | :--- | :--- |
| **Track Hackathon** | Track 2: Automation & Workflows | Track 3: Market Intelligence | Track 2: Automation & Workflows | **Multi-Track: Market Intel + Agentic Workflows** |
| **Konsep Utama** | *Market watchdog* deterministik & data integrity | Dashboard valuasi & skor "Bagger Radar" | Kanvas visual node-graph ala Miro/Node-RED | **AI Market Concierge 5-Bintang + Regional News Aggregator** |
| **Tech Stack** | Python, React (opsional), Telegram Bot | Python Streamlit (>43k baris kode), Plotly | Bun, Next.js, Tailwind v4, Prisma SQLite, `expr-eval` | **FastAPI, Pure Vector SVG, SQLite Caching, Gemma 4 LLM** |
| **Pemanfaatan Sectors API** | • `GET /v1/daily/{ticker}/`<br>• `GET /v1/foreign-flow/{ticker}/`<br>• `GET /v1/company/report/{ticker}/?days=30` | • `GET /v2/companies/`<br>• `GET /v2/company/report/{symbol}/`<br>• `GET /v2/daily/{symbol}/`<br>• Static JSON snapshots | • `GET /v2/daily/{symbol}/`<br>• `GET /v2/companies/top-changes/`<br>• `GET /v2/companies/?q=...`<br>• `GET /v2/company/report/{symbol}/` | • `GET /v2/companies/`<br>• `GET /v2/daily/{symbol}/`<br>• `GET /v2/company/report/{symbol}/`<br>• Multi-sector IDX + SGX coverage |
| **Strategi Kuota API** | Quota budget log (<1.000 calls/hari), LQ45 restriction | Snapshot data statis di direktori `data/` | SWR polling 2s + fallback mock random generator | **Smart Credit-Shield Cache di SQLite/JSON (Zero Credit Repetition)** |
| **Integrasi Berita Eksternal** | ❌ Tidak ada berita | ❌ Tidak ada berita | ❌ Tidak ada berita | **✅ Agregator 20 Portal Berita x 4 Negara (ID, SG, MY, JP)** |
| **Interaksi Pengguna** | Peringatan pasif via Telegram | Dashboard visual statis Streamlit | Rakit kartu manual di kanvas (DIY) | **Percakapan Dua Arah (Teks + Audio Suara TTS) + Widget Kustom** |
| **Cakupan Pasar** | IDX (LQ45 saja) | IDX (Saham Indonesia saja) | IDX (Saham Indonesia saja) | **Multi-Sektor (IDX & SGX) + Makro Regional** |
| **Target Pasar** | Trader kuantitatif teknikal | Investor ritel pencari *multibagger* | Peneliti saham institusional | **Pemilik Bisnis UMKM, Investor Ritel, & Trader Lintas Sektor** |

---

## 2. Ringkasan Eksekutif dari Masing-Masing Kompetitor

### 1. Sentinel Flow (Oky Kurnia Wicaksono)
* **Apa yang dibuat:**
  - Pipeline daemon otomatis berbasis Python yang memvalidasi integritas feed data pasar bursa BEI.
  - Tiga aturan anomali deterministik tanpa model ML: *Volume Spurt* (>3x SMA-20), *Sector Outlier* (>5% move vs ≤0.5% sektor), dan *Foreign Flow Reversal* (>Rp 5 Miliar net flow berlawanan arah).
  - Mekanisme *cold-start priming* data historis 30 hari dan *cooldown lock* harian untuk mencegah spam di Telegram.
* **Pemanfaatan Data Sectors:**
  - `GET /v1/daily/{ticker}/` untuk harga & volume.
  - `GET /v1/foreign-flow/{ticker}/` untuk aliran dana asing.
  - `GET /v1/company/report/{ticker}/?days=30` untuk perhitungan moving average.
* **Kelemahan Utama:** Tidak memiliki analisis naratif berita (tidak tahu penyebab kenaikan saham) dan tidak ada interaktivitas AI.

---

### 2. RowletAI (Gio-AI-Team)
* **Apa yang dibuat:**
  - Aplikasi dashboard Streamlit monolitik skala masif dengan maskot burung hantu ("Rowlet").
  - Sistem penilaian komposit *Bagger Radar* yang menggabungkan fundamental, momentum, valuasi, dan metrik risiko.
  - Halaman *Company Journal* dan komparasi teman sekelas industri (*Curated Peer Groups* seperti tambang batubara `AADI.JK`).
* **Pemanfaatan Data Sectors:**
  - `GET /v2/companies/` untuk struktur industri bursa.
  - `GET /v2/company/report/{symbol}/` untuk laporan keuangan lengkap dan rasio valuasi.
  - `GET /v2/daily/{symbol}/` untuk grafik harga harian.
  - Menyiapkan snapshot lokal `data/*.json` untuk menghemat kredit.
* **Kelemahan Utama:** Kode monolitik sangat besar (>43.000 baris dalam satu file), murni dashboard baca pasif tanpa kemampuan percakapan interaktif, dan tanpa integrasi berita.

---

### 3. Scriffle (thelast10years / Rayyan Eka Putra & Artya Aryatama)
* **Apa yang dibuat:**
  - Kanvas visual berbasis kartu/node yang menghubungkan kartu data (*Watcher, Condition, Alert, Action*) dengan kabel logika.
  - 10 jenis kartu interaktif (6 kartu otomasi dan 4 kartu brainstorming).
  - Eksekusi DSL aman menggunakan `expr-eval` (tanpa fungsi `eval()` berbahaya).
  - Integrasi aksi ke notifikasi browser, webhook Discord, dan ekspor laporan fundamental ke format HTML/PDF.
  - Mesin *mock fallback* realistis jika API key tidak tersedia.
* **Pemanfaatan Data Sectors:**
  - `GET /v2/daily/{symbol}/` untuk harga ticker terkini.
  - `GET /v2/companies/top-changes/` untuk filter Top Movers bursa.
  - `GET /v2/companies/?q=...` untuk kueri AI Screener berbasis bahasa alami.
  - `GET /v2/company/report/{symbol}/` untuk menyusun lembaran riset PDF.
* **Kelemahan Utama:** Kurva belajar tinggi (pengguna harus merakit alur kabel sendiri), polling interval 2 detik rentan memakan kuota jika dijalankan langsung, dan tidak ada agregasi sentimen berita regional.

---

## 3. Posisi Menang Garda (BE.N.IX) di Hadapan Dewan Juri

Ketiga kompetitor memiliki kelebihan masing-masing di aspek teknikal bursa (Sentinel di alert Telegram, Rowlet di rasio fundamental, Scriffle di kanvas visual), namun **ketiganya memiliki kelemahan yang sama:**
> **Semua kompetitor hanya mengolah data angka mentah dari IDX, tanpa mengerti narasi atau berita dunia nyata di balik pergerakan angka tersebut.**

Di sinilah **Garda (BE.N.IX)** menjadi solusi paling unggul dan bernilai komersial tinggi:
1. **Sintesis Data + Konteks Narasi (Data + Narrative Context):**
   - Ketika volume saham melonjak, Garda tidak hanya mencatat angka lonjakan (seperti Sentinel), tetapi langsung menghubungkannya dengan **berita terkini dari 20 portal media finansial di 4 negara (Indonesia, Singapura, Malaysia, Jepang)**.
2. **AI Concierge 5-Bintang yang Berempati:**
   - Menyajikan komunikasi dua arah yang hangat, presisi, dan kontekstual bagi pemilik usaha UMKM dan investor ritel, lengkap dengan **suara audio (Text-to-Speech)** yang interaktif.
3. **Cakupan Multi-Sektor & Regional (IDX & SGX):**
   - Tidak terkunci pada pasar domestik Indonesia saja, melainkan mampu membandingkan performa sektor dengan bursa Singapura dan sentimen kawasan ASEAN/Asia Timur.
4. **Efisiensi Kuota Tanpa Kompromi (Zero-Credit Shield):**
   - Menggunakan pipeline SQLite caching lokal dan middleware pintar yang mengutamakan pencarian lokal terlebih dahulu sebelum menyentuh kuota API Sectors, menghemat kuota hingga 95%+.
5. **Estetika Terminal Keuangan Kelas Atas (Anvieo / Bloomberg Style):**
   - Menghindari kotak-kotak kartu pasif yang membosankan, digantikan dengan antarmuka terminal profesional, kolom percakapan terdedikasi setinggi layar (100vh), dan animasi inti neural **Pure Vector SVG 3D** yang 100% tajam bebas blur.

---

## Arsip Data Pengajuan Asli Kompetitor

```markdown
[06/10/26, 09.55.58] Rendy ariawindana: Oky Kurnia Wicaksono  [10:09 PM]
Hi everyone & Sectors Team! :wave:
Project: Sentinel Flow
Track: Track 2 · Automation & Workflows
One-liner: Dirancang untuk analis dan trader pasar modal IDX yang kesulitan memantau integritas data serta lonjakan transaksi secara manual setiap menit, Sentinel Flow menyediakan pipeline otomasi deterministik untuk memvalidasi feed Sectors API dan mengirimkan alert anomali instan ke Telegram tanpa ketergantungan model ML.
GitHub Repo: https://github.com/OkyWoww/sentinel-flow
Demo Video: https://youtu.be/BMVROfameSM

[06/10/26, 09.56.26] Rendy ariawindana:
Project : RowletAI
Track : 3 - Market Intelligence
Problem Statement : RowletAI helps Indonesian equity investors and researchers turn fragmented market data into clear, comparable, and evidence-driven company insights.
Public Repository URL : https://github.com/Enderise920/Gio-AI-Team
Teaser Video URL : https://youtu.be/O8lVveZkEWg
Judging Video URL : https://youtu.be/S_PoMuL-Kek
Social Media Post URL : https://www.instagram.com/rowlet.ai

[06/10/26, 09.56.43] Rendy ariawindana:
project: Scriffle - Visual Research and Automation Workspace for Indonesians Stock
track: Track 02 - Automation and Workflows
problem statement: Intended for stock researchers. Scriffle, empowered by Sectors data, gives the users freedom to automate their research visually without having to fetch data from other place manually. No more juggling tabs.
repo: https://github.com/rayyanekaputra/scriffle
teaser vid: https://www.youtube.com/watch?v=RtfPdk06gi0
judging vid: https://www.youtube.com/watch?v=hlduJlEXh_4
```