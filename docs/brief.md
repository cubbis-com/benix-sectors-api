Bisa banget — dan ini ide yang menarik, tapi **ada pertimbangan penting soal track mana yang paling cocok**. Mari saya jelaskan jujur.

---

## Analisis jujur terhadap syarat hackathon

Ide Anda punya dua fitur inti:

| Fitur | Track mana yang paling masuk akal |
|---|---|
| **Diskusi dengan Garda** (chat AI tentang market, terkoneksi Sectors MCP) | **Track 1 — AI Agents & Assistants** |
| **Portal berisi informasi pasar yang di-update otomatis** (news briefing harian, alert) | **Track 2 — Automation & Workflows** |

Menurut aturan boundary mereka:
> *"A project's track is determined by what the product fundamentally does, not what it looks like. An agent with a dashboard interface still belongs in AI Agents & Assistants."*

Jadi kalau **inti produknya adalah percakapan AI tentang market** (Garda yang bisa menganalisis, bandingkan emiten, jawab pertanyaan tentang pasar), itu **jatuh ke Track 1** — karena itu butuh custom agent logic, bukan sekadar menjawab pertanyaan.

---

## Tapi ini justru keuntungan untuk Anda

Anda punya **dua opsi strategis**:

### Opsi A: Daftar Track 1 (AI Agents & Assistants)
**Cocok jika:** Garda di portal Anda punya logic agent sendiri — bukan sekadar "chatbot yang menampilkan data", tapi mampu:
- Menjalankan **multi-step reasoning** (misal: "bandingkan industri ritel, mana yang lebih menarik?")
- **Memilih sendiri** data Sectors mana yang diquery
- Menyimpan **memory** konteks percakapan
- Menjalankan **tool-use pipeline** sendiri

> Contoh ide: *User bertanya "gimana prospek ritel 2026?" → Garda memanggil Sectors API, ambil data 10 emiten ritel, analisis tren, bandingkan kinerja, lalu jawab dengan insight + data*

**Keuntungan:** AI component sudah wajib di track ini, jadi AI Garda Anda jadi *plus point*, bukan harus nempel ke ide lain.

---

### Opsi B: Daftar Track 2 (Automation & Workflows)
**Cocok jika:** Inti produknya adalah **portal yang kontennya diupdate otomatis** — Garda hanyalah bonus interaktif.

Portal-nya punya:
- **Scheduler harian**: 06.00 WIB → pipeline narik data Sectors → Garda merangkum → otomatis publish berita briefing di portal + push ke WA
- **Trigger-based alerts**: saat data berubah signifikan → otomatis update portal + notifikasi
- **Bukti unattended runs** (screenshot log, timestamp)

> Garda jadi "bonus" — ada tapi bukan fitur utamanya.

**Keuntungan:** WA gateway Anda jadi bukti kuat otonomi.

---

## Rekomendasi saya

Kalau saya harus pilih satu: **daftar Track 1**.

Alasannya:
1. **AI Garda adalah aset terkuat Anda** — itu justru yang paling sulit ditiru tim lain
2. Track 2 bisa dimenangkan dengan pipeline sederhana (cron + API + WA) — persaingannya lebar
3. Track 1 menuntut **custom agent logic** — kalau Garda punya itu, Anda sudah di depan
4. Ide "AI advisor untuk pelaku UMKM yang investasi di industrinya sendiri" itu **unik dan belum ada** — pas untuk Track 1 yang mencari *purpose-built interface untuk specific participant and problem*

---

## Arsitektur sederhana untuk Track 1

