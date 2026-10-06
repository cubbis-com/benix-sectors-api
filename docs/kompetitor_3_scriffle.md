# Analisis Kompetitor 3: Scriffle (thelast10years)

> **Sectors Hackathon 2026** — Track 2: Automation & Workflows  
> **Repository:** [https://github.com/rayyanekaputra/scriffle](https://github.com/rayyanekaputra/scriffle)  
> **Teaser Video:** [https://www.youtube.com/watch?v=RtfPdk06gi0](https://www.youtube.com/watch?v=RtfPdk06gi0)  
> **Judging Video:** [https://www.youtube.com/watch?v=hlduJlEXh_4](https://www.youtube.com/watch?v=hlduJlEXh_4)  
> **Authors:** Rayyan Eka Putra & Artya Aryatama (`@thelast10years`)

---

## 1. Ringkasan Proyek & Value Proposition

**Scriffle** adalah kanvas visual (*visual research and automation workspace*) interaktif berbasis kartu/node untuk saham Indonesia (IDX), yang terintegrasi langsung dengan Sectors API v2.

Konsep dasarnya mirip perpaduan antara **Miro/Figma canvas dengan Node-RED/Zapier**, di mana pengguna menyambungkan kartu-kartu data (*Watcher, Condition, Alert, Action*) menjadi alur kerja otomasi riset tanpa harus bolak-balik berpindah tab browser (*no more juggling tabs*).

> **Problem Statement:** *"Intended for stock researchers. Scriffle, empowered by Sectors data, gives the users freedom to automate their research visually without having to fetch data from other places manually. No more juggling tabs."*

---

## 2. Arsitektur & Tech Stack

```text
User action / polling timer
          │
          ▼
POST /api/engine/trigger
  ├── Sectors API (live, jika API key diinput)
  └── Randomized mock engine (offline — distribusi harga realistis ±0–7%)
          │
          ▼
graphEngine.ts (BFS Graph Traversal)
  ├── BFS traversal dari Watcher / Screener source nodes
  ├── Evaluasi aturan Condition via dslEngine.ts (expr-eval sandbox)
  ├── Eksekusi downstream Note / Alert / Action nodes
  └── Action mutations:
        ├── Spawns kartu baru di canvas
        ├── Calls reportExporter.ts (Sectors fundamental brief → file PDF/HTML)
        └── Fires discordWebhook.ts (rich embed ke Discord)
          │
          ▼
SQLite via Prisma ORM (prisma/dev.db)
```

- **Runtime & Package Manager:** Bun (v1.4+) atau Node.js (v18+)
- **Frontend & UI Canvas:** Next.js / React dengan Tailwind CSS v4 (desain flat 2px outline tanpa drop shadow, font Stack Sans Text, ikon MingCute)
- **Database & State:** SQLite lokal (`prisma/dev.db`) dikelola via Prisma ORM 5.22.0
- **Sinkronisasi & Polling:** SWR dengan *short-poll* interval 2 detik pada `/api/canvas` dan `/api/logs` (sengaja tanpa WebSocket agar bebas overhead koneksi)
- **Engine Aturan Logika:** `expr-eval` (sandbox parser matematika dan DSL yang aman, tanpa fungsi `eval()` mentah)
- **Testing:** Vitest v5 unit test suite

---

## 3. Fitur Utama yang Dibangun

### A. 10 Jenis Kartu Canvas (10 Canvas Nodes):
Scriffle memiliki 10 jenis kartu interaktif yang dibagi menjadi 2 kategori:

1. **Kartu Otomasi (6 Automation Nodes):**
   - **AI Screener:** Menjalankan kueri pencarian bahasa alami langsung ke API Sectors (contoh: *"Top 5 banks by market cap"* atau *"Coal miners with dividend yield above 8%"*).
   - **Watcher:** Memantau ticker spesifik (misal: BBCA) secara berkala atau memindai daftar *Top Gainers / Losers* harian se-IHSG.
   - **Condition:** Menjalankan percabangan logika (*True / False path*) berbasis aturan matematika kustom (contoh: *"if price_change > 3.5 && volume > 1000000"*).
   - **Sticky Note:** Kartu catatan dinamis yang teksnya ter-update secara otomatis saat event terpicu.
   - **Alert:** Mengirimkan notifikasi langsung ke peramban web atau webhook ke kanal **Discord**.
   - **Action:** Memicu aksi otomatis seperti membuat kartu baru di kanvas atau mengekspor laporan fundamental emiten (*institutional research brief*) ke format HTML/PDF.

2. **Kartu Brainstorming & Anotasi (4 Annotation Nodes):**
   - **Text Block:** Catatan bebas dengan formatting heading, bold, dan highlight marker.
   - **Sticker:** Lencana emoji dan tag penanda area kanvas.
   - **Image:** Mengunggah atau menempelkan gambar/screenshot grafik via clipboard (`Ctrl+V`).
   - **File:** Melampirkan dokumen riset untuk dipratinjau di browser.

### B. Preset Templat Siap Pakai:
- *IDX Big 3 Banking Comparison* (komparasi BBCA, BBRI, BMRI)
- *Bluechip Rotation & Auto-Discovery Engine*
- *BBCA Momentum Breakout & Mutator Loop*
- *Macro & Alpha Intelligence Dashboard*
- *Omnibus Alpha Command Center* (tata letak multi-sektor)

### C. Offline Simulation Mock Engine:
Jika pengguna tidak memasukkan API key Sectors, Scriffle tidak mengalami error, melainkan otomatis mengaktifkan mesin simulasi realistis dengan fluktuasi pergerakan acak (distribusi -5% s/d +7%) sehingga kanvas tetap dapat didemokan sepenuhnya.

### D. Keamanan Kunci API Sesi:
Kunci API Sectors hanya disimpan di dalam memori React tab browser (*session-only*), tidak pernah ditulis ke SQLite, localStorage, atau file export kanvas.

---

## 4. Pemanfaatan Data Sectors API

Scriffle berinteraksi dengan **Sectors REST API v2** melalui service terpusat `sectorsApi.ts`:

| Endpoint Sectors API v2 | Parameter & Operasi | Kegunaan dalam Scriffle |
| :--- | :--- | :--- |
| `GET /v2/daily/{symbol}/` | Ticker simbol (misal `BBCA`) | Membaca data harga penutupan, harga pembukaan, volume transaksi, dan fluktuasi persentase harian untuk kartu *Watcher*. |
| `GET /v2/companies/top-changes/` | `?classifications=...&min_mcap_billion=...` | Mengambil daftar saham *Top Gainers* dan *Top Losers* untuk kartu pemantau rotasi sektor. |
| `GET /v2/companies/` | `?q=...` atau `?where=...&order_by=...` | Menggerakkan fitur **AI Screener** (menerjemahkan bahasa alami manusia ke data saham terfilter). |
| `GET /v2/company/report/{symbol}/` | Fundamental report (overview, valuation, financials, dividend) | Diekstraksi oleh modul `reportExporter.ts` untuk menyusun lembaran riset PDF/HTML instan saat kartu *Action* terpicu. |

---

## 5. Kelebihan & Kekurangan (SWOT vs Garda)

### Kelebihan:
- **Inovasi UX & Visual Sangat Menonjol:** Pendekatan visual node canvas membuat eksplorasi terasa sangat menyenangkan, interaktif, dan modern bagi analis data.
- **Fleksibilitas Alur Kerja:** Pengguna bebas merancang logika pipa data sendiri dengan menyambungkan kabel antar kartu.
- **Integrasi Webhook Discord & Ekspor Laporan:** Sangat ramah tim riset institusi yang bekerja secara kolaboratif.
- **Graceful Fallback Mock Data:** Aplikasi tidak rusak meskipun pengguna kehabisan kredit atau lupa memasukkan API key.

### Kelemahan:
- **Kurva Pembelajaran Tinggi (Complex DIY Canvas):** Pengguna awam atau pemilik UMKM harus menyusun node satu per satu secara manual; bukan solusi langsung pakai yang siap saji (*not an out-of-the-box assistant*).
- **Overhead Polling (SWR 2s):** Polling interval 2 detik pada canvas rentan menghabiskan kuota API dengan sangat cepat jika dijalankan dalam mode live tanpa pembatasan ketat.
- **Tanpa Agregasi Berita & Sentimen Regional:** Tidak ada pengkayaan berita dari 20 portal media regional; fokusnya murni pergerakan harga teknikal dan kueri screener.
- **Hanya Pasar Saham Indonesia (IDX):** Belum mencakup bursa regional seperti Singapore Exchange (SGX).

---

## 6. Posisi Strategis Garda (BE.N.IX) terhadap Scriffle

| Aspek | Scriffle | Garda (BE.N.IX) |
| :--- | :--- | :--- |
| **Model Antarmuka** | Kanvas visual node-graph (ala Miro/Node-RED) | **Terminal Keuangan Terpadu (Bloomberg/Anvieo Style) + Asisten Koncierge AI (Gemma 4)** |
| **Kemudahan Penggunaan** | Manual (pengguna merakit kartu & logika kabel sendiri) | **Otomatis & Siap Saji (Tanya jawab langsung, AI menyusun analisis & rekomendasi)** |
| **Suara & Aksesibilitas** | Teks visual tanpa audio | **Audio Suara AI (Text-to-Speech) Interaktif dengan Mode Mute** |
| **Konteks Berita** | Tidak ada berita eksternal | **Agregasi Berita Real-Time dari 20 Portal Media (ID, SG, MY, JP)** |
| **Cakupan Pasar** | IDX saja | **Multi-Sektor IDX + SGX + Komparasi Regional** |
| **Efisiensi Kuota** | SWR 2s polling yang intensif | **Credit-Shield Caching Cerdas di SQLite/JSON (0 Kredit untuk Pertanyaan Berulang)** |
