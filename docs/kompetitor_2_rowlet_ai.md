# Analisis Kompetitor 2: RowletAI (Gio-AI-Team)

> **Sectors Hackathon 2026** — Track 3: Market Intelligence  
> **Repository:** [https://github.com/Enderise920/Gio-AI-Team](https://github.com/Enderise920/Gio-AI-Team)  
> **Teaser Video:** [https://youtu.be/O8lVveZkEWg](https://youtu.be/O8lVveZkEWg)  
> **Judging Video:** [https://youtu.be/S_PoMuL-Kek](https://youtu.be/S_PoMuL-Kek)  
> **Social Media:** [https://www.instagram.com/rowlet.ai](https://www.instagram.com/rowlet.ai)  
> **Author:** Gio-AI-Team (Enderise920)

---

## 1. Ringkasan Proyek & Value Proposition

**RowletAI** adalah dashboard riset ekuitas pasar modal Indonesia (*Indonesian Equity Market Intelligence*) yang bertujuan mengubah data pasar yang terfragmentasi menjadi wawasan perusahaan yang terstruktur, dapat dibandingkan (*comparable*), dan berbasis bukti (*evidence-driven*).

Fokus utamanya adalah membantu investor ritel menyaring saham berpotensi naik berlipat (*multibagger*) menggunakan model skor kepemilikan mereka yang disebut **"Bagger Radar"**, dilengkapi dengan komparasi teman sekelas (*peer groups*) dan jurnal riset metodologi yang transparan.

> **Problem Statement:** *"RowletAI helps Indonesian equity investors and researchers turn fragmented market data into clear, comparable, and evidence-driven company insights."*

---

## 2. Arsitektur & Tech Stack

- **Framework Aplikasi:** Python **Streamlit** (aplikasi monolitik besar dengan file utama `app/dashboard.py` mencapai lebih dari 43.000 baris kode).
- **Data Processing & Analytics:** Pandas, NumPy.
- **Visualisasi & Charting:** Plotly (`plotly.graph_objects`), CSS kustom yang disematkan ke komponen HTML Streamlit.
- **Integrasi Pihak Ketiga Tambahan:** Integrasi API gambar (Unsplash, Pexels, Pixabay) untuk ilustrasi profil visual emiten.
- **Penyimpanan Data:** Kombinasi file JSON pra-hitung (*precomputed snapshots*) di direktori `data/` dan cache file runtime lokal.

---

## 3. Fitur Utama yang Dibangun

1. **Bagger Radar (Multibagger Screening):**
   - Algoritma penilaian gabungan (*composite scoring*) yang mengukur daya tarik saham Indonesia berdasarkan 4 dimensi utama:
     - **Fundamentals Score:** Pertumbuhan laba, margin operasional, ROE, solvabilitas.
     - **Momentum Score:** Tren kekuatan harga, likuiditas, dan aksi volume.
     - **Valuation Score:** Relativitas PE, PBV terhadap rata-rata historis dan industrinya.
     - **Risk Metrics:** Volatilitas, beta pasar, dan profil risiko utang.
2. **Company Journal & Evidence Dossier:**
   - Halaman profil mendalam untuk setiap emiten dengan penjelasan transparan mengenai bagaimana skor dihitung.
   - Menyertakan catatan metodologi riset untuk mengedukasi investor mengenai kalkulasi rasio keuangan.
3. **Compare Insight (Curated Peer Comparison):**
   - Fitur komparasi *head-to-head* antara emiten terpilih dengan kelompok kompetitor sejenisnya (*peer groups*).
   - Menyediakan grup kurasi lokal (misal: klaster produsen batu bara `AADI.JK` dengan emiten tambang sekelasnya) agar perbandingan rasio keuangan benar-benar relevan dan tidak bias.
4. **Branding & Visual Experience:**
   - Menggunakan maskot burung hantu ("Rowlet") dan antarmuka visual bertema modern dengan banner visual terdedikasi di landing page dan sidebar.

---

## 4. Pemanfaatan Data Sectors API

RowletAI mengombinasikan pemanggilan langsung ke **Sectors REST API v2** dengan basis data lokal berupa **file snapshot JSON terhitung**:

### A. Endpoint Sectors API v2 yang Digunakan:
| Endpoint Sectors | Parameter & Bentuk | Kegunaan dalam RowletAI |
| :--- | :--- | :--- |
| `GET /v2/companies/` | `?category=...&sub_sector=...` | Mengambil direktori emiten, klasifikasi sektor, dan pemetaan industri bursa IDX. |
| `GET /v2/company/report/{symbol}/` | Overview, valuation, financials, dividend, ownership | Mengisi lembar kerja fundamental komprehensif, laba bersih, neraca keuangan, dan kepemilikan institusi. |
| `GET /v2/daily/{symbol}/` | Seri harga OHLCV & volume | Menampilkan grafik tren harga harian dan kalkulasi momentum di chart Plotly. |

### B. Pemanfaatan Data Snapshot Lokal (`data/*.json`):
Untuk menjaga performa rendering Streamlit dan memangkas konsumsi kredit API, RowletAI menyiapkan beberapa file data lokal:
- `bagger_scores.json`: Skor radar siap pakai untuk emiten IDX.
- `fundamentals.json`: Snapshot data rasio fundamental hasil pra-proses.
- `momentum_scores.json` & `risk_metrics.json`: Metrik teknikal & risiko terhitung.
- `company_profiles.json`: Deskripsi dan profil bisnis perusahaan.
- `local_peer_groups.json`: Pemetaan kelompok kompetitor industri (misal: industri batubara, perbankan).
- `daily_cache.json` & `journal_report_cache.json`: Cache lokal otomatis saat API dipanggil.

---

## 5. Kelebihan & Kekurangan (SWOT vs Garda)

### Kelebihan:
- **Metrik Analisis Fundamental Sangat Kaya:** Menyajikan pembobotan rasio keuangan yang sangat detail dan transparan bagi investor penganut analisis fundamental murni (*value investing*).
- **Curated Peer Groups:** Analisis komparasi antar sesama pemain industri memberikan konteks yang adil (tidak membandingkan bank dengan pertambangan).
- **Branding yang Kuat:** Memiliki identitas maskot dan visual branding yang menarik bagi investor pemula.

### Kelemahan:
- **Arsitektur Monolitik yang Berat:** File `app/dashboard.py` yang membengkak hingga >43.000 baris kode sangat rawan terhadap masalah performa, *maintainability*, dan latency rendering Streamlit saat data bertambah besar.
- **Sifatnya Statis (Bukan Agen Interaktif):** Tidak ada kemampuan percakapan interaktif (*conversational AI*); pengguna hanya membaca dashboard pasif.
- **Tidak Memiliki Agregator Berita Pasar:** Tidak ada pengkayaan berita dari portal media keuangan; tidak bisa menjelaskan sentimen terkini atau isu makro ekonomi di luar angka laporan keuangan.
- **Hanya Pasar Domestik (IDX):** Terbatas pada saham Indonesia, tanpa jangkauan ke bursa regional seperti Singapura (SGX).

---

## 6. Posisi Strategis Garda (BE.N.IX) terhadap RowletAI

| Aspek | RowletAI | Garda (BE.N.IX) |
| :--- | :--- | :--- |
| **Model Interaksi** | Dashboard Streamlit pasif (tabel & grafik) | **Asisten AI Koncierge Percakapan (Gemma 4) + Bloomberg Technical UI + Audio TTS** |
| **Integrasi Berita** | Tidak ada agregasi berita | **Agregasi Berita Real-Time dari 20 Portal Media (ID, SG, MY, JP)** |
| **Cakupan Pasar** | Hanya saham Indonesia (IDX) | **Multi-Sektor IDX + SGX + Komparasi Lintas Negara** |
| **Arsitektur Sistem** | Monolitik Streamlit (>43k LOC) | **FastAPI Middleware Berkinerja Tinggi + SQLite Caching Ringan + Responsive Portal** |
| **Target Pengguna** | Investor ritel penggemar rasio | **Pemilik Usaha UMKM, Trader, & Eksekutif Korporat yang Membutuhkan Insight Seketika** |