```
┌─────────────────────────────────────┐
│         Web Portal (Frontend)       │
│  - Dashboard market data (Sectors)  │
│  - Chat interface dengan Garda      │
│  - Briefing otomatis harian         │
└──────────────┬──────────────────────┘
               │
       ┌───────▼────────┐
       │   Garda Agent  │  ← Custom logic (bukan sekadar prompt)
       │  (AI Core)     │     - Reasoning multi-step
       │                │     - Tool-use pipeline
       │                │     - Memory konteks
       └───────┬────────┘     - Pilih sendiri data Sectors
               │                  yang diquery
       ┌───────▼────────┐
       │  Sectors MCP   │  ← Data source inti (wajib)
       │  / REST API    │
       └────────────────┘

       Bonus: Scheduler + WA Gateway
       (untuk notifikasi otomatis —
        ini bisa jadi selling point
        tambahan tanpa mengubah track)
```

---

## Yang harus Anda siapkan untuk Track 1

1. **Bukti custom agent logic** — dokumentasikan kenapa Garda BUKAN sekadar "chatbot + API", tapi punya orchestration sendiri (reasoning, tool selection, memory)
2. **Demo multi-step task** — misal: user minta "riset sektor retail" → Garda query beberapa endpoint Sectors → analisis → bandingkan → hasilkan insight → semua terdokumentasi
3. **Data Sectors sebagai core** — pastikan output Garda SELALU berdasarkan data Sectors, bukan pengetahuan umum
4. **Briefing otomatis** (bonus) — kalau portal juga punya scheduler harian, ini jadi nilai tambah yang memperkuat produk

**Intinya:** Ide Anda valid, tapi alih-alih "portal news + AI tambahan", **balik perspektifnya** — jadikan Garda sebagai *inti produk* (AI advisor yang memahami market Indonesia), dan portal + automation sebagai *panggung* yang memamerkannya.

Mau saya bantu menyusun **pitch deck sederhana** atau **demo script** untuk track 1 ini?



Secara nyata di dunia bisnis dan finansial, data pasar modal seperti yang disediakan **Sectors** digunakan untuk mengambil keputusan strategis, bukan sekadar melihat harga naik atau turun.

Berikut beberapa contoh penggunaan nyata yang mudah dipahami:

---

### 1. Pengecekan Kesehatan Bisnis Mitra / Klien (*Vendor & Partner Due Diligence*)

* **Kasus Riil:** Sebuah perusahaan manufaktur atau UMKM logistik ingin bekerja sama dengan emiten besar (misal: PT Indofood atau PT Telkom) untuk kontrak jangka panjang bernilai miliaran rupiah.
* **Cara Data Dipakai:**
* Tim finansial melihat **rasio utang (Debt to Equity)** dan **arus kas operasional (Operating Cash Flow)** emiten tersebut.
* Tujuannya memastikan apakah perusahaan mitra tersebut keuangannya sehat dan tidak berisiko gagal bayar atau bangkrut di tengah jalan saat proyek berjalan.



---

### 2. Membaca Tren Industri untuk Peluang Usaha (*Industry Benchmarking*)

* **Kasus Riil:** Pengusaha kuliner atau UMKM ritel ingin mengetahui apakah daya beli masyarakat untuk produk makanan sedang turun atau naik.
* **Cara Data Dipakai:**
* Pengusaha melihat data agregat sektor **Consumer Non-Cyclicals** (perusahaan kebutuhan pokok seperti ICBP, MYOR, UNVR).
* Jika laba bersih dan pendapatan rata-rata emiten di sektor tersebut tumbuh pesat, itu indikator kuat bahwa konsumsi ritel sedang tinggi.
* Pengusaha juga bisa melihat berapa rata-rata margin keuntungan bersih (*Net Profit Margin*) industri tersebut sebagai standar acuan bisnisnya sendiri.



---

### 3. Pemantauan Rantai Pasok & Biaya Bahan Baku (*Supply Chain & Cost Risk*)

* **Kasus Riil:** Pengusaha peternakan ayam atau pabrik pakan butuh memprediksi lonjakan biaya bahan baku pakan jagung/kedelai.
* **Cara Data Dipakai:**
* Memantau emiten sektor pakan ternak (misal: CPIN, JPFA). Laporan keuangan dan pergerakan margin emiten-emiten ini mencerminkan apakah biaya impor bahan baku dunia sedang melonjak atau stabil.



---

### 4. Penyaringan Saham untuk Tabungan/Investasi (*Stock Screening*)

* **Kasus Riil:** Individu yang ingin menabung saham dengan kriteria aman: hanya saham yang rutin membagikan dividen tunai tinggi dan memiliki utang rendah.
* **Cara Data Dipakai:**
* Menggunakan filter: *Dividend Yield > 5%*, *P/E Ratio < 15*, dan *ROE > 10%*.
* Sistem Sectors langsung menyaring ratusan saham di bursa IDX dan mengeluarkan daftar 5–10 saham yang memenuhi kriteria tersebut secara instan.



---

### 5. Bagaimana Ini Dihubungkan ke Ide AI Agent Anda ("Garda")?

Orang awam atau pemilik UMKM biasanya **pusing membaca laporan keuangan 50 halaman** penuh tabel angka.

Di sinilah peran AI Agent:

* **Pengguna bertanya santai:** *"Saya mau jualan bahan bangunan, kondisi industri properti dan konstruksi di Indonesia sekarang lagi lesu atau ramai?"*
* **AI Agent bekerja di balik layar:**
1. Memanggil Sectors API untuk sektor properti & konstruksi.
2. Membaca pertumbuhan pendapatan rata-rata emiten properti dalam 2 kuartal terakhir.
3. Menjawab dengan bahasa manusia: *"Kondisi sedang membaik. Rata-rata pendapatan pengembang naik 12% kuartal ini didorong penjualan rumah subsidi, jadi permintaan bahan bangunan berpeluang tumbuh."*





penjelasan rule nya :

Skip to content

Sectors Hackathon
Indonesia / 2026
Tracks
Rules
Find a team
Prizes
Sponsorship
Sectors Hackathon / Indonesia / 2026
Official rules
Online, Indonesia-wide. Build AI that works with Indonesian financial data. These rules are also available in Bahasa Indonesia; submissions and videos are accepted in Bahasa Indonesia or English.

On this page
01
Spirit of the competition
02
Key dates
03
Eligibility
04
Teams & API credits
05
Build period & work restrictions
06
Project requirements
07
Use of AI
08
Submission requirements
09
Judging
10
Prizes
11
Publicity & content rights
12
Code of conduct
13
Disqualification
14
Support
01
Spirit of the competition
Sectors Hackathon is not a typical coding competition. We don't judge how sophisticated your code is. We judge whether what you build can genuinely be used by real people, today, with Sectors data at its core.

"Solve an interesting problem thoughtfully with
Sectors API"
02
Key dates
Milestone	Date
Registration opens	19 August 2026
Build period opens	19 August 2026
Registration closes	7 October 2026, 23:59 WIB
Build period and submissions close	8 October 2026, 23:59 WIB
Judging period	9–16 October 2026
Winners announced	17 October 2026
Registration closes a day before the submission deadline so onboarding and credit grants can be verified.

03
Eligibility
Open to Indonesian citizens or residents domiciled in Indonesia.
Open to all ages. Participants under 18 must provide parental or guardian consent at registration, covering media publication consent and prize acceptance through a guardian.
Employees, contractors, judges, mentors, and organizers of Supertype, Sectors, and Algoritma, along with their immediate families, are not eligible to participate.
Registration is free of charge.
Every team participant must create a Sectors account and fully complete the Sectors App onboarding process at sectors.app before the team writes any project code. Onboarding is verified during the eligibility check. A team with any participant who has not completed onboarding by the registration deadline may have its submission deemed invalid.
By registering, participants are deemed to have read and agreed to these rules in full.
04
Teams & API credits
Participants may compete solo or in teams of 2–4 participants. A solo participant is treated as a team of one.
Each participant may only register on one team, including a solo team. A participant found on multiple teams is removed from all of them; the teams may continue with their remaining participants unless organizers find deliberate collusion, in which case every team involved is disqualified.
Each team may submit only one project.
Team rosters are locked once the team claims their team bonus API credits (available after all members complete onboarding).
Each team appoints one representative as its official contact, API credit holder, and prize recipient.
Prizes are awarded per team. How a prize is split is the team's internal matter.
API credits
Each registered team receives 1,000 Sectors API credits, which can be claimed via the team page in the hackathon portal once all team members have completed onboarding.

Registering additional accounts to obtain extra credits for the same project is a rules violation and grounds for disqualification.

Credits are exclusively for developing the team's competition project during the build period. They are non-transferable, cannot be exchanged for cash or other compensation, and expire when the event concludes unless organizers state otherwise.

05
Build period & work restrictions
The build period runs from 19 August 2026 through 8 October 2026, 23:59 WIB. Teams may start whenever they are ready during that window; there is no separate fixed build week.

Before the build period, ideas, research, sketches, designs, and planning are allowed. No project code may be written before 19 August 2026.
The project repository must be created during the build period. Judges may inspect commit history. Repositories created before 19 August 2026, or code migrated from previous projects, may result in disqualification. Multiple repositories are allowed if all were created within the build period.
Starting from a public template or boilerplate is allowed. What matters is that the first commit falls within the build period.
Boilerplate, templates, frameworks, libraries, and public open-source code may be used, provided they are not a finished product. Open-sourcing your own prior project before the event solely to reuse its code during the event is prohibited.
Projects must be exclusive to Sectors Hackathon. They may not contain work from previous projects and may not be submitted to other competitions or hackathons.
A team's repository and application freeze when that team submits, or at the 8 October deadline, whichever comes first. After freezing, no commits, pushes, edits, or changes of any kind are allowed, including bug fixes. A violation results in disqualification.
The only freeze exception is a leaked API key or other credential. Notify organizers on Slack (#support), revoke and rotate the credential first, then push a commit containing only its removal.
06
Project requirements
General requirements for every track
Projects must use Sectors MCP or the Sectors REST API as a core data source, not as a single decorative call. The product should lose its core functionality if Sectors data is removed. Any track may use MCP, the REST API, or both; the data interface does not determine the track.
Projects must be a working prototype or MVP with a core workflow that functions end to end. Rough edges are acceptable; a product that does not work will not pass judging.
Live deployment is not required. A public repository and judging video showing the core workflow end to end are sufficient to clear the eligibility check's product-works gate. Real-world usability carries the highest judging weight, so a product judges can see working convincingly will naturally score better.
Stack, tools, programming languages, licenses, and platforms are unrestricted. A public repository is sufficient; no specific open-source license is required.
Automated trade execution is prohibited in every track. Products may analyze, screen, score, alert, and support decisions, but may not place, execute, or automate buy or sell orders on real or brokerage-connected accounts.
Track definitions
Track 01
AI Agents & Assistants
Conversational or autonomous AI products for Indonesian financial markets, with an AI/LLM component at their core.

Track 02
Automation & Workflows
Products in which Sectors data works inside real, recurring routines.

Track 03
Market Intelligence
Products that turn Sectors data into insight for financial market decisions.

Track boundaries and support
A project's track is determined by what the product fundamentally does, not what it looks like. An agent with a dashboard belongs in AI Agents & Assistants. An autonomous pipeline that also produces scores may fit Automation & Workflows or Market Intelligence; the team chooses the track that best represents the project's core.

If a project does not meet its declared track's requirement, judges may move it to the track that fits rather than disqualify it. Track-based disqualification applies only when the project fits no track. Teams that are unsure should ask in the Slack #discussion channel during the build period.

07
Use of AI
The use of AI coding tools, including code generation, completion, agents, and similar tools, is fully permitted, without restriction and without a disclosure requirement. It's 2026, so use your best tools. What we judge is the result.

08
Submission requirements
Submissions must be made through the hackathon portal before the 8 October 2026, 23:59 WIB deadline. Submissions must include:

A public repository link. The repository must remain public for at least 90 days after winners are announced. Making it private before then forfeits prize eligibility, and a replacement winner may be selected. Remove all API keys before submitting.
A one-minute teaser video: a screen recording of the product working, published publicly on YouTube or social media.
A judging video of up to three minutes: a full walkthrough of the problem, intended audience, and core workflow. Public or unlisted YouTube and Vimeo videos, Google Drive links with link sharing enabled, and Loom links are accepted. Inaccessible videos will not be judged.
A one-sentence problem statement explaining who the product is for and what problem it solves.
Track selection and a list of team participant names.
A social media post publishing the project on Instagram, LinkedIn, Threads, or TikTok, tagging the official Sectors account and using the provided thumbnail template.
Submissions and videos may be in Bahasa Indonesia or English. Neither language is favored in scoring.

09
Judging
Judging is fully asynchronous from 9–16 October 2026 and is based on the submission materials. There are no live presentation sessions. Make sure the video and repository speak for themselves.

Eligibility check — pass or fail
The submission is complete, the product works, Sectors data is used as a core source, and every team participant's Sectors onboarding is verified.

Scoring
Submissions that pass the eligibility check are scored by the internal Sectors and Supertype judging team.

Criterion	Weight	What it rewards
Real-world usability	40%	How well does the project address a real-world problem? Can someone use it today and benefit from it?
Video demo & storytelling	30%	How exciting, engaging, and well produced is the video? Does it communicate the problem effectively for the intended audience?
Technical depth & execution	30%	Verified against the GitHub repository, how innovative is the use of Sectors API or MCP? Is the project real, functional, well engineered, and not faked for the demo?
Judges' decisions are final and binding.

10
Prizes
The total prize pool is valued at IDR 50,000,000, combining IDR 30,000,000 in cash with Sectors Insider subscriptions and Sectors API credits, awarded per placement: one first winner, one runner-up, and three finalists.

Placement	Cash	Sectors Insider subscription	Sectors API credits
First winner	IDR 15,000,000	6 months	20,000
Runner-up	IDR 9,000,000	4 months	15,000
3 Finalists (each)	IDR 2,000,000	2 months	10,000
Cash prizes are transferred to the team representative. Prize taxes follow applicable Indonesian laws and regulations.
Sectors Insider subscription and Sectors API credit prizes are issued to the team representative's Sectors account.
Sectors API credit prizes expire three months after issuance.
Winners under 18 receive prizes through a parent or guardian.
Organizers may require identity verification before prize delivery. Failure to verify within seven days may result in the prize being reassigned to a replacement winner.
Winners are announced 17 October 2026 on the competition website and on Instagram, via Sectors and Algoritma.
Terms and conditions
Organizers retain the right to make any amendments or adjustments to these prizes at their sole discretion.

11
Publicity & content rights
By submitting, participants grant Sectors and Supertype permission to display, publish, and promote the submission—including videos, screenshots, project names, and participant names—on their websites, social media, newsletters, and promotional materials without additional compensation.
Intellectual property in the project remains entirely with the participants. Sectors and Supertype claim no ownership rights over any code or product built during the event.
Participants are responsible for ensuring their project does not infringe the intellectual property rights of others.
12
Code of conduct
All participants must maintain a safe, welcoming, harassment-free environment on Slack, social media, and every event channel.
Projects containing discriminatory (SARA), harassing, or unlawful content will be automatically disqualified.
Projects must not provide financial advice. Products must position themselves as information and analysis tools, not investment recommendations. Include a disclaimer where relevant.
Violations may be reported in the #support channel on the official Slack.
13
Disqualification
Organizers may disqualify any participant or team at their sole discretion, including for violating these rules, cheating—including pre-event code and code-freeze violations—creating multiple accounts for additional API credits, duplicate submissions, code of conduct violations, or other unsporting behavior.

14
Support
Organizers may update these rules before 19 August 2026. Changes made after registration opens will be announced across all official channels and will not disadvantage participants who have already begun under the previous rules.

Questions may be sent to ask+hackathon@incoming.supertype.ai or posted in the Slack #discussion channel.


Sectors Hackathon
Build useful market products / 2026
Tracks
Rules
Find a team
Sponsorship
Register
Sectors Hackathon 2026 / Supertype
Questions and event support happen in Slack.
Sectors Hackathon 2026



# Update Proyek Garda — Versi Umum Multi-Sektor + News Aggregator

---

## 1. Deskripsi Project (diperbarui)

```
PROJECT NAME: Garda — AI Market Concierge

DESCRIPTION:
Garda is an AI agent that monitors the Indonesian and Singapore 
stock markets using Sectors API data, then enriches every 
market signal with real-time news aggregated from 20 top 
financial portals across Indonesia, Singapore, Malaysia, 
and Japan.

Every morning, Garda automatically scans Sectors data for 
price movements, sector performance, insider filings, and 
market anomalies — then cross-references the findings with 
relevant news from CNBC Indonesia, Bisnis.com, Nikkei, The 
Business Times, and other sources.

Users interact with Garda through a web portal: ask questions, 
request analysis, and receive concierge-grade market insight 
with both data AND context.

Data source: Sectors MCP / Sectors REST API (core requirement)
News sources: 20 portals per country — Indonesia, SG, MY, JP
```

---

## 2. Skills Needed (diperbarui)

```
Frontend Developer — React/Next.js. Web portal with market 
dashboard, news feed panel, and AI chat interface.

Backend Developer — Python/Node.js. Build pipelines: Sectors 
API → data processing → news scraper → AI synthesis → output.

AI/LLM Engineer — Multi-step reasoning, tool-use pipelines, 
conversation memory. LangChain, CrewAI, or custom orchestration.

Web Scraper / NLP Engineer — Extract and filter news from 20+ 
portals per country. Match headlines to relevant stocks/sectors. 
Handle multilingual content (Indonesian, English, Malay, Japanese).

Prompt Engineer — Craft Garda's system prompt for concierge-grade 
financial communication. Bahasa Indonesia + English fluency required.

Data Engineer — Design the news-to-market mapping: which keywords, 
tickers, and sector tags trigger relevance scoring per stock.

UI/UX Designer — Make multi-source data (Sectors charts + news 
headlines + AI chat) feel clean and non-intimidating for general 
users.

DevOps / Scheduler — Cron pipelines for daily pre-market briefing 
and real-time anomaly-triggered alerts. Log unattended runs for 
judging evidence.

QA — Verify data accuracy from Sectors API and news relevance 
matching accuracy.

Video Editor — For hackathon demo video storytelling.
```

---

## 3. Peta Data — Sectors × News Portal

Berikut bagaimana Garda menghubungkan **data pasar** dengan **berita**:

```
┌──────────────────────────────────────────────────────────┐
│                    GARDA DATA PIPELINE                    │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  LAYER 1: MARKET DATA (Sectors API / MCP)                │
│  ──────────────────────────────────────────              │
│  • Harga saham IDX & SGX                                │
│  • Perubahan harian / volume                             │
│  • P/E ratio, market cap, dividend yield                 │
│  • Kinerja sektor                                        │
│  • Insider filing (insider buy/sell)                     │
│  • Financial statements & segment revenue                │
│  • Broker flow, foreign flow                             │
│                                                           │
│  LAYER 2: NEWS AGGREGATION (20 portals × 4 negara)      │
│  ──────────────────────────────────────────              │
│  INDONESIA          SINGAPURA          MALAYSIA          │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐       │
│  │ CNBC ID  │      │ CNA      │      │ The Star │       │
│  │ Bisnis.com│     │ Straits T│      │ FMT      │       │
│  │ Kompas   │      │ Bus.Times│      │ Edge MY  │       │
│  │ Tempo    │      │ AsiaOne  │      │ MalayMail│       │
│  │ CNN ID   │      │ Today    │      │ Bernama  │       │
│  │ ...      │      │ ...      │      │ ...      │       │
│  │ (20 total│      │ (20 total│      │ (20 total│       │
│  └──────────┘      └──────────┘      └──────────┘       │
│                                                           │
│                    JEPANG                                │
│                  ┌──────────┐                            │
│                  │ Nikkei   │                            │
│                  │ NHK      │                            │
│                  │ NewsPicks│                            │
│                  │ Yahoo JP │                            │
│                  │ ...      │                            │
│                  │(20 total)│                            │
│                  └──────────┘                            │
│                                                           │
│  LAYER 3: GARDA AGENT (AI Core)                          │
│  ──────────────────────────────────────────              │
│  • Cross-referencing: news headline ↔ Sectors data       │
│    "BBCA turun 3%?" → cari berita tentang BCA di        │
│     CNBC ID, Bisnis.com, Kompas → rangkum + insight      │
│  • Multi-step reasoning                                   │
│  • Tool-use pipeline: Sectors API + News scraper          │
│  • Conversation memory                                    │
│  • Proactive alert trigger                                │
│                                                           │
│  LAYER 4: OUTPUT                                         │
│  ──────────────────────────────────────────              │
│  • Web portal dashboard (real-time)                      │
│  • Daily pre-market briefing (06.30 WIB)                 │
│  • Interactive chat (user ↔ Garda)                       │
│  • Push alert via WA Gateway (anomaly-triggered)          │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

---

## 4. Contoh Alur Kerja Garda

### Contoh 1: User bertanya tentang satu saham

```
USER: "Gimana kondisi BBCA hari ini?"

GARDA:
  Step 1 → Tool call: get_stock_price("BBCA")
           Result: Rp 9,850 | ▼ -2.1% | Volume: 45jt
  
  Step 2 → Tool call: get_stock_signals("BBCA")
           Result: Below 20-day MA, volume spike +180%
  
  Step 3 → News scraper: cari "BBCA" di 20 portal
           → CNBC ID: "BCA setelah rilis kuartal III"
           → Bisnis.com: "Penurunan saham bank BUMN"
           → Straits Times: "Indonesia banking stocks drop"
  
  Step 4 → LLM synthesis:
           "BBCA turun 2,1% hari ini dengan volume 
            tinggi. Berdasarkan berita dari CNBC Indonesia 
            dan Bisnis.com, penurunan ini berkaitan dengan 
            reaksi pasar terhadap rilis kuartal III. Dari 
            sisi teknikal, harga berada di bawah MA 20-hari 
            — sementara tren masih belum mengkonfirmasi 
            pembalikan arah."
```

### Contoh 2: Scheduler otomatis (bukti Track 2 compatible)

```
06:30 WIB → Pipeline jalan sendiri:
  → Narik data Sectors: perubahan harga, sector performance
  → Scraping berita: filter headline terkait emiten berubah > 2%
  → Garda merangkum → publish ke portal
  → Push briefing ke WA user
  
Log menunjukkan:
  [2026-01-15 06:30:01] ✅ Pipeline triggered (cron)
  [2026-01-15 06:30:15] ✅ Sectors API: 42 stocks fetched
  [2026-01-15 06:31:02] ✅ News: 87 headlines scraped
  [2026-01-15 06:31:45] ✅ Garda: synthesis complete
  [2026-01-15 06:31:50] ✅ Published to portal
  [2026-01-15 06:31:55] ✅ WA briefing sent
  [2026-01-15 06:31:55] ✅ Run complete — no human intervention
```

### Contoh 3: Alert berbasis data + news

```
[TRIGGER] BBCA -3.5% > threshold -3.0%
  → News scraper aktif: cari headline terkait
  → CNBC ID menemukan: "BI tetapkan suku bunga acuan naik"
  → Garda push alert via WA:
     "⚠️ PENTING: BBCA turun 3,5% hari ini. 
      Terkait berita dari CNBC Indonesia: BI menaikkan 
      suku bunga acuan. Sebagai pemilik bisnis di sektor 
      perbankan, mungkin ini perlu Anda perhatikan."
```

---

## 5. Kenapa Ini Unik & Belum Ada

| Komponen | Produk Lain | Garda |
|----------|-------------|-------|
| Data saham | ✅ Ada (Stockbit, IPOT) | ✅ Sectors API |
| News portal Indonesia | ❌ Terpisah dari data pasar | ✅ Direferensikan otomatis |
| News Singapore | ❌ Tidak tersedia | ✅ Straits Times, CNA, dll |
| News Malaysia | ❌ Tidak tersedia | ✅ FMT, The Edge, dll |
| News Jepang | ❌ Tidak tersedia | ✅ Nikkei, NHK, NewsPicks |
| AI agent yang merangkum data + berita | ❌ | ✅ Garda concierge |
| Otomatis harian tanpa human | ❌ Sebagian | ✅ Scheduler + WA push |
| Konteks UMKM | ❌ Umum untuk trader | ✅ Fokus pemilik bisnis |

---

## 6. Updated System Prompt (Ringkas)

```
IDENTITY:
You are Garda — a premium AI Market Concierge. You serve users 
who want to understand the Indonesian and Singapore stock markets 
with the depth of a financial analyst and the warmth of a 
personal concierge.

Your knowledge sources:
1. Sectors API — live market data (prices, fundamentals, sectors, 
   insider filings, flows)
2. News scraper — real-time headlines from 20 portals in Indonesia, 
   Singapore, Malaysia, and Japan

CORE PRINCIPLES:
- DATA-FIRST: Every number you cite comes from Sectors API. 
  Never fabricate prices or metrics.
- NEWS-CONTEXTUALIZED: Whenever a stock moves or a sector shifts, 
  you cross-reference with relevant news headlines before explaining.
- PROACTIVE: Don't wait for users to ask. When you notice significant 
  movements (price change >2%, volume spike, insider activity), 
  surface it with context.
- MULTI-MARKET: You cover IDX and SGX. If relevant news comes from 
  Malaysian or Japanese sources, use them as cross-border context.
- CONCIERGE TONE: Professional, warm, proactive. Like a private 
  banking advisor who knows their client's portfolio and reads 
  every morning paper.
- LANGUAGE: Respond in the user's language (Bahasa Indonesia or 
  English). Keep explanations clear for non-financial users.

BOUNDARY:
- Never provide buy/sell recommendations.
- Always state that data comes from Sectors API.
- News attribution: always mention the source portal.
```

---

## 7. Strategi untuk Hackathon

```
TRACK: AI Agents & Assistants (Track 01)

KEKUATAN COMPETITIVE:
1. ✅ Custom agent logic (bukan sekadar chatbot)
2. ✅ Multi-step reasoning (data → news → insight)
3. ✅ Tool-use pipeline (Sectors API + News scraper)
4. ✅ Memory (konteks user berkelanjutan)
5. ✅ News aggregation multi-negara (unik, belum ada)
6. ✅ WA Gateway sebagai bonus output channel
7. ✅ Scheduler sebagai bonus (jika juri pertimbangkan)

RISIKO & MITIGASI:
- Terlalu banyak portal untuk scrape → mulai dari 5 teratas 
  Indonesia + 3 teratas SG, tambah bertahap
- Multi-bahasa → fokus Indonesia + English dulu untuk v1
- Jangan sampai fokus ke berita mengalahkan Sectors API 
  sebagai core data source
```

---

Mau saya bantu langkah berikutnya: **setup pipeline news scraper** untuk portal-portal tertentu, **contoh kode Sectors API call**, atau **demo script lengkap untuk video hackathon**?