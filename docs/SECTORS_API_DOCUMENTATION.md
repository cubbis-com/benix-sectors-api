# Sectors Financial API v2 — Dokumentasi Lengkap & Panduan Integrasi

> **Dokumen Referensi Tunggal (Single Source of Truth) untuk Seluruh API Sectors**
> Berisi seluruh 74 endpoint Sectors Financial API v2, model kalkulasi kredit, arsitektur caching untuk efisiensi kuota, panduan MCP Server, dan middleware Python.

---

## 1. Ringkasan & Autentikasi

- **Base URL**: `https://api.sectors.app`
- **Sectors MCP Server URL**: `https://sectors-mcp.supertype.ai/mcp` (Streamable HTTP transport)
- **API Version**: `2.0.0`
- **Cakupan Pasar**: Indonesia (IDX), Singapore (SGX), Malaysia (KLSE), Sektor Tambang Indonesia (Mining Extension)

### Cara Autentikasi
1. **REST API (v2)**: Masukkan API key pada header `Authorization` secara langsung (raw key, **tanpa prefix `Bearer`**).
2. **Wajib User-Agent**: Selalu sertakan header `User-Agent` custom (misal `SectorsMiddleware/1.0` atau `Mozilla/5.0`) karena Cloudflare menolak default bot Python dengan error 403 Forbidden.
3. **Sectors MCP Server**: Menggunakan header `Authorization: Bearer <SECTORS_API_KEY>`.

```python
import os, requests

api_key = os.getenv("SECTORS_API_KEY", "your_sectors_api_key_here")
headers = {
    "Authorization": api_key,  # Raw key, TANPA prefix Bearer
    "User-Agent": "SectorsMiddleware/1.0"
}
res = requests.get("https://api.sectors.app/v2/subsectors/", headers=headers)
print(res.json()[:3])
```

---

## 2. Sistem Kuota Kredit & Aturan Penagihan (Billing & Credits)

Karena kuota API terbatas (misal 500 kredit per plan/hari), pemahaman aturan penagihan sangat krusial:

| Status HTTP | Memotong Kredit? | Rincian Biaya |
|---|---|---|
| **2xx (Success)** | **YA** | Sesuai tarif endpoint: mayoritas **1 kredit**, endpoint ranking/top tertentu **2 kredit**, dan Company Screener Natural Language `?q=` **3 kredit**. |
| **404 (Not Found)** | **YA** (1 kredit) | Request valid tapi simbol/ticker/slug tidak ditemukan (misal ticker salah `XYZW`). Dihitung 1 kredit karena query database tetap dieksekusi. |
| **400 (Bad Request)** | **TIDAK** (0 kredit) | Parameter salah format ditolak sebelum query jalan. *(Kecuali: Screener `?q=` jika gagal setelah dikirim ke model LLM, dikenakan 1 kredit)*. |
| **401 / 403 (Auth Error)** | **TIDAK** (0 kredit) | Key tidak valid / akses ditolak tidak memotong kredit. |
| **429 (Rate Limit / Quota)** | **TIDAK** (0 kredit) | Limit habis. |
| **5xx (Server Error)** | **TIDAK** (0 kredit) | Kegagalan di sisi server Sectors tidak memotong kredit. |

### Rekomendasi TTL Cache untuk Menghemat Kuota:
- **Helper Lists (Subsectors, Industries, Tags, Quarterly Dates)**: `TTL = 86400 detik (24 jam)`. Data kategori hampir tidak pernah berubah harian.
- **Company Report, Segments, Shareholders, Quarterly Financials**: `TTL = 21600 detik (6 jam)`. Laporan finansial kuartalan hanya rilis tiap 3 bulan.
- **Daily Close Universe & Historical Prices**: `TTL = 3600 detik (1 jam)`. Di luar jam bursa dapat di-cache hingga 12 jam.
- **Top Movers, Most Traded & Index Daily**: `TTL = 1800 detik (30 menit)` selama jam bursa.
- **Broker Activity & Foreign Flow**: `TTL = 1800 detik (30 menit)`.

---

## 3. Matriks Navigasi 74 Endpoints Sectors API v2

### Group 1: Indonesia (IDX)
| No | Tag / Kategori | Endpoint Summary | Method | Path | Biaya Kredit |
|---|---|---|---|---|---|
| 1 | Company Screener | Companies Screener | `GET` | `/v2/companies/` | Costs 1 credit for structured queries. Using the natural-language `?q=` parameter costs 3 credits. |
| 2 | Company Screener | Free Float Market Analysis | `GET` | `/v2/free-float/` | Costs 1 credit per 100 companies returned, rounded up. |
| 3 | Helper Lists | Companies with Revenue Segments | `GET` | `/v2/companies/list_companies_with_segments/` | Costs 1 credit. |
| 4 | Helper Lists | Latest Quarterly Financial Dates (Universe) | `GET` | `/v2/companies/quarterly-financial-dates/` | Costs 1 credit per page. The full universe is ~32 pages at the maximum `limit` of 30 (~32 credits per full sweep). Use `since` to poll incrementally for far fewer credits. |
| 5 | Helper Lists | Quarterly Financial Dates | `GET` | `/v2/company/get_quarterly_financial_dates/{symbol}/` | Costs 1 credit. |
| 6 | Helper Lists | Industries | `GET` | `/v2/industries/` | Costs 1 credit. |
| 7 | Helper Lists | Subindustries | `GET` | `/v2/subindustries/` | Costs 1 credit. |
| 8 | Helper Lists | Subsectors | `GET` | `/v2/subsectors/` | Costs 1 credit. |
| 9 | Helper Lists | News Tags | `GET` | `/v2/tags/` | Costs 1 credit. |
| 10 | Detailed Reports | Corporate Actions | `GET` | `/v2/company/corporate-actions/{symbol}/` | Costs 1 credit. |
| 11 | Detailed Reports | Company Revenue Segments | `GET` | `/v2/company/get-segments/{symbol}/` | Costs 1 credit. |
| 12 | Detailed Reports | Company Report | `GET` | `/v2/company/report/` | Costs 1 credit per requested section. Default behavior (all 8 sections) consumes 8 credits. |
| 13 | Detailed Reports | Company Report | `GET` | `/v2/company/report/{symbol}/` | Costs 1 credit per requested section. Default behavior (all 8 sections) consumes 8 credits. |
| 14 | Detailed Reports | Shareholders Composition | `GET` | `/v2/company/shareholders-composition/{symbol}/` | Costs 1 credit. |
| 15 | Detailed Reports | Company Quarterly Financials | `GET` | `/v2/financials/quarterly/{symbol}/` | Costs 1 credit per quarter returned. |
| 16 | Detailed Reports | Subsector Report | `GET` | `/v2/subsector/report/` | Costs 1 credit per requested section. Default behavior (all 6 sections) consumes 6 credits. |
| 17 | Detailed Reports | Subsector Report | `GET` | `/v2/subsector/report/{sub_sector}/` | Costs 1 credit per requested section. Default behavior (all 6 sections) consumes 6 credits. |
| 18 | Transaction Data | Daily Full-Universe Close | `GET` | `/v2/close/` | Costs 1 credit per page. The full ~950-ticker universe is ~32 pages at the maximum `limit` of 30 (~32 credits per full pull). |
| 19 | Transaction Data | Daily Transaction Data | `GET` | `/v2/daily/{symbol}/` | Costs 1 credit. |
| 20 | Transaction Data | IDX Market Summary | `GET` | `/v2/idx-total/` | Costs 1 credit. |
| 21 | Transaction Data | Daily Full-Universe Index Close | `GET` | `/v2/index-daily/` | Costs 1 credit. |
| 22 | Transaction Data | Index Daily Transaction Data | `GET` | `/v2/index-daily/{index_code}/` | Costs 1 credit. |
| 23 | Rankings | Top Company Movers | `GET` | `/v2/companies/top-changes/` | Costs 1 credit per requested classification × period combination. Default behavior (2 classifications × 5 periods) consumes 10 credits. |
| 24 | Rankings | Most Traded Stocks | `GET` | `/v2/most-traded/` | Costs 2 credits. |
| 25 | IPO & Performance | Company IPO & Listing Performance | `GET` | `/v2/listing-performance/{symbol}/` | Costs 1 credit. |
| 26 | News & Filings | Corporate Actions Calendar | `GET` | `/v2/corporate-actions/` | Costs 1 credit per requested type. Default (all 7 types) consumes 7 credits. |
| 27 | News & Filings | Company Filings | `GET` | `/v2/filings/` | Costs 1 credit. |
| 28 | News & Filings | News Articles | `GET` | `/v2/news/` | Costs 1 credit. |
| 29 | News & Filings | Stock Suspensions | `GET` | `/v2/suspensions/` | Costs 1 credit. |
| 30 | Brokers | Broker Activity By Code | `GET` | `/v2/broker-activity/{broker_code}/` | Costs 1 credit. |
| 31 | Brokers | Top Accumulations and Distributions Per Broker | `GET` | `/v2/broker-activity/{broker_code}/top/` | Costs 2 credits. |
| 32 | Brokers | Broker Activity Per Symbol | `GET` | `/v2/broker-summary/{symbol}/` | Costs 1 credit. |
| 33 | Brokers | Top Buyers and Sellers Per Symbol | `GET` | `/v2/broker-summary/{symbol}/top/` | Costs 2 credits. |
| 34 | Brokers | Broker Registry | `GET` | `/v2/brokers/` | Costs 1 credit. |
| 35 | Brokers | Top Brokers Daily Ranking | `GET` | `/v2/brokers/top/` | Costs 2 credits. |
| 36 | Brokers | Daily Full-Universe Foreign Flow | `GET` | `/v2/foreign-flow/` | Costs 1 credit per page. The full universe (typically 550-700 tickers with foreign activity on the day) is about 20-25 pages at the maximum `limit` of 30. |
| 37 | Brokers | Daily Net Foreign Inflow | `GET` | `/v2/foreign-flow/{symbol}/` | Costs 1 credit. |

### Group 2: Singapore (SGX)
| No | Tag / Kategori | Endpoint Summary | Method | Path | Biaya Kredit |
|---|---|---|---|---|---|
| 1 | SGX - Company Screener | SGX Companies Screener | `GET` | `/v2/sgx/companies/` | Costs 1 credit for structured queries. Using the natural-language `?q=` parameter costs 3 credits. |
| 2 | SGX - Helper Lists | List all SGX sectors | `GET` | `/v2/sgx/sectors/` | Costs 1 credit. |
| 3 | SGX - Helper Lists | SGX Subsectors | `GET` | `/v2/sgx/subsectors/` | Costs 1 credit. |
| 4 | SGX - Helper Lists | SGX News Tags | `GET` | `/v2/sgx/tags/` | Costs 1 credit. |
| 5 | SGX - Detailed Reports | Full company report for an SGX-listed symbol | `GET` | `/v2/sgx/company/report/` | Costs 1 credit per requested section. Default behavior (all 4 sections) consumes 4 credits. |
| 6 | SGX - Detailed Reports | Full company report for an SGX-listed symbol | `GET` | `/v2/sgx/company/report/{symbol}/` | Costs 1 credit per requested section. Default behavior (all 4 sections) consumes 4 credits. |
| 7 | SGX - Transaction Data | SGX Share Buybacks | `GET` | `/v2/sgx/buybacks/` | Costs 1 credit. |
| 8 | SGX - Transaction Data | SGX Daily Full-Universe Close | `GET` | `/v2/sgx/close/` | Costs 1 credit per page. The full universe (roughly 560-600 tickers) is about 20 pages at the maximum `limit` of 30 (~20 credits per full pull). |
| 9 | SGX - Transaction Data | SGX Daily Price Data | `GET` | `/v2/sgx/daily/{symbol}/` | Costs 1 credit. |
| 10 | SGX - Transaction Data | SGX Short Sell | `GET` | `/v2/sgx/short-sell/` | Costs 1 credit. |
| 11 | SGX - Rankings | Top SGX companies by classification | `GET` | `/v2/sgx/companies/top/` | Costs 1 credit per requested classification. Default behavior (all 5 classifications) consumes 5 credits. |
| 12 | SGX - News & Filings | SGX Insider Filings | `GET` | `/v2/sgx/filings/` | Costs 1 credit. |
| 13 | SGX - News & Filings | SGX News | `GET` | `/v2/sgx/news/` | Costs 1 credit. |

### Group 3: Malaysia (KLSE)
| No | Tag / Kategori | Endpoint Summary | Method | Path | Biaya Kredit |
|---|---|---|---|---|---|
| 1 | KLSE | List KLSE companies filtered by sector | `GET` | `/v2/klse/companies/` | Costs 1 credit. |
| 2 | KLSE | Top KLSE companies by classification | `GET` | `/v2/klse/companies/top/` | Costs 1 credit per requested classification. Default behavior (all 5 classifications) consumes 5 credits. |
| 3 | KLSE | Full company report for a KLSE-listed symbol | `GET` | `/v2/klse/company/report/` | Costs 1 credit per requested section. Default behavior (all 4 sections) consumes 4 credits. |
| 4 | KLSE | Full company report for a KLSE-listed symbol | `GET` | `/v2/klse/company/report/{symbol}/` | Costs 1 credit per requested section. Default behavior (all 4 sections) consumes 4 credits. |
| 5 | KLSE | List all KLSE sectors | `GET` | `/v2/klse/sectors/` | Costs 1 credit. |

### Group 4: Mining (Extension)
| No | Tag / Kategori | Endpoint Summary | Method | Path | Biaya Kredit |
|---|---|---|---|---|---|
| 1 | Companies | List Mining Companies | `GET` | `/v2/mining/companies/` | Costs 1 credit. |
| 2 | Companies | Mining Company Financials | `GET` | `/v2/mining/companies/financials/{slug}/` | Costs 1 credit. |
| 3 | Companies | Mining Company Ownership | `GET` | `/v2/mining/companies/ownership/{slug}/` | Costs 1 credit. |
| 4 | Companies | Mining Company Performance | `GET` | `/v2/mining/companies/performance/{slug}/` | Costs 1 credit. |
| 5 | Companies | Mining Company Detail | `GET` | `/v2/mining/companies/{slug}/` | Costs 1 credit. |
| 6 | Commodities & Trade | List Commodities | `GET` | `/v2/mining/commodities/` | Costs 1 credit. |
| 7 | Commodities & Trade | Commodity Price History | `GET` | `/v2/mining/commodities/{commodity_name}/price/` | Costs 1 credit. |
| 8 | Commodities & Trade | Top Export Destinations | `GET` | `/v2/mining/exports/` | Costs 1 credit. |
| 9 | Commodities & Trade | Global Commodity Data | `GET` | `/v2/mining/global-commodity/` | Costs 1 credit. |
| 10 | Commodities & Trade | Company Sales Destinations | `GET` | `/v2/mining/sales-destination/{slug}/` | Costs 1 credit. |
| 11 | Production & Sites | Resources & Reserves Index | `GET` | `/v2/mining/resources-reserves/` | Costs 1 credit. |
| 12 | Production & Sites | Resources & Reserves Detail | `GET` | `/v2/mining/resources-reserves/{province}/` | Costs 1 credit. |
| 13 | Production & Sites | Mining Sites | `GET` | `/v2/mining/sites/` | Costs 1 credit. |
| 14 | Production & Sites | Mining Site Detail | `GET` | `/v2/mining/sites/{slug}/` | Costs 1 credit. |
| 15 | Production & Sites | Total Commodity Production | `GET` | `/v2/mining/total-production/` | Costs 1 credit. |
| 16 | Contracts & Licenses | Mining Contracts | `GET` | `/v2/mining/contracts/` | Costs 1 credit. |
| 17 | Contracts & Licenses | Mining License Auctions | `GET` | `/v2/mining/license-auctions/` | Costs 1 credit. |
| 18 | Contracts & Licenses | Mining License Auction Detail | `GET` | `/v2/mining/license-auctions/{wiup_code}/` | Costs 1 credit. |
| 19 | Contracts & Licenses | Mining Licenses | `GET` | `/v2/mining/licenses/` | Costs 1 credit. |

---

## 4. Panduan Lengkap Detail Seluruh 74 Endpoints

# Indonesia (IDX)

## Sub-Kategori: Company Screener

### 1. Companies Screener
- **Method & Path**: `GET https://api.sectors.app/v2/companies/`
- **Kategori**: `Indonesia (IDX)` / `Company Screener`
- **Biaya Kredit**: `Costs 1 API credit for structured queries. Using the natural-language `?q=` parameter costs 3 API credits.`

**Penjelasan**:
High-performance API for filtering and sorting IDX-listed companies. Supports both structured SQL-like queries (`where`, `order_by`) and natural language queries (`q`). Returns a paginated list of companies.

**Query modes** (mutually exclusive — `q` overrides all others):
- `q`: Natural language, e.g. `top 10 tech companies by revenue in 2023`
- `where` + `order_by`: SQL-like structured query

> 💡 **Note**: For the most precise natural language results, filter by sector/industry slugs. Retrieve the complete slug list from the [Subsectors](https://docs.sectors.app/api-references/v2/indonesia/helper-list/subsectors), [Industries](https://docs.sectors.app/api-references/v2/indonesia/helper-list/industries), or [Subindustries](https://docs.sectors.app/api-references/v2/indonesia/helper-list/subindustries) endpoints.


To account for reporting lags, 'latest year' queries made between January and April default to the previous audited year (e.g. a query in early 2026 uses 2024 data).



**Operators:** `=`, `!=`, `>`, `>=`, `<`, `<=`, `like`, `in`

**Logic:** combine conditions with `and` and `or`

**String values:** use single or double quotes — `sector = 'Technology'`

**Lists (for `in`):** `tags in ['blue-chip', 'dividend']`



Access historical or forecast data using bracket notation: `field[YYYY]`

Examples: `revenue[2023] > 100000000000` or `forecast_eps_growth[2025] > 0.15`



Perform calculations within your query on both sides of a condition.

Examples: `revenue[2024] / total_assets[2024] > 0.5` or `revenue[2024] > revenue[2023] * 1.2`






**How to Use:** Query these fields directly using standard operators (`=`, `!=`, `>`, `<`, `LIKE`, `IN`). String comparisons are case-insensitive.


- `where=market_cap > 500000000000000`
- `where=company_name like '%energi%'`
- `where=sector = 'Financials' and listing_date > '2005-01-01'`


- **symbol**: IDX ticker symbol (e.g. BBCA, TLKM)
- **company_name**: Full registered company name
- **listing_board**: IDX board: Main, Development, or Acceleration
- **industry**: IDX industry classification
- **sub_industry**: IDX sub-industry classification
- **sector**: IDX sector classification (broader than industry)
- **sub_sector**: IDX sub-sector classification
- **market_cap**: Market capitalisation in IDR
- **market_cap_rank**: Rank by market cap among all IDX companies (1 = largest)
- **employee_num**: Total number of employees
- **employee_num_rank**: Rank by employee count among all IDX companies
- **listing_date**: Date the company was first listed on IDX
- **last_ex_dividend_date**: Most recent ex-dividend date
- **last_close_price**: Latest closing price in IDR
- **daily_close_change**: Day-over-day closing price change as a decimal
- **forward_pe**: Forward price-to-earnings ratio based on next year earnings estimate
- **intrinsic_value**: Estimated intrinsic value per share in IDR
- **esg_score**: ESG (Environmental, Social, Governance) composite score
- **yield_ttm**: Dividend yield over the trailing twelve months
- **dividend_ttm**: Total dividends paid per share over the trailing twelve months in IDR
- **payout_ratio**: Proportion of earnings paid out as dividends
- **cash_payout_ratio**: Proportion of free cash flow paid out as dividends
- **yoy_quarter_earnings_growth**: Year-over-year earnings growth based on the most recent quarter
- **yoy_quarter_revenue_growth**: Year-over-year revenue growth based on the most recent quarter



**How to Use:** Query using the `in` operator to check if any of the provided values exist in the array.


- `where=indices in ['LQ45', 'IDX30']`
- `where=tags in ['52-w-high', 'public-float-under-25']`


- **tags**: Analyst sentiment tags (e.g. 'bullish'). Filter with `in` operator.
- **indices**: IDX indices this stock belongs to (e.g. LQ45, IDX30). Filter with `in` operator.
- **affiliates**: Related company tickers (affiliates/group entities)



**How to Use:** Query as if they were direct fields — the parser automatically extracts the value from the underlying JSON.


- `where=pe_ttm < 15 and roe_ttm > 0.1`
- `where=last_close_price < all_time_high_price`
- `where=ytd_low_date > '2025-03-01'`


- **pe_ttm**: Price-to-earnings ratio (trailing twelve months)
- **pb_mrq**: Price-to-book ratio (most recent quarter)
- **ps_ttm**: Price-to-sales ratio (trailing twelve months)
- **dar_mrq**: Debt-to-assets ratio (most recent quarter)
- **der_mrq**: Debt-to-equity ratio (most recent quarter)
- **roa_ttm**: Return on assets (trailing twelve months)
- **roe_ttm**: Return on equity (trailing twelve months)
- **total_assets_mrq**: Total assets in IDR (most recent quarter)
- **total_equity_mrq**: Total shareholders equity in IDR (most recent quarter)
- **total_revenue_mrq**: Total revenue in IDR (most recent quarter)
- **earnings_mrq**: Net profit/loss in IDR (most recent quarter)
- **total_liabilities_mrq**: Total liabilities in IDR (most recent quarter)
- **yearly_mcap_change**: Year-over-year market cap change as a decimal
- **dividend_yield_avg_period**: Number of years used to compute average dividend yield
- **dividend_yield_avg**: Average annual dividend yield over the period
- **ytd_low_price**: Year-to-date lowest closing price in IDR
- **ytd_low_date**: Date of the year-to-date lowest closing price
- **ytd_high_price**: Year-to-date highest closing price in IDR
- **ytd_high_date**: Date of the year-to-date highest closing price
- **52_w_low_price**: 52-week lowest closing price in IDR
- **52_w_low_date**: Date of the 52-week lowest closing price
- **52_w_high_price**: 52-week highest closing price in IDR
- **52_w_high_date**: Date of the 52-week highest closing price
- **90_d_low_price**: 90-day lowest closing price in IDR
- **90_d_low_date**: Date of the 90-day lowest closing price
- **90_d_high_price**: 90-day highest closing price in IDR
- **90_d_high_date**: Date of the 90-day highest closing price
- **all_time_low_price**: All-time lowest closing price in IDR
- **all_time_low_date**: Date of the all-time lowest closing price
- **all_time_high_price**: All-time highest closing price in IDR
- **all_time_high_date**: Date of the all-time highest closing price



**How to Use:** Must use bracket notation `field[YYYY]` to access data for a specific year. Supports all numeric operators, field-to-field comparisons, and arithmetic expressions.


- `where=revenue[2023] > earnings[2023] * 5`
- `where=roe[2023] > 0.15 and roe[2022] > 0.15`
- `where=pe[2024] < pe_peer_avg[2024]`


- **eps**: Earnings per share for the year. Use: `eps[2024]`.
- **eps_growth**: Year-over-year EPS growth rate. Use: `eps_growth[2024]`.
- **total_dividend**: Total dividends paid per share for the year. Use: `total_dividend[2024]`.
- **total_yield**: Total dividend yield for the year. Use: `total_yield[2024]`.
- **earnings**: Annual net profit/loss in IDR. Use: `earnings[2024]`.
- **allowance_for_loans**: Allowance for loan losses in IDR. Use: `allowance_for_loans[2024]`. (banking)
- **capital_expenditure**: Capital expenditure in IDR. Use: `capital_expenditure[2024]`.
- **cash_and_equivalents**: Cash and cash equivalents in IDR. Use: `cash_and_equivalents[2024]`.
- **cash_inflow**: Total cash inflow in IDR. Use: `cash_inflow[2024]`.
- **cash_only**: Cash excluding equivalents in IDR. Use: `cash_only[2024]`.
- **cash_outflow**: Total cash outflow in IDR. Use: `cash_outflow[2024]`.
- **core_capital_tier1**: Tier 1 core capital in IDR. Use: `core_capital_tier1[2024]`. (banking)
- **cost_of_revenue**: Cost of goods sold / cost of revenue in IDR. Use: `cost_of_revenue[2024]`.
- **credit_rwa**: Credit risk-weighted assets in IDR. Use: `credit_rwa[2024]`. (banking)
- **current_account**: Current account deposits in IDR. Use: `current_account[2024]`. (banking)
- **current_assets**: Total current assets in IDR. Use: `current_assets[2024]`.
- **current_liabilities**: Total current liabilities in IDR. Use: `current_liabilities[2024]`.
- **earnings_before_tax**: Earnings before income tax in IDR. Use: `earnings_before_tax[2024]`.
- **ebit**: Earnings before interest and tax in IDR. Use: `ebit[2024]`.
- **ebitda**: Earnings before interest, tax, depreciation and amortisation in IDR. Use: `ebitda[2024]`.
- **end_cash_position**: Ending cash position from the cash flow statement in IDR. Use: `end_cash_position[2024]`.
- **financing_cash_flow**: Net cash from financing activities in IDR. Use: `financing_cash_flow[2024]`.
- **fixed_assets**: Net property, plant and equipment in IDR. Use: `fixed_assets[2024]`.
- **free_cash_flow**: Operating cash flow minus capex in IDR. Use: `free_cash_flow[2024]`.
- **gross_loan**: Gross loan portfolio before allowances in IDR. Use: `gross_loan[2024]`. (banking)
- **gross_profit**: Revenue minus cost of revenue in IDR. Use: `gross_profit[2024]`.
- **high_quality_liquid_asset**: High-quality liquid assets (HQLA) held in IDR. Use: `high_quality_liquid_asset[2024]`. (banking)
- **interest_expense**: Total interest expense in IDR. Use: `interest_expense[2024]`.
- **interest_expense_non_operating**: Non-operating interest expense in IDR. Use: `interest_expense_non_operating[2024]`.
- **interest_income**: Total interest income in IDR. Use: `interest_income[2024]`.
- **inventories**: Inventories on the balance sheet in IDR. Use: `inventories[2024]`.
- **investing_cash_flow**: Net cash from investing activities in IDR. Use: `investing_cash_flow[2024]`.
- **market_rwa**: Market risk-weighted assets in IDR. Use: `market_rwa[2024]`. (banking)
- **net_cash_flow**: Net change in cash for the period in IDR. Use: `net_cash_flow[2024]`.
- **net_interest_income**: Interest income minus interest expense in IDR. Use: `net_interest_income[2024]`. (banking)
- **net_loan**: Net loans after allowances in IDR. Use: `net_loan[2024]`. (banking)
- **net_premium_income**: Net insurance premium income in IDR. Use: `net_premium_income[2024]`. (insurance)
- **non_current_liabilities**: Long-term liabilities in IDR. Use: `non_current_liabilities[2024]`.
- **non_interest_bearing_liabilities**: Liabilities that do not accrue interest in IDR. Use: `non_interest_bearing_liabilities[2024]`. (banking)
- **non_interest_income**: Fee and commission income outside of interest in IDR. Use: `non_interest_income[2024]`. (banking)
- **non_loan_assets**: Total assets excluding loans in IDR. Use: `non_loan_assets[2024]`. (banking)
- **non_loan_earning_assets**: Interest-earning assets excluding loans in IDR. Use: `non_loan_earning_assets[2024]`. (banking)
- **non_loan_non_earning_assets**: Non-earning assets excluding loans in IDR. Use: `non_loan_non_earning_assets[2024]`. (banking)
- **non_operating_income_or_loss**: Income or losses outside core operations in IDR. Use: `non_operating_income_or_loss[2024]`.
- **operating_cash_flow**: Net cash generated from core operations in IDR. Use: `operating_cash_flow[2024]`.
- **operating_expense**: Total operating expenses in IDR. Use: `operating_expense[2024]`.
- **operating_pnl**: Operating profit/loss (revenue minus operating expenses) in IDR. Use: `operating_pnl[2024]`.
- **operational_rwa**: Operational risk-weighted assets in IDR. Use: `operational_rwa[2024]`. (banking)
- **other_interest_bearing_liabilities**: Other interest-bearing liabilities excluding deposits in IDR. Use: `other_interest_bearing_liabilities[2024]`. (banking)
- **outstanding_shares**: Total shares outstanding. Use: `outstanding_shares[2024]`.
- **prepaid_assets**: Prepaid expenses and other current assets in IDR. Use: `prepaid_assets[2024]`.
- **premium_expense**: Insurance premium expenses in IDR. Use: `premium_expense[2024]`. (insurance)
- **premium_income**: Gross insurance premium income in IDR. Use: `premium_income[2024]`. (insurance)
- **provision**: Provision for loan losses or liabilities in IDR. Use: `provision[2024]`.
- **realized_capital_goods_investment**: Realised investment in capital goods in IDR. Use: `realized_capital_goods_investment[2024]`.
- **retained_earnings**: Cumulative retained earnings on balance sheet in IDR. Use: `retained_earnings[2024]`.
- **revenue**: Annual total revenue in IDR. Use: `revenue[2024]`.
- **savings_account**: Savings account deposits in IDR. Use: `savings_account[2024]`. (banking)
- **supplementary_capital_tier2**: Tier 2 supplementary capital in IDR. Use: `supplementary_capital_tier2[2024]`. (banking)
- **tax**: Income tax expense in IDR. Use: `tax[2024]`.
- **time_deposit**: Time deposit liabilities in IDR. Use: `time_deposit[2024]`. (banking)
- **total_assets**: Total assets on the balance sheet in IDR. Use: `total_assets[2024]`.
- **total_capital**: Total regulatory capital in IDR. Use: `total_capital[2024]`. (banking)
- **total_cash_and_due_from_banks**: Cash and amounts due from other banks in IDR. Use: `total_cash_and_due_from_banks[2024]`. (banking)
- **total_debt**: Total interest-bearing debt in IDR. Use: `total_debt[2024]`.
- **total_deposit**: Total customer deposits in IDR. Use: `total_deposit[2024]`. (banking)
- **total_equity**: Total shareholders equity in IDR. Use: `total_equity[2024]`.
- **total_liabilities**: Total liabilities on the balance sheet in IDR. Use: `total_liabilities[2024]`.
- **total_risk_weighted_asset**: Total risk-weighted assets in IDR. Use: `total_risk_weighted_asset[2024]`. (banking)
- **special_mention_loan**: Special mention (watch-list) loans in IDR. Use: `special_mention_loan[2024]`. (banking)
- **non_performing_loan**: Non-performing loans (NPL) in IDR. Use: `non_performing_loan[2024]`. (banking)
- **restructured_loan_current**: Restructured loans currently performing in IDR. Use: `restructured_loan_current[2024]`. (banking)
- **forecast_eps_growth**: Analyst consensus EPS growth forecast. Use: `forecast_eps_growth[2025]`.
- **forecast_revenue_growth**: Analyst consensus revenue growth forecast. Use: `forecast_revenue_growth[2025]`.
- **forecast_eps_estimate**: Analyst consensus EPS estimate in IDR. Use: `forecast_eps_estimate[2025]`.
- **forecast_revenue_estimate**: Analyst consensus revenue estimate in IDR. Use: `forecast_revenue_estimate[2025]`.
- **pe**: Price-to-earnings ratio for the year. Use: `pe[2024]`.
- **pb**: Price-to-book ratio for the year. Use: `pb[2024]`.
- **ps**: Price-to-sales ratio for the year. Use: `ps[2024]`.
- **pcf**: Price-to-cash-flow ratio for the year. Use: `pcf[2024]`.
- **peg**: Price/earnings-to-growth ratio for the year. Use: `peg[2024]`.
- **enterprise_to_ebitda**: Enterprise value to EBITDA for the year. Use: `enterprise_to_ebitda[2024]`.
- **enterprise_to_revenue**: Enterprise value to revenue for the year. Use: `enterprise_to_revenue[2024]`.
- **pb_peer_avg**: Peer average price-to-book ratio for the year. Use: `pb_peer_avg[2024]`.
- **pe_peer_avg**: Peer average price-to-earnings ratio for the year. Use: `pe_peer_avg[2024]`.
- **ps_peer_avg**: Peer average price-to-sales ratio for the year. Use: `ps_peer_avg[2024]`.
- **debt_to_asset_ratio**: Total debt divided by total assets. Use: `debt_to_asset_ratio[2024]`.
- **debt_to_equity_ratio**: Total debt divided by shareholders equity. Use: `debt_to_equity_ratio[2024]`.
- **cash_flow_to_debt_ratio**: Operating cash flow divided by total debt. Use: `cash_flow_to_debt_ratio[2024]`.
- **interest_coverage_ratio**: EBIT divided by interest expense. Use: `interest_coverage_ratio[2024]`.
- **current_ratio**: Current assets divided by current liabilities. Use: `current_ratio[2024]`.
- **operating_cash_flow_margin**: Operating cash flow as a percentage of revenue. Use: `operating_cash_flow_margin[2024]`.
- **fixed_asset_turnover**: Revenue divided by net fixed assets. Use: `fixed_asset_turnover[2024]`.
- **total_asset_turnover**: Revenue divided by total assets. Use: `total_asset_turnover[2024]`.
- **roa**: Return on assets for the year. Use: `roa[2024]`.
- **roe**: Return on equity for the year. Use: `roe[2024]`.
- **net_profit_margin**: Net profit as a percentage of revenue. Use: `net_profit_margin[2024]`.
- **gross_profit_margin**: Gross profit as a percentage of revenue. Use: `gross_profit_margin[2024]`.
- **operating_profit_margin**: Operating profit as a percentage of revenue. Use: `operating_profit_margin[2024]`.
- **capital_adequacy_ratio**: Regulatory capital as a percentage of risk-weighted assets. Use: `capital_adequacy_ratio[2024]`. (banking)
- **casa_ratio**: Current and savings account deposits as a share of total deposits. Use: `casa_ratio[2024]`. (banking)
- **leverage_ratio**: Tier 1 capital divided by total exposure. Use: `leverage_ratio[2024]`. (banking)
- **loan_to_deposit_ratio**: Net loans divided by total deposits. Use: `loan_to_deposit_ratio[2024]`. (banking)
- **liquidity_coverage_ratio**: HQLA divided by net cash outflows over 30 days. Use: `liquidity_coverage_ratio[2024]`. (banking)
- **efficiency_ratio**: Operating expenses divided by net revenue. Use: `efficiency_ratio[2024]`.
- **net_interest_margin**: Net interest income as a percentage of earning assets. Use: `net_interest_margin[2024]`. (banking)
- **cost_to_income_ratio**: Operating costs divided by operating income. Use: `cost_to_income_ratio[2024]`.



**How to Use:** Must use bracket notation `field[Qi-YYYY]` to access data for a specific quarter.


- `where=revenue_q[Q1-2024] > 1000000000`
- `where=earnings_q[Q4-2023] > earnings_q[Q3-2023]`


- **revenue_q**: Quarterly revenue in IDR. Use: `revenue_q[Q1-2024]`.
- **earnings_q**: Quarterly net profit/loss in IDR. Use: `earnings_q[Q1-2024]`.
- **net_loan_q**: Quarterly net loans in IDR. Use: `net_loan_q[Q1-2024]`. (banking)
- **gross_profit_q**: Quarterly gross profit in IDR. Use: `gross_profit_q[Q1-2024]`.
- **time_deposit_q**: Quarterly time deposits in IDR. Use: `time_deposit_q[Q1-2024]`. (banking)
- **operating_pnl_q**: Quarterly operating profit/loss in IDR. Use: `operating_pnl_q[Q1-2024]`.
- **total_deposit_q**: Quarterly total deposits in IDR. Use: `total_deposit_q[Q1-2024]`. (banking)
- **ebit_q**: Quarterly EBIT in IDR. Use: `ebit_q[Q1-2024]`.
- **ebitda_q**: Quarterly EBITDA in IDR. Use: `ebitda_q[Q1-2024]`.
- **earnings_before_tax_q**: Quarterly earnings before tax in IDR. Use: `earnings_before_tax_q[Q1-2024]`.
- **tax_q**: Quarterly income tax expense in IDR. Use: `tax_q[Q1-2024]`.
- **cost_of_revenue_q**: Quarterly cost of revenue in IDR. Use: `cost_of_revenue_q[Q1-2024]`.
- **current_account_q**: Quarterly current account deposits in IDR. Use: `current_account_q[Q1-2024]`. (banking)
- **interest_income_q**: Quarterly interest income in IDR. Use: `interest_income_q[Q1-2024]`. (banking)
- **premium_expense_q**: Quarterly premium expenses in IDR. Use: `premium_expense_q[Q1-2024]`. (insurance)
- **savings_account_q**: Quarterly savings account deposits in IDR. Use: `savings_account_q[Q1-2024]`. (banking)
- **interest_expense_q**: Quarterly interest expense in IDR. Use: `interest_expense_q[Q1-2024]`.
- **operating_expense_q**: Quarterly operating expenses in IDR. Use: `operating_expense_q[Q1-2024]`.
- **non_operating_income_or_loss_q**: Quarterly non-operating income/loss in IDR. Use: `non_operating_income_or_loss_q[Q1-2024]`.
- **interest_expense_non_operating_q**: Quarterly non-operating interest expense in IDR. Use: `interest_expense_non_operating_q[Q1-2024]`.
- **non_interest_bearing_liabilities_q**: Quarterly non-interest-bearing liabilities in IDR. Use: `non_interest_bearing_liabilities_q[Q1-2024]`. (banking)
- **realized_capital_goods_investment_q**: Quarterly realised capital goods investment in IDR. Use: `realized_capital_goods_investment_q[Q1-2024]`.
- **other_interest_bearing_liabilities_q**: Quarterly other interest-bearing liabilities in IDR. Use: `other_interest_bearing_liabilities_q[Q1-2024]`. (banking)
- **total_assets_q**: Quarterly total assets in IDR. Use: `total_assets_q[Q1-2024]`.
- **current_assets_q**: Quarterly current assets in IDR. Use: `current_assets_q[Q1-2024]`.
- **total_liabilities_q**: Quarterly total liabilities in IDR. Use: `total_liabilities_q[Q1-2024]`.
- **net_premium_income_q**: Quarterly net premium income in IDR. Use: `net_premium_income_q[Q1-2024]`. (insurance)
- **allowance_for_loans_q**: Quarterly allowance for loan losses in IDR. Use: `allowance_for_loans_q[Q1-2024]`. (banking)
- **current_liabilities_q**: Quarterly current liabilities in IDR. Use: `current_liabilities_q[Q1-2024]`.
- **non_current_liabilities_q**: Quarterly non-current liabilities in IDR. Use: `non_current_liabilities_q[Q1-2024]`.
- **total_equity_q**: Quarterly total equity in IDR. Use: `total_equity_q[Q1-2024]`.
- **total_debt_q**: Quarterly total debt in IDR. Use: `total_debt_q[Q1-2024]`.
- **cash_only_q**: Quarterly cash (excluding equivalents) in IDR. Use: `cash_only_q[Q1-2024]`.
- **provision_q**: Quarterly provision for losses in IDR. Use: `provision_q[Q1-2024]`.
- **gross_loan_q**: Quarterly gross loans before allowances in IDR. Use: `gross_loan_q[Q1-2024]`. (banking)
- **total_cash_and_due_from_banks_q**: Quarterly cash and amounts due from banks in IDR. Use: `total_cash_and_due_from_banks_q[Q1-2024]`. (banking)
- **operating_cash_flow_q**: Quarterly operating cash flow in IDR. Use: `operating_cash_flow_q[Q1-2024]`.
- **investing_cash_flow_q**: Quarterly investing cash flow in IDR. Use: `investing_cash_flow_q[Q1-2024]`.
- **financing_cash_flow_q**: Quarterly financing cash flow in IDR. Use: `financing_cash_flow_q[Q1-2024]`.
- **net_interest_income_q**: Quarterly net interest income in IDR. Use: `net_interest_income_q[Q1-2024]`. (banking)
- **non_interest_income_q**: Quarterly non-interest income in IDR. Use: `non_interest_income_q[Q1-2024]`. (banking)
- **free_cash_flow_q**: Quarterly free cash flow in IDR. Use: `free_cash_flow_q[Q1-2024]`.
- **premium_income_q**: Quarterly gross premium income in IDR. Use: `premium_income_q[Q1-2024]`. (insurance)
- **capital_expenditure_q**: Quarterly capital expenditure in IDR. Use: `capital_expenditure_q[Q1-2024]`.



**How to Use:** The query checks if **any** object in the list matches the condition. Use `=` or `like` for strings, numeric operators for numbers.


- `where=major_shareholders_name like 'PT%' and major_shareholders_share_percentage > 0.1`
- `where=key_executives_name = 'Prajogo Pangestu'`


- **key_executives_name**: Filter by executive name in the key_executives list. Use `like` operator.
- **key_executives_position**: Filter by executive position/title in the key_executives list. Use `like` operator.
- **executives_shareholdings_name**: Filter by executive name in the shareholdings list.
- **executives_shareholdings_share_amount**: Filter by executive share amount (number of shares).
- **executives_shareholdings_share_percentage**: Filter by executive ownership percentage.
- **major_shareholders_name**: Filter by major shareholder name. Use `like` operator.
- **major_shareholders_share_value**: Filter by major shareholder share value in IDR.
- **major_shareholders_share_amount**: Filter by major shareholder number of shares.
- **major_shareholders_share_percentage**: Filter by major shareholder ownership percentage.
- **free_float**: Public (non-insider) ownership percentage from major_shareholders. Value is a decimal (0.45 = 45%).





> 💳 **Credits**: Costs 1 API credit for structured queries. Using the natural-language `?q=` parameter costs 3 API credits.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `where` | `query` | `string` | Tidak | `-` | SQL-like conditions for advanced filtering. Ignored if `q` is present. Supports operators `=`, `!=`, `>`, `>=`, `<`, `<=`, `like`, `in` combined with `and`/`or`. Use bracket notation for yearly fields: `revenue[2024] > 1000000000000`. Supports arithmetic on both sides: `revenue[2024] / total_assets[2024] > 0.5`. |
| `q` | `query` | `string` | Tidak | `-` | A natural language query (e.g. `top 10 tech companies by revenue in 2023`). When `q` is provided, all other query parameters (`where`, `order_by`, etc.) are ignored as the LLM will generate them. |
| `order_by` | `query` | `string` | Tidak | `symbol` | Field to sort results by. Use `-` prefix for descending order (e.g. `-market_cap`). Supports arithmetic expressions (e.g. `-(earnings[2024]/earnings[2023])`). Ignored if `q` is present. |
| `desc` | `query` | `boolean` | Tidak | `False` | Sort in descending order. Ignored if `q` is present. |
| `limit` | `query` | `integer` | Tidak | `50` | Maximum number of results to return. Max: 200. Ignored if `q` is present. |
| `offset` | `query` | `integer` | Tidak | `0` | Number of results to skip for pagination. Ignored if `q` is present. |
| `include_query_values` | `query` | `boolean` | Tidak | `False` | If `true`, the response includes a `query_values` object showing the interpreted year and country extracted from the query. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/companies/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 2. Free Float Market Analysis
- **Method & Path**: `GET https://api.sectors.app/v2/free-float/`
- **Kategori**: `Indonesia (IDX)` / `Company Screener`
- **Biaya Kredit**: `Costs 1 API credit per 100 companies returned, rounded up.`

**Penjelasan**:
Returns the free float percentage for IDX-listed companies, optionally filtered by one level of the sector taxonomy. Results are ordered by `free_float` descending.

> 💡 **Note**: Free float is calculated as the `share_percentage` of the **Public** entry in a company's major shareholders list.

> ⚠️ **Warning**: Query parameters are **mutually exclusive**. Provide at most one filter parameter per request.

> 💳 **Credits**: Costs 1 API credit per 100 companies returned, rounded up.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `sector` | `query` | `string` | Tidak | `-` | Kebab-case sector slug. E.g. `infrastructures`, `healthcare`, `transportation-logistic`. Retrieve valid values from the [Subsectors](https://docs.sectors.app/api-references/v2/indonesia/helper-list/subsectors) endpoint. |
| `sub_sector` | `query` | `string` | Tidak | `-` | Kebab-case subsector slug. E.g. `banks`, `basic-materials`, `food-beverage`. Retrieve valid values from the [Subsectors](https://docs.sectors.app/api-references/v2/indonesia/helper-list/subsectors) endpoint. |
| `industry` | `query` | `string` | Tidak | `-` | Kebab-case industry slug. E.g. `oil-gas`, `electrical`, `chemicals`. Retrieve valid values from the [Industries](https://docs.sectors.app/api-references/v2/indonesia/helper-list/industries) endpoint. |
| `sub_industry` | `query` | `string` | Tidak | `-` | Kebab-case sub-industry slug. E.g. `coal-production`, `gold`, `healthcare-providers`. Retrieve valid values from the [Subindustries](https://docs.sectors.app/api-references/v2/indonesia/helper-list/subindustries) endpoint. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/free-float/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

## Sub-Kategori: Helper Lists

### 3. Companies with Revenue Segments
- **Method & Path**: `GET https://api.sectors.app/v2/companies/list_companies_with_segments/`
- **Kategori**: `Indonesia (IDX)` / `Helper Lists`
- **Biaya Kredit**: `Costs 1 API credit.`

**Penjelasan**:
Returns a dictionary of all companies that have revenue and cost segment data available, along with their available financial years.

**Used by:** [Company Revenue and Cost Segments](https://docs.sectors.app/api-references/v2/indonesia/report/company-segments)

> 💳 **Credits**: Costs 1 API credit.

*Endpoint ini tidak membutuhkan parameter input query atau path.*

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/companies/list_companies_with_segments/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 4. Latest Quarterly Financial Dates (Universe)
- **Method & Path**: `GET https://api.sectors.app/v2/companies/quarterly-financial-dates/`
- **Kategori**: `Indonesia (IDX)` / `Helper Lists`
- **Biaya Kredit**: `Costs 1 API credit per page. The full universe is ~32 pages at the maximum `limit` of 30 (~32 credits per full sweep). Use `since` to poll incrementally for far fewer credits.`

**Penjelasan**:
Returns the **latest** available quarterly report date (and its quarter label) for **every** IDX company in one paginated feed — instead of calling the per-symbol [Quarterly Financial Dates](https://docs.sectors.app/api-references/v2/indonesia/helper-list/company-quarterly-dates) helper once per ticker.

Built for **freshness polling**: store the dates you've seen, then re-poll with `?since=` to fetch only the companies that have since reported a new quarter, keeping repeat polls cheap.

**Related:** [Quarterly Financials](https://docs.sectors.app/api-references/v2/indonesia/report/quarterly-financials) for the actual figures on a given `report_date`.

> 💡 **Note**: One row per company (~950), sorted by symbol. Companies with no quarterly data are omitted.

> 💳 **Credits**: Costs 1 API credit per page. The full universe is ~32 pages at the maximum `limit` of 30 (~32 credits per full sweep). Use `since` to poll incrementally for far fewer credits.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `year` | `query` | `integer` | Tidak | `-` | Restrict to report dates within this calendar year, then return each company's latest quarter within it (e.g. `2024`). |
| `limit` | `query` | `integer` | Tidak | `20` | Maximum number of companies to return per page. Max: 30. |
| `offset` | `query` | `integer` | Tidak | `0` | Number of companies to skip for pagination. |
| `since` | `query` | `string` | Tidak | `-` | Return only companies whose latest quarter-end date is on or after this date (`YYYY-MM-DD`). Use it to poll for newly-reported quarters. A future date returns an empty result set. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/companies/quarterly-financial-dates/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 5. Quarterly Financial Dates
- **Method & Path**: `GET https://api.sectors.app/v2/company/get_quarterly_financial_dates/{symbol}/`
- **Kategori**: `Indonesia (IDX)` / `Helper Lists`
- **Biaya Kredit**: `Costs 1 API credit.`

**Penjelasan**:
Returns all available quarterly financial report dates for a given symbol, grouped by year. Use the `report_date` values returned here as inputs to the `report_date` parameter in the Quarterly Financials endpoint.

**Used by:** [Company Quarterly Financials](https://docs.sectors.app/api-references/v2/indonesia/report/quarterly-financials)

> 💡 **Note**: IDX symbol: 4 letters, optionally followed by `.jk` (case-insensitive). E.g. `ASII`, `BBCA`, `BMRI`.

> 💳 **Credits**: Costs 1 API credit.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `symbol` | `path` | `string` | Ya | `-` | IDX symbol symbol. E.g. `ASII`, `BBCA`. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/company/get_quarterly_financial_dates/BBCA/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 6. Industries
- **Method & Path**: `GET https://api.sectors.app/v2/industries/`
- **Kategori**: `Indonesia (IDX)` / `Helper Lists`
- **Biaya Kredit**: `Costs 1 API credit.`

**Penjelasan**:
Returns all available subsector/industry pairs as kebab-case slugs. Use these values as inputs to the `industry` parameter.

**Used by:** [Companies Screener](https://docs.sectors.app/api-references/v2/indonesia/screener/companies), [Free Float Market Analysis](https://docs.sectors.app/api-references/v2/indonesia/screener/free-float)

> 💳 **Credits**: Costs 1 API credit.

*Endpoint ini tidak membutuhkan parameter input query atau path.*

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/industries/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 7. Subindustries
- **Method & Path**: `GET https://api.sectors.app/v2/subindustries/`
- **Kategori**: `Indonesia (IDX)` / `Helper Lists`
- **Biaya Kredit**: `Costs 1 API credit.`

**Penjelasan**:
Returns all available industry/sub-industry pairs as kebab-case slugs. Use these values as inputs to the `sub_industry` parameter.

**Used by:** [Companies Screener](https://docs.sectors.app/api-references/v2/indonesia/screener/companies), [Free Float Market Analysis](https://docs.sectors.app/api-references/v2/indonesia/screener/free-float)

> 💳 **Credits**: Costs 1 API credit.

*Endpoint ini tidak membutuhkan parameter input query atau path.*

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/subindustries/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 8. Subsectors
- **Method & Path**: `GET https://api.sectors.app/v2/subsectors/`
- **Kategori**: `Indonesia (IDX)` / `Helper Lists`
- **Biaya Kredit**: `Costs 1 API credit.`

**Penjelasan**:
Returns all available sector/subsector pairs as kebab-case slugs. Use these values as inputs to `sector` and `sub_sector` parameters.

**Used by:** [Companies Screener](https://docs.sectors.app/api-references/v2/indonesia/screener/companies), [Sector Report](https://docs.sectors.app/api-references/v2/indonesia/report/sector-report), [Free Float Market Analysis](https://docs.sectors.app/api-references/v2/indonesia/screener/free-float)

> 💳 **Credits**: Costs 1 API credit.

*Endpoint ini tidak membutuhkan parameter input query atau path.*

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/subsectors/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 9. News Tags
- **Method & Path**: `GET https://api.sectors.app/v2/tags/`
- **Kategori**: `Indonesia (IDX)` / `Helper Lists`
- **Biaya Kredit**: `Costs 1 API credit.`

**Penjelasan**:
Returns a sorted alphabetical array of all available tag slugs used across news articles and company filings. Use these values as inputs to the `tags` parameter.

**Used by:** [News Articles](https://docs.sectors.app/api-references/v2/indonesia/news/news), [Company Filings](https://docs.sectors.app/api-references/v2/indonesia/news/filings)

> 💳 **Credits**: Costs 1 API credit.

*Endpoint ini tidak membutuhkan parameter input query atau path.*

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/tags/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

## Sub-Kategori: Detailed Reports

### 10. Corporate Actions
- **Method & Path**: `GET https://api.sectors.app/v2/company/corporate-actions/{symbol}/`
- **Kategori**: `Indonesia (IDX)` / `Detailed Reports`
- **Biaya Kredit**: `Costs 1 API credit.`

**Penjelasan**:
> 💡 **Note**: IDX symbol: 4 letters, optionally followed by `.jk` (case-insensitive). E.g. `BBCA`, `BMRI`, `TLKM`.

Returns all corporate action history for a given IDX-listed company: stock splits, right issues, warrants, bonus shares, AGM events, upcoming dividends, and historical dividends.

> 💡 **Note**: For every company's actions in a date window, see the market-wide [Corporate Actions Calendar](https://docs.sectors.app/api-references/v2/indonesia/news/corporate-actions).

> 💳 **Credits**: Costs 1 API credit.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `symbol` | `path` | `string` | Ya | `-` | IDX symbol. E.g. `BBCA`, `BMRI`. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/company/corporate-actions/BBCA/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 11. Company Revenue Segments
- **Method & Path**: `GET https://api.sectors.app/v2/company/get-segments/{symbol}/`
- **Kategori**: `Indonesia (IDX)` / `Detailed Reports`
- **Biaya Kredit**: `Costs 1 API credit.`

**Penjelasan**:
Returns a Sankey-graph-ready revenue and cost segment breakdown for a given company and financial year. Not all companies have segment data — use the [Companies with Revenue Segments](https://docs.sectors.app/api-references/v2/indonesia/helper-list/companies-segments-list) endpoint to check availability.

> 💡 **Note**: IDX symbol: 4 letters, optionally followed by `.jk` (case-insensitive). E.g. `BUMI`, `TLKM`, `ASII`.

> 💳 **Credits**: Costs 1 API credit.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `symbol` | `path` | `string` | Ya | `-` | IDX symbol symbol. E.g. `BUMI`, `TLKM`. Not all companies have segment data — check the [Companies with Revenue Segments](https://docs.sectors.app/api-references/v2/indonesia/helper-list/companies-segments-list) helper first. |
| `financial_year` | `query` | `integer` | Tidak | `-` | Financial year to retrieve. Defaults to the latest available year. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/company/get-segments/BBCA/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 12. Company Report
- **Method & Path**: `GET https://api.sectors.app/v2/company/report/`
- **Kategori**: `Indonesia (IDX)` / `Detailed Reports`
- **Biaya Kredit**: `Costs 1 API credit per requested section. Default behavior (all 8 sections) consumes 8 credits.`

**Penjelasan**:
Returns a comprehensive company report organized into distinct sections. By default all sections are included. Use `sections` to request only the data you need and reduce response size.

> 💡 **Note**: IDX symbol: 4 letters, optionally followed by `.jk` (case-insensitive). E.g. `BREN`, `BBCA`, `TLKM`.


- **overview**: Company identity, market cap, price history, ESG score, tags, indices, affiliates
- **valuation**: Close price, forward PE, intrinsic value, historical valuation (PB, PE, PS, PCF, PEG by year)
- **future**: Analyst forecasts, EPS growth estimates
- **peers**: Peer comparison within the same subsector
- **financials**: Historical annual financials (revenue, earnings, assets, equity, margins)
- **dividend**: Dividend history, yield, payout ratio
- **management**: Key executives and their shareholdings
- **ownership**: Major shareholders and ownership structure


> 💳 **Credits**: Costs 1 API credit per requested section. Default behavior (all 8 sections) consumes 8 credits.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `symbol` | `path` | `string` | Ya | `-` | IDX symbol symbol. E.g. `BREN`, `BBCA`. |
| `sections` | `query` | `array` | Tidak | `-` | Comma-separated list of sections to include. Default to all. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/company/report/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 13. Company Report
- **Method & Path**: `GET https://api.sectors.app/v2/company/report/{symbol}/`
- **Kategori**: `Indonesia (IDX)` / `Detailed Reports`
- **Biaya Kredit**: `Costs 1 API credit per requested section. Default behavior (all 8 sections) consumes 8 credits.`

**Penjelasan**:
Returns a comprehensive company report organized into distinct sections. By default all sections are included. Use `sections` to request only the data you need and reduce response size.

> 💡 **Note**: IDX symbol: 4 letters, optionally followed by `.jk` (case-insensitive). E.g. `BREN`, `BBCA`, `TLKM`.


- **overview**: Company identity, market cap, price history, ESG score, tags, indices, affiliates
- **valuation**: Close price, forward PE, intrinsic value, historical valuation (PB, PE, PS, PCF, PEG by year)
- **future**: Analyst forecasts, EPS growth estimates
- **peers**: Peer comparison within the same subsector
- **financials**: Historical annual financials (revenue, earnings, assets, equity, margins)
- **dividend**: Dividend history, yield, payout ratio
- **management**: Key executives and their shareholdings
- **ownership**: Major shareholders and ownership structure


> 💳 **Credits**: Costs 1 API credit per requested section. Default behavior (all 8 sections) consumes 8 credits.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `symbol` | `path` | `string` | Ya | `-` | IDX symbol symbol. E.g. `BREN`, `BBCA`. |
| `sections` | `query` | `array` | Tidak | `-` | Comma-separated list of sections to include. Default to all. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/company/report/BBCA/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 14. Shareholders Composition
- **Method & Path**: `GET https://api.sectors.app/v2/company/shareholders-composition/{symbol}/`
- **Kategori**: `Indonesia (IDX)` / `Detailed Reports`
- **Biaya Kredit**: `Costs 1 API credit.`

**Penjelasan**:
> 💡 **Note**: IDX symbol: 4 letters, optionally followed by `.jk` (case-insensitive). E.g. `BBCA`, `BMRI`, `TLKM`.

Returns monthly shareholder composition snapshots for a given IDX-listed company within a single calendar year, broken down by investor category (insurance, corporate, pension fund, financial institutions, individual, mutual fund, securities companies, foundation, other) for both local (`_l`) and foreign (`_f`) investors.

> 💡 **Note**: Data is available from 2021 onwards. Querying earlier years returns an empty `data` array.

> 💳 **Credits**: Costs 1 API credit.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `symbol` | `path` | `string` | Ya | `-` | IDX symbol. E.g. `BBCA`, `BMRI`. |
| `year` | `query` | `integer` | Tidak | `-` | Calendar year (e.g. `2025`). Defaults to the current year. Data is available from 2021; earlier years return an empty `data` array. Future years are rejected. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/company/shareholders-composition/BBCA/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 15. Company Quarterly Financials
- **Method & Path**: `GET https://api.sectors.app/v2/financials/quarterly/{symbol}/`
- **Kategori**: `Indonesia (IDX)` / `Detailed Reports`
- **Biaya Kredit**: `Costs 1 API credit per quarter returned.`

**Penjelasan**:
Returns quarterly financial data for a given IDX symbol. Fields vary by sector — financial-sector companies (banks, insurance) have additional metrics like `net_interest_income`, `gross_loan`, `total_deposit`.

> 💡 **Note**: Use the [Quarterly Financial Dates](https://docs.sectors.app/api-references/v2/indonesia/helper-list/company-quarterly-dates) endpoint to get valid `report_date` values for a symbol.

> 💡 **Note**: IDX symbol: 4 letters, optionally followed by `.jk` (case-insensitive). E.g. `BMRI`, `BBCA`, `TLKM`.

> 💳 **Credits**: Costs 1 API credit per quarter returned.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `symbol` | `path` | `string` | Ya | `-` | IDX symbol symbol. E.g. `BMRI`, `BBCA`. |
| `report_date` | `query` | `string` | Tidak | `-` | Specific report date (YYYY-MM-DD). Use the [Quarterly Financial Dates](https://docs.sectors.app/api-references/v2/indonesia/helper-list/company-quarterly-dates) endpoint to get valid values. |
| `approx` | `query` | `boolean` | Tidak | `True` | If `true` (default), use approximate quarter matching when an exact date is not found. |
| `n_quarters` | `query` | `integer` | Tidak | `-` | Number of most recent quarters to return. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/financials/quarterly/BBCA/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 16. Subsector Report
- **Method & Path**: `GET https://api.sectors.app/v2/subsector/report/`
- **Kategori**: `Indonesia (IDX)` / `Detailed Reports`
- **Biaya Kredit**: `Costs 1 API credit per requested section. Default behavior (all 6 sections) consumes 6 credits.`

**Penjelasan**:
Returns a comprehensive report for an IDX subsector, organized into distinct sections. Use `sections` to fetch only the data you need.

> 💡 **Note**: The `sub_sector` path parameter must be in **kebab-case** format. Get valid values from the [Subsectors](https://docs.sectors.app/api-references/v2/indonesia/helper-list/subsectors) endpoint. E.g. `banks`, `utilities`, `food-beverage`.


- **statistics**: Company count, median PE, weighted avg PE, min/max PE
- **market_cap**: Total and avg market cap, quarterly market cap trend, mcap change (1w/1y/YTD)
- **stability**: Weighted max drawdown, weighted relative standard deviation
- **valuation**: Historical PB, PE, PS, PCF by year
- **growth**: Weighted avg revenue and earnings growth
- **companies**: List of companies in the subsector with key metrics


> 💳 **Credits**: Costs 1 API credit per requested section. Default behavior (all 6 sections) consumes 6 credits.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `sub_sector` | `path` | `string` | Ya | `-` | Kebab-case subsector slug. E.g. `banks`, `utilities`. Get valid values from the [Subsectors](https://docs.sectors.app/api-references/v2/indonesia/helper-list/subsectors) endpoint. |
| `sections` | `query` | `array` | Tidak | `-` | Comma-separated sections to include. Default to all. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/subsector/report/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 17. Subsector Report
- **Method & Path**: `GET https://api.sectors.app/v2/subsector/report/{sub_sector}/`
- **Kategori**: `Indonesia (IDX)` / `Detailed Reports`
- **Biaya Kredit**: `Costs 1 API credit per requested section. Default behavior (all 6 sections) consumes 6 credits.`

**Penjelasan**:
Returns a comprehensive report for an IDX subsector, organized into distinct sections. Use `sections` to fetch only the data you need.

> 💡 **Note**: The `sub_sector` path parameter must be in **kebab-case** format. Get valid values from the [Subsectors](https://docs.sectors.app/api-references/v2/indonesia/helper-list/subsectors) endpoint. E.g. `banks`, `utilities`, `food-beverage`.


- **statistics**: Company count, median PE, weighted avg PE, min/max PE
- **market_cap**: Total and avg market cap, quarterly market cap trend, mcap change (1w/1y/YTD)
- **stability**: Weighted max drawdown, weighted relative standard deviation
- **valuation**: Historical PB, PE, PS, PCF by year
- **growth**: Weighted avg revenue and earnings growth
- **companies**: List of companies in the subsector with key metrics


> 💳 **Credits**: Costs 1 API credit per requested section. Default behavior (all 6 sections) consumes 6 credits.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `sub_sector` | `path` | `string` | Ya | `-` | Kebab-case subsector slug. E.g. `banks`, `utilities`. Get valid values from the [Subsectors](https://docs.sectors.app/api-references/v2/indonesia/helper-list/subsectors) endpoint. |
| `sections` | `query` | `array` | Tidak | `-` | Comma-separated sections to include. Default to all. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/subsector/report/banks/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

## Sub-Kategori: Transaction Data

### 18. Daily Full-Universe Close
- **Method & Path**: `GET https://api.sectors.app/v2/close/`
- **Kategori**: `Indonesia (IDX)` / `Transaction Data`
- **Biaya Kredit**: `Costs 1 API credit per page. The full ~950-ticker universe is ~32 pages at the maximum `limit` of 30 (~32 credits per full pull).`

**Penjelasan**:
Returns the daily closing price for **every** IDX ticker on a single trading day, in one paginated feed — instead of calling the per-symbol [Daily Transaction Data](https://docs.sectors.app/api-references/v2/indonesia/transaction/daily) endpoint once per ticker.

> 💡 **Note**: Defaults to the most recent trading day. Pass `date` (`YYYY-MM-DD`) to pull a specific day. Future dates return 400.

> 💡 **Note**: Tickers with no recorded close for the requested day are omitted.

> 💳 **Credits**: Costs 1 API credit per page. The full ~950-ticker universe is ~32 pages at the maximum `limit` of 30 (~32 credits per full pull).

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `limit` | `query` | `integer` | Tidak | `20` | Maximum number of tickers to return per page. Max: 30. |
| `offset` | `query` | `integer` | Tidak | `0` | Number of tickers to skip for pagination. |
| `date` | `query` | `string` | Tidak | `-` | Trading day to pull, in `YYYY-MM-DD` format. Defaults to the most recent trading day with data. Future dates return 400. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/close/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 19. Daily Transaction Data
- **Method & Path**: `GET https://api.sectors.app/v2/daily/{symbol}/`
- **Kategori**: `Indonesia (IDX)` / `Transaction Data`
- **Biaya Kredit**: `Costs 1 API credit.`

**Penjelasan**:
Returns daily close price, volume, and market cap for a given IDX symbol over a date range of up to 90 days.

> 💡 **Note**: IDX symbol: 4 letters, optionally followed by `.jk` (case-insensitive). E.g. `BBCA`, `GOTO`, `TLKM`.

> 💡 **Note**: Date range: defaults to last 30 days. Max window 90 days; wider ranges are clamped to the most recent 90 days ending at `end`. Future `end` dates return 400.

> 💳 **Credits**: Costs 1 API credit.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `symbol` | `path` | `string` | Ya | `-` | IDX symbol. E.g. `BBCA`, `GOTO`, `TLKM`. |
| `start` | `query` | `string` | Tidak | `-` | Start date in `YYYY-MM-DD` format. Defaults to 30 days before `end`. Wider ranges are clamped to the most recent 90 days. |
| `end` | `query` | `string` | Tidak | `-` | End date in `YYYY-MM-DD` format. Defaults to today. Future dates return 400. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/daily/BBCA/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 20. IDX Market Summary
- **Method & Path**: `GET https://api.sectors.app/v2/idx-total/`
- **Kategori**: `Indonesia (IDX)` / `Transaction Data`
- **Biaya Kredit**: `Costs 1 API credit.`

**Penjelasan**:
Returns historical total IDX market capitalization for a date range of up to 90 days.

> 💡 **Note**: Earliest available data is from **January 1, 2021**. Requesting earlier dates returns 400.

> 💡 **Note**: Date range: defaults to last 30 days. Max window 90 days; wider ranges are clamped to the most recent 90 days ending at `end`. Future `end` dates return 400.

> 💳 **Credits**: Costs 1 API credit.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `start` | `query` | `string` | Tidak | `-` | Start date in `YYYY-MM-DD` format. Earliest valid: `2021-01-01`. Defaults to 30 days before `end`. Wider ranges are clamped to the most recent 90 days. |
| `end` | `query` | `string` | Tidak | `-` | End date in `YYYY-MM-DD` format. Defaults to today. Future dates return 400. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/idx-total/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 21. Daily Full-Universe Index Close
- **Method & Path**: `GET https://api.sectors.app/v2/index-daily/`
- **Kategori**: `Indonesia (IDX)` / `Transaction Data`
- **Biaya Kredit**: `Costs 1 API credit.`

**Penjelasan**:
Returns the closing level of **every** IDX index on a single trading day in one call — instead of calling the per-index [Index Daily Transaction Data](https://docs.sectors.app/api-references/v2/indonesia/transaction/index-daily) endpoint once per index.

> 💡 **Note**: Defaults to the most recent trading day. Pass `date` (`YYYY-MM-DD`) to pull a specific day. Future dates return 400.

> 💡 **Note**: Indices with no recorded close for the requested day are omitted. 

> 💳 **Credits**: Costs 1 API credit.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `date` | `query` | `string` | Tidak | `-` | Trading day to pull, in `YYYY-MM-DD` format. Defaults to the most recent trading day with data. Future dates return 400. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/index-daily/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 22. Index Daily Transaction Data
- **Method & Path**: `GET https://api.sectors.app/v2/index-daily/{index_code}/`
- **Kategori**: `Indonesia (IDX)` / `Transaction Data`
- **Biaya Kredit**: `Costs 1 API credit.`

**Penjelasan**:
Returns daily closing price for a given IDX index over a date range of up to 90 days.

> 💡 **Note**: Earliest available data is from **January 2, 2019**.


`ftse`, `idx30`, `idxbumn20`, `idxesgl`, `idxg30`, `idxhidiv20`, `idxq30`, `idxv30`, `ihsg`, `jii70`, `kompas100`, `lq45`, `sminfra18`, `srikehati`, `sti`, `economic30`, `idxvesta28`


> 💡 **Note**: Date range: defaults to last 30 days. Max window 90 days; wider ranges are clamped to the most recent 90 days ending at `end`. Future `end` dates return 400.

> 💳 **Credits**: Costs 1 API credit.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `index_code` | `path` | `string` | Ya | `-` | Index code. E.g. `lq45`, `ihsg`, `idx30`. |
| `start` | `query` | `string` | Tidak | `-` | Start date in `YYYY-MM-DD` format. Defaults to 30 days before `end`. Wider ranges are clamped to the most recent 90 days. |
| `end` | `query` | `string` | Tidak | `-` | End date in `YYYY-MM-DD` format. Defaults to today. Future dates return 400. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/index-daily/idx30/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

## Sub-Kategori: Rankings

### 23. Top Company Movers
- **Method & Path**: `GET https://api.sectors.app/v2/companies/top-changes/`
- **Kategori**: `Indonesia (IDX)` / `Rankings`
- **Biaya Kredit**: `Costs 1 API credit per requested classification × period combination. Default behavior (2 classifications × 5 periods) consumes 10 credits.`

**Penjelasan**:
Returns top gainers and losers across multiple time periods. Supports two classifications (`top_gainers`, `top_losers`) and five periods (`1d`, `7d`, `14d`, `30d`, `365d`).

> 💳 **Credits**: Costs 1 API credit per requested classification × period combination. Default behavior (2 classifications × 5 periods) consumes 10 credits.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `sub_sector` | `query` | `string` | Tidak | `-` | Filter by kebab-case subsector slug. E.g. `banks`. Get valid values from the [Subsectors](https://docs.sectors.app/api-references/v2/indonesia/helper-list/subsectors) endpoint. |
| `n_stock` | `query` | `integer` | Tidak | `5` | Number of companies per period. Default 5, max 10. |
| `classifications` | `query` | `array` | Tidak | `all` | Comma-separated. Choices: `top_gainers`, `top_losers`. Default: both. |
| `periods` | `query` | `array` | Tidak | `all` | Comma-separated periods. Choices: `1d`, `7d`, `14d`, `30d`, `365d`. Default: all. |
| `min_mcap_billion` | `query` | `integer` | Tidak | `5000` | Minimum market cap filter in billion IDR. Default 5000. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/companies/top-changes/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 24. Most Traded Stocks
- **Method & Path**: `GET https://api.sectors.app/v2/most-traded/`
- **Kategori**: `Indonesia (IDX)` / `Rankings`
- **Biaya Kredit**: `Costs 2 API credits.`

**Penjelasan**:
Returns the most traded IDX stocks by transaction volume over a date range of up to 90 days. Results are keyed by date.

> 💡 **Note**: Date range: defaults to last 30 days. Max window 90 days; wider ranges are clamped to the most recent 90 days ending at `end`. Future `end` dates return 400.

> 💳 **Credits**: Costs 2 API credits.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `sub_sector` | `query` | `string` | Tidak | `-` | Filter by kebab-case subsector slug. E.g. `banks`. Get valid values from the [Subsectors](https://docs.sectors.app/api-references/v2/indonesia/helper-list/subsectors) endpoint. |
| `start` | `query` | `string` | Tidak | `-` | Start date in `YYYY-MM-DD` format. Defaults to 30 days before `end`. Wider ranges are clamped to the most recent 90 days. |
| `end` | `query` | `string` | Tidak | `-` | End date in `YYYY-MM-DD` format. Defaults to today. Future dates return 400. |
| `adjusted` | `query` | `boolean` | Tidak | `False` | If `true`, rank by volume × closing price instead of raw volume. |
| `n_stock` | `query` | `integer` | Tidak | `5` | Number of tickers per day. Default 5, max 10. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/most-traded/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

## Sub-Kategori: IPO & Performance

### 25. Company IPO & Listing Performance
- **Method & Path**: `GET https://api.sectors.app/v2/listing-performance/{symbol}/`
- **Kategori**: `Indonesia (IDX)` / `IPO & Performance`
- **Biaya Kredit**: `Costs 1 API credit.`

**Penjelasan**:
Returns price change percentages since listing date for a given IDX-listed symbol, across 7, 30, 90, and 365-day windows.

> 💡 **Note**: Listing performance data is only available for tickers listed **after May 2005**.

> 💡 **Note**: IDX symbol: 4 letters, optionally followed by `.jk` (case-insensitive). E.g. `GOTO`, `BREN`, `BUKA`.

> 💳 **Credits**: Costs 1 API credit.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `symbol` | `path` | `string` | Ya | `-` | IDX symbol symbol. E.g. `ARTO`, `BREN`, `GOTO`. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/listing-performance/BBCA/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

## Sub-Kategori: News & Filings

### 26. Corporate Actions Calendar
- **Method & Path**: `GET https://api.sectors.app/v2/corporate-actions/`
- **Kategori**: `Indonesia (IDX)` / `News & Filings`
- **Biaya Kredit**: `Costs 1 API credit per requested type. Default (all 7 types) consumes 7 credits.`

**Penjelasan**:
Corporate actions across every IDX ticker in a date window, grouped by type: the market-wide counterpart of the per-symbol [Corporate Actions](https://docs.sectors.app/api-references/v2/indonesia/company/corporate-actions) endpoint. Row keys match the per-symbol endpoint. `start`/`end` filter (and sort) each type on one key: `dividend`, `upcoming_dividend`, `bonus` and `right_issue` on `ex_date`, `stock_split` on `date` (its ex-date), `warrant` on `trading_period_start`, and `agm` on `agm_date`; ties sort by `symbol`.

> 💡 **Note**: `end` may be in the future, so the window works as a calendar. Default window: today - 30 days to today + 30 days. Wider ranges are clamped to the 90 days ending at `end`.

> 💡 **Note**: Only the requested `type` keys are present in the response.

> 💳 **Credits**: Costs 1 API credit per requested type. Default (all 7 types) consumes 7 credits.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `start` | `query` | `string` | Tidak | `-` | Start date (YYYY-MM-DD). Default: end - 30 days. |
| `end` | `query` | `string` | Tidak | `-` | End date (YYYY-MM-DD); may be in the future. Default: today + 30 days. |
| `type` | `query` | `array` | Tidak | `-` | Comma-separated action types. Default: all. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/corporate-actions/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 27. Company Filings
- **Method & Path**: `GET https://api.sectors.app/v2/filings/`
- **Kategori**: `Indonesia (IDX)` / `News & Filings`
- **Biaya Kredit**: `Costs 1 API credit.`

**Penjelasan**:
Returns IDX insider trading filings — buy/sell transactions by company insiders and major shareholders. Supports filtering by sector, subsector, tags, symbol, transaction type, holder_type, and date range.

> 💡 **Note**: IDX symbol: 4 letters, optionally followed by `.jk` (case-insensitive). E.g. `BBCA`, `BMRI`, `TLKM`.

> 💡 **Note**: Date filters: both `start` and `end` are independent and optional — omit either side to leave that bound unconstrained. Future `end` dates return 400.

> 💳 **Credits**: Costs 1 API credit.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `symbol` | `query` | `string` | Tidak | `-` | IDX symbol symbol to filter by. E.g. `BBCA`, `BMRI`. |
| `sector` | `query` | `string` | Tidak | `-` | Kebab-case sector slug. E.g. `healthcare`, `financials`. Get valid values from the [Subsectors](https://docs.sectors.app/api-references/v2/indonesia/helper-list/subsectors) endpoint. |
| `sub_sector` | `query` | `string` | Tidak | `-` | Kebab-case subsector slug. E.g. `banks`, `tobacco`. Get valid values from the [Subsectors](https://docs.sectors.app/api-references/v2/indonesia/helper-list/subsectors) endpoint. |
| `start` | `query` | `string` | Tidak | `-` | Start date in `YYYY-MM-DD` format. Optional; if omitted, no lower bound is applied. Filters on `timestamp`. |
| `end` | `query` | `string` | Tidak | `-` | End date in `YYYY-MM-DD` format. Optional; if omitted, no upper bound is applied. Future dates return 400. |
| `limit` | `query` | `integer` | Tidak | `20` | Number of results to return. Maximum: 30. |
| `offset` | `query` | `integer` | Tidak | `0` | Number of results to skip for pagination. |
| `transaction_type` | `query` | `string` | Tidak | `-` | Filter by transaction direction: `buy`, `sell`, or `others`. |
| `tags` | `query` | `string` | Tidak | `-` | Comma-separated tag slugs. E.g. `Bullish,insider-trading`. Get valid values from the [News Tags](https://docs.sectors.app/api-references/v2/indonesia/helper-list/tags) endpoint. |
| `holder_type` | `query` | `string` | Tidak | `-` | Filter by holder type (case-insensitive). |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/filings/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 28. News Articles
- **Method & Path**: `GET https://api.sectors.app/v2/news/`
- **Kategori**: `Indonesia (IDX)` / `News & Filings`
- **Biaya Kredit**: `Costs 1 API credit.`

**Penjelasan**:
Returns paginated news articles from either the IDX (Indonesian Stock Exchange) or mining news sources. Use the `extension` parameter to choose the data source — each extension has its own set of valid filter parameters.

> ⚠️ **Warning**: Mixing IDX and mining parameters will return a 400 error. E.g. passing `sector` with `extension=mining` is invalid.


- **sector**: Comma-separated sector slugs (kebab-case). Get values from the [Subsectors](https://docs.sectors.app/api-references/v2/indonesia/helper-list/subsectors) endpoint.
- **sub_sector**: Comma-separated subsector slugs (kebab-case). E.g. `banks`, `insurance`, `retailing`. Get valid values from the [Subsectors](https://docs.sectors.app/api-references/v2/indonesia/helper-list/subsectors) endpoint.
- **tags**: Comma-separated tag slugs. Get values from the [News Tags](https://docs.sectors.app/api-references/v2/indonesia/helper-list/tags) endpoint.
- **symbols**: Comma-separated IDX symbols. E.g. `BBCA,BBRI,BMRI`.
- **keyword**: Case-insensitive substring match on article title.



- **keyword**: Case-insensitive substring match on article title.
- **commodity_type**: Filter by commodity. E.g. `Coal`, `Nickel`, `Gold`.


> 💡 **Note**: Date filters: both `start` and `end` are independent and optional — omit either side to leave that bound unconstrained. Future `end` dates return 400.

> 💳 **Credits**: Costs 1 API credit.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `sector` | `query` | `string` | Tidak | `-` | **IDX only.** Comma-separated sector slugs (kebab-case). |
| `sub_sector` | `query` | `string` | Tidak | `-` | **IDX only.** Comma-separated subsector slugs (kebab-case). |
| `commodity_type` | `query` | `string` | Tidak | `-` | **Mining only.** Filter by commodity type. E.g. `Coal`, `Nickel`. |
| `start` | `query` | `string` | Tidak | `-` | Start date in `YYYY-MM-DD` format. Optional; if omitted, no lower bound is applied. Filters on `timestamp`. |
| `end` | `query` | `string` | Tidak | `-` | End date in `YYYY-MM-DD` format. Optional; if omitted, no upper bound is applied. Future dates return 400. |
| `limit` | `query` | `integer` | Tidak | `20` | Items per page. Max 30. |
| `offset` | `query` | `integer` | Tidak | `0` | Items to skip for pagination. |
| `tags` | `query` | `string` | Tidak | `-` | **IDX only.** Comma-separated tag slugs. Get valid values from the [News Tags](https://docs.sectors.app/api-references/v2/indonesia/helper-list/tags) endpoint. |
| `extension` | `query` | `string` | Tidak | `idx` | Data source. Default `idx`. |
| `keyword` | `query` | `string` | Tidak | `-` | Case-insensitive substring match on article title. Works for both IDX and mining. |
| `symbols` | `query` | `string` | Tidak | `-` | **IDX only.** Comma-separated IDX symbols. E.g. `BBCA,BBRI`. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/news/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 29. Stock Suspensions
- **Method & Path**: `GET https://api.sectors.app/v2/suspensions/`
- **Kategori**: `Indonesia (IDX)` / `News & Filings`
- **Biaya Kredit**: `Costs 1 API credit.`

**Penjelasan**:
Returns a paginated list of historical IDX-listed stock suspensions, including the date a stock was suspended, the official reason, and a link to the IDX PDF notice. Filter by `symbol` to look up a specific company's suspension history, or by `start` / `end` to scope to a date window.

> 💡 **Note**: Date filters: both `start` and `end` are independent and optional — omit either side to leave that bound unconstrained. Future `end` dates return 400.

> 💳 **Credits**: Costs 1 API credit.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `symbol` | `query` | `string` | Tidak | `-` | Optional filter by IDX symbol (case-insensitive). E.g. `BBCA`, `GOTO`. |
| `start` | `query` | `string` | Tidak | `-` | Start date in `YYYY-MM-DD` format. Optional; if omitted, no lower bound is applied. Filters on `suspension_date`. |
| `end` | `query` | `string` | Tidak | `-` | End date in `YYYY-MM-DD` format. Optional; if omitted, no upper bound is applied. Future dates return 400. |
| `limit` | `query` | `integer` | Tidak | `20` | Items per page. Max 30. |
| `offset` | `query` | `integer` | Tidak | `0` | Number of items to skip. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/suspensions/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

## Sub-Kategori: Brokers

### 30. Broker Activity By Code
- **Method & Path**: `GET https://api.sectors.app/v2/broker-activity/{broker_code}/`
- **Kategori**: `Indonesia (IDX)` / `Brokers`
- **Biaya Kredit**: `Costs 1 API credit.`

**Penjelasan**:
All (stock, day) trading activity for one broker over a date range up to 14 days, grouped by date. Optionally filter to a single stock via `symbol`. Each entry in `data` lists every stock the broker touched that day with buy/sell/net values.

> 💡 **Note**: Each row also carries the foreign-investor split of that broker's trades: the `f_*` fields are the portion of the buy/sell frequency, lots, and value executed for foreign investors, and `d_bavg_per_share` / `d_savg_per_share` are the domestic-investor average prices. Domestic frequency, lots, and value are `total - foreign`. These fields are `null` when no foreign-investor participation was recorded for that broker on that day.

> 💡 **Note**: Broker codes are the two-letter exchange-member identifiers (e.g. `MG`, `AK`, `CC`). Retrieve the full list of valid codes from the [Broker Registry](https://docs.sectors.app/api-references/v2/indonesia/brokers/broker-registry) endpoint.

> 💳 **Credits**: Costs 1 API credit.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `broker_code` | `path` | `string` | Ya | `-` | Broker code. E.g. `MG`, `AK`, `CC`. |
| `symbol` | `query` | `string` | Tidak | `-` | Optional filter to a single stock ticker (e.g. `BBCA`). |
| `start` | `query` | `string` | Tidak | `-` | Start date (YYYY-MM-DD). Default: end - 14 days. |
| `end` | `query` | `string` | Tidak | `-` | End date (YYYY-MM-DD). Default: today. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/broker-activity/YP/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 31. Top Accumulations and Distributions Per Broker
- **Method & Path**: `GET https://api.sectors.app/v2/broker-activity/{broker_code}/top/`
- **Kategori**: `Indonesia (IDX)` / `Brokers`
- **Biaya Kredit**: `Costs 2 API credits.`

**Penjelasan**:
Returns the stocks a single broker has been most actively accumulating and distributing over a date range. `top_accumulations` ranks stocks the broker has net bought (largest positive net IDR first); `top_distributions` ranks stocks the broker has net sold (largest negative net IDR first). Each entry also reports how much of that flow was executed for foreign investors (`foreign_net_idr`, `foreign_buy_idr`, `foreign_sell_idr`); pass `foreign=true` to rank by `foreign_net_idr` instead, i.e. the stocks the broker's foreign clients are moving. Useful for tracking a specific broker's directional positioning across the IDX universe.

> 💡 **Note**: Broker codes are the two-letter exchange-member identifiers (e.g. `MG`, `AK`, `CC`). Retrieve the full list of valid codes from the [Broker Registry](https://docs.sectors.app/api-references/v2/indonesia/brokers/broker-registry) endpoint.

> 💳 **Credits**: Costs 2 API credits.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `broker_code` | `path` | `string` | Ya | `-` | Broker code. E.g. `MG`, `AK`, `CC`. |
| `start` | `query` | `string` | Tidak | `-` | Start date (YYYY-MM-DD). Default: end - 90 days. |
| `end` | `query` | `string` | Tidak | `-` | End date (YYYY-MM-DD). Default: today. |
| `foreign` | `query` | `boolean` | Tidak | `False` | If `true`, rank by the foreign-investor portion of each broker's flow instead of the total. Bare `?foreign` also means `true`; any value other than `true`/`false` returns 400. Default `false`. Accumulations and distributions are then ranked by `foreign_net_idr`. |
| `n_brokers` | `query` | `integer` | Tidak | `-` | How many accumulations and distributions to return each (default 10, max 90). |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/broker-activity/YP/top/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 32. Broker Activity Per Symbol
- **Method & Path**: `GET https://api.sectors.app/v2/broker-summary/{symbol}/`
- **Kategori**: `Indonesia (IDX)` / `Brokers`
- **Biaya Kredit**: `Costs 1 API credit.`

**Penjelasan**:
Per-broker daily trading rows for one IDX ticker over a date range up to 14 days, grouped by date. Optionally filter to a single broker via `broker_code`. Each entry in `data` lists every broker active on that day with buy/sell/net values, lots, frequency, and weighted avg price per share.

> 💡 **Note**: Each row also carries the foreign-investor split of that broker's trades: the `f_*` fields are the portion of the buy/sell frequency, lots, and value executed for foreign investors, and `d_bavg_per_share` / `d_savg_per_share` are the domestic-investor average prices. Domestic frequency, lots, and value are `total - foreign`. These fields are `null` when no foreign-investor participation was recorded for that broker on that day.

> 💡 **Note**: IDX symbol: 4 letters, optionally followed by `.jk` (case-insensitive). E.g. `BBCA`, `GOTO`.

> 💳 **Credits**: Costs 1 API credit.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `symbol` | `path` | `string` | Ya | `-` | IDX ticker symbol. E.g. `BBCA`, `GOTO`. |
| `broker_code` | `query` | `string` | Tidak | `-` | Optional filter to a single broker code (e.g. `MG`). |
| `start` | `query` | `string` | Tidak | `-` | Start date (YYYY-MM-DD). Default: end - 14 days. |
| `end` | `query` | `string` | Tidak | `-` | End date (YYYY-MM-DD). Default: today. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/broker-summary/BBCA/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 33. Top Buyers and Sellers Per Symbol
- **Method & Path**: `GET https://api.sectors.app/v2/broker-summary/{symbol}/top/`
- **Kategori**: `Indonesia (IDX)` / `Brokers`
- **Biaya Kredit**: `Costs 2 API credits.`

**Penjelasan**:
Returns the brokers most actively accumulating and distributing a single IDX ticker over a date range. `top_buyers` ranks brokers by net buy value (largest positive net IDR first); `top_sellers` ranks brokers by net sell value (largest negative net IDR first). Each entry also reports how much of that broker's flow was executed for foreign investors (`foreign_net_idr`, `foreign_buy_idr`, `foreign_sell_idr`); pass `foreign=true` to rank by `foreign_net_idr` instead, i.e. the top foreign buyers and sellers of the stock. Useful for spotting institutional accumulation or distribution patterns on a specific stock.

> 💡 **Note**: IDX symbol: 4 letters, optionally followed by `.jk` (case-insensitive). E.g. `BBCA`, `GOTO`.

> 💡 **Note**: The `origin` filter uses the broker's registry classification (a foreign- or domestic-owned member), not the origin of its clients. Use the `foreign_*` fields for investor-origin flow.

> 💳 **Credits**: Costs 2 API credits.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `symbol` | `path` | `string` | Ya | `-` | IDX ticker symbol. E.g. `BBCA`, `GOTO`. |
| `start` | `query` | `string` | Tidak | `-` | Start date (YYYY-MM-DD). Default: end - 90 days. |
| `end` | `query` | `string` | Tidak | `-` | End date (YYYY-MM-DD). Default: today. |
| `cohort` | `query` | `string` | Tidak | `-` | Filter brokers by cohort (case-insensitive). Default `all`. |
| `foreign` | `query` | `boolean` | Tidak | `False` | If `true`, rank by the foreign-investor portion of each broker's flow instead of the total. Bare `?foreign` also means `true`; any value other than `true`/`false` returns 400. Default `false`. Buyers and sellers are then ranked by `foreign_net_idr`. |
| `n_brokers` | `query` | `integer` | Tidak | `-` | How many buyers and sellers to return each (default 10, max 90). |
| `origin` | `query` | `string` | Tidak | `-` | Filter brokers by origin. Default `all`. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/broker-summary/BBCA/top/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 34. Broker Registry
- **Method & Path**: `GET https://api.sectors.app/v2/brokers/`
- **Kategori**: `Indonesia (IDX)` / `Brokers`
- **Biaya Kredit**: `Costs 1 API credit.`

**Penjelasan**:
Curated registry of IDX exchange-member brokers with name, origin (foreign / domestic), cohort (retail / mixed / institutional / unknown), and license type. Use this as the authoritative source for valid broker codes when calling broker-scoped endpoints such as `/v2/broker-activity/{broker_code}/`.

> 💳 **Credits**: Costs 1 API credit.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `cohort` | `query` | `string` | Tidak | `-` | Optional filter by broker cohort (case-insensitive). |
| `origin` | `query` | `string` | Tidak | `-` | Optional filter by broker origin. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/brokers/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 35. Top Brokers Daily Ranking
- **Method & Path**: `GET https://api.sectors.app/v2/brokers/top/`
- **Kategori**: `Indonesia (IDX)` / `Brokers`
- **Biaya Kredit**: `Costs 2 API credits.`

**Penjelasan**:
Brokers ranked by gross trade value (default) or absolute net flow for a single date. Optionally filter by `origin` (foreign/domestic) and `cohort` (retail/mixed/institutional/unknown). Returns all matching brokers if `n_brokers` is omitted. Each row also reports the portion of the broker's turnover executed for foreign investors (`foreign_gross`, `foreign_net`); pass `foreign=true` to rank by those instead of the totals.

> 💡 **Note**: Origin and cohort classifications come from the broker registry and describe the broker itself (a foreign- or domestic-owned member), not its clients. Use the `foreign_*` fields for investor-origin flow. Retrieve the full list with these classifications from the [Broker Registry](https://docs.sectors.app/api-references/v2/indonesia/brokers/broker-registry) endpoint.

> 💳 **Credits**: Costs 2 API credits.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `cohort` | `query` | `string` | Tidak | `-` | Filter by broker cohort (case-insensitive). Default `all`. |
| `date` | `query` | `string` | Tidak | `-` | Target date (YYYY-MM-DD). Default: latest available. |
| `foreign` | `query` | `boolean` | Tidak | `False` | If `true`, rank by the foreign-investor portion of each broker's flow instead of the total. Bare `?foreign` also means `true`; any value other than `true`/`false` returns 400. Default `false`. With `metric=gross` ranks by `foreign_gross`; with `metric=net` by absolute `foreign_net`. |
| `metric` | `query` | `string` | Tidak | `-` | `gross` ranks by total buy + sell value; `net` ranks by absolute net flow. Default `gross`. |
| `n_brokers` | `query` | `integer` | Tidak | `-` | How many brokers to return. Default: all matching (~88 total). Max 90. |
| `origin` | `query` | `string` | Tidak | `-` | Filter by broker origin. Default `all`. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/brokers/top/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 36. Daily Full-Universe Foreign Flow
- **Method & Path**: `GET https://api.sectors.app/v2/foreign-flow/`
- **Kategori**: `Indonesia (IDX)` / `Brokers`
- **Biaya Kredit**: `Costs 1 API credit per page. The full universe (typically 550-700 tickers with foreign activity on the day) is about 20-25 pages at the maximum `limit` of 30.`

**Penjelasan**:
Returns the net foreign-investor flow (IDR) of **every** IDX ticker on a single trading day, in one paginated feed — instead of calling the per-symbol [Daily Net Foreign Inflow](https://docs.sectors.app/api-references/v2/indonesia/brokers/foreign-flow-by-symbol) endpoint once per ticker. Sorted by `net_foreign_inflow` descending by default, so the first page is the day's top foreign buys; `order_by=net_foreign_inflow` puts the top foreign sells first.

> 💡 **Note**: Defaults to the most recent trading day. Pass `date` (`YYYY-MM-DD`) to pull a specific day. Future dates return 400.

> 💡 **Note**: Flow is attributed by the investor's origin, not the broker's. Tickers with no foreign-investor participation on the day are omitted.

> 💳 **Credits**: Costs 1 API credit per page. The full universe (typically 550-700 tickers with foreign activity on the day) is about 20-25 pages at the maximum `limit` of 30.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `order_by` | `query` | `string` | Tidak | `-net_foreign_inflow` | Sort field; prefix with `-` for descending. Default `-net_foreign_inflow` (top foreign buys first). |
| `limit` | `query` | `integer` | Tidak | `20` | Maximum number of tickers to return per page. Max: 30. |
| `offset` | `query` | `integer` | Tidak | `0` | Number of tickers to skip for pagination. |
| `date` | `query` | `string` | Tidak | `-` | Trading day to pull, in `YYYY-MM-DD` format. Defaults to the most recent trading day with data. Future dates return 400. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/foreign-flow/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 37. Daily Net Foreign Inflow
- **Method & Path**: `GET https://api.sectors.app/v2/foreign-flow/{symbol}/`
- **Kategori**: `Indonesia (IDX)` / `Brokers`
- **Biaya Kredit**: `Costs 1 API credit.`

**Penjelasan**:
Daily net foreign-investor inflow (IDR) for one IDX ticker over a date range up to 90 days. Positive `net_foreign_inflow` means foreign investors were net buyers that day; negative means they were net sellers. `foreign_share` is the foreign fraction of the stock's two-sided turnover. Usually useful for tracking foreign sentiment and capital flow on a specific stock.

> 💡 **Note**: Pass `IHSG` (any case, with or without `.JK`) for the market-wide series: every ticker summed, one point per day, `symbol` echoed as `IHSG`. For every ticker's flow on one day use the [Daily Full-Universe Foreign Flow](https://docs.sectors.app/api-references/v2/indonesia/brokers/foreign-flow) endpoint.

> 💡 **Note**: Flow is attributed by the investor's origin, not the broker's. Every broker's daily activity on the stock is split into its foreign-investor and domestic-investor portions, and this endpoint sums the foreign portion across all brokers, so a foreign-owned broker's domestic clients count as domestic and a local broker's foreign clients count as foreign.

> 💡 **Note**: IDX symbol: 4 letters, optionally followed by `.jk` (case-insensitive). E.g. `BBCA`, `GOTO`.

> 💡 **Note**: Only foreign flow is returned because the exchange is a closed market: for any `(symbol, date)`, foreign and domestic net values always sum to zero, so domestic flow is simply `-net_foreign_inflow`.

> 💳 **Credits**: Costs 1 API credit.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `symbol` | `path` | `string` | Ya | `-` | IDX ticker symbol. E.g. `BBCA`, `GOTO`. |
| `start` | `query` | `string` | Tidak | `-` | Start date (YYYY-MM-DD). Default: end - 90 days. |
| `end` | `query` | `string` | Tidak | `-` | End date (YYYY-MM-DD). Default: today. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/foreign-flow/BBCA/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

# Singapore (SGX)

## Sub-Kategori: SGX - Company Screener

### 38. SGX Companies Screener
- **Method & Path**: `GET https://api.sectors.app/v2/sgx/companies/`
- **Kategori**: `Singapore (SGX)` / `SGX - Company Screener`
- **Biaya Kredit**: `Costs 1 API credit for structured queries. Using the natural-language `?q=` parameter costs 3 API credits.`

**Penjelasan**:
High-performance API for filtering and sorting SGX-listed companies. Supports both structured SQL-like queries (`where`, `order_by`) and natural language queries (`q`). Returns a paginated list of companies.

**Query modes** (mutually exclusive — `q` overrides all others):
- `q`: Natural language, e.g. `top 5 SGX banks by market cap`
- `where` + `order_by`: SQL-like structured query

> 💡 **Note**: SGX symbol: 3-4 characters (letters or digits), optional `.SI` suffix on input. E.g. `D05`, `U11`, `Z74`, `TCPD`. Output always carries the `.SI` suffix.

> 💡 **Note**: SGX sector column contains duplicate variants (e.g. `Consumer Cyclical` / `Consumer Cyclicals`, `Financial Services` / `Financials`, `Real Estate` / `Properties & Real Estate` / `REIT`) pending upstream cleanup. To capture all matching companies, query with `OR` (e.g. `sector = 'Real Estate' OR sector = 'Properties & Real Estate' OR sector = 'REIT'`).


To account for reporting lags, 'latest year' queries made between January and April default to the previous audited year (e.g. a query in early 2026 uses 2024 data).



**Operators:** `=`, `!=`, `>`, `>=`, `<`, `<=`, `like`, `in`

**Logic:** combine conditions with `and` and `or`

**String values:** use single or double quotes — `sector = 'Technology'`

**Lists (for `in`):** `tags in ['blue-chip', 'dividend']`



Access historical data using bracket notation: `field[YYYY]`

Examples: `revenue[2023] > 1000000000` or `total_yield[2024] > 0.05`

**Note:** SGX data is annual only — there is no quarterly data.



Perform calculations within your query on both sides of a condition.

Examples: `earnings[2024] > earnings[2023] * 1.25` or `revenue[2024] / revenue[2023] > 1.5`



Some IDX screener features are **not available** for SGX due to data scope:

- **No person / entity ownership queries** — no `executives`, `major_shareholders`, or `affiliates` fields.
- **No peer averages** — no `pe_peer_avg`, `pb_peer_avg`, etc.
- **No `free_float` field**.
- **No quarterly data** — only annual fields like `revenue[2024]`.
- **Coverage caveats**: yearly fields marked `[Big caps only]` are populated only for ~22 large-caps; fields marked `[Banks only]` are populated only for DBS / OCBC / UOB.






**How to Use:** Query these fields directly using standard operators (`=`, `!=`, `>`, `<`, `LIKE`, `IN`). String comparisons are case-insensitive.


- `where=market_cap > 500000000000000`
- `where=company_name like '%energi%'`
- `where=sector = 'Financials' and listing_date > '2005-01-01'`


- **symbol**: SGX ticker symbol (3-4 characters, e.g. `D05`, `U11`, `Z74`, `TCPD`; accepts optional `.SI` suffix on input, always returned with it)
- **company_name**: Full registered company name
- **sector**: SGX sector classification. NB: source data contains duplicate labels (e.g. `Consumer Cyclical` vs `Consumer Cyclicals`, `Financial Services` vs `Financials`) — pending upstream cleanup.
- **sub_sector**: SGX sub-sector classification (126 distinct values)
- **market_cap**: Market capitalisation in SGD
- **volume**: Recent average daily trading volume (shares)
- **last_close_price**: Most recent close price in SGD
- **employee_num**: Total number of employees
- **pe**: Price-to-earnings ratio
- **eps**: Earnings per share (SGD)
- **beta**: Beta vs SGX market
- **ps**: Price-to-sales ratio
- **pcf**: Price-to-cash-flow ratio
- **pb**: Price-to-book ratio
- **gross_margin**: Gross profit margin (decimal, e.g. 0.45 = 45%)
- **operating_margin**: Operating profit margin (decimal)
- **net_profit_margin**: Net profit margin (decimal)
- **quick_ratio**: Quick ratio (acid test)
- **current_ratio**: Current ratio
- **debt_to_equity**: Debt-to-equity ratio
- **one_year_eps_growth**: 1-year EPS growth (decimal)
- **one_year_sales_growth**: 1-year sales (revenue) growth (decimal)
- **forward_dividend**: Forward annual dividend per share in SGD
- **forward_dividend_yield**: Forward annual dividend yield (decimal)
- **dividend_ttm**: Trailing-twelve-month dividend per share in SGD
- **dividend_yield_5y_avg**: 5-year average dividend yield (decimal)
- **dividend_growth_rate**: Year-over-year dividend growth rate (decimal)
- **payout_ratio**: Dividend payout ratio (decimal)
- **change_1d**: 1-day price change (decimal)
- **change_7d**: 7-day price change (decimal)
- **change_1m**: 1-month price change (decimal)
- **change_ytd**: Year-to-date price change (decimal)
- **change_1y**: 1-year price change (decimal)
- **change_3y**: 3-year price change (decimal)



**How to Use:** Query using the `in` operator to check if any of the provided values exist in the array.


- `where=indices in ['LQ45', 'IDX30']`
- `where=tags in ['52-w-high', 'public-float-under-25']`


- **tags**: Analyst sentiment / classification tags



**How to Use:** Query as if they were direct fields — the parser automatically extracts the value from the underlying JSON.


- `where=pe_ttm < 15 and roe_ttm > 0.1`
- `where=last_close_price < all_time_high_price`
- `where=ytd_low_date > '2025-03-01'`


- **ytd_low_price**: Year-to-date lowest closing price in SGD
- **ytd_low_date**: Date of the year-to-date lowest closing price
- **ytd_high_price**: Year-to-date highest closing price in SGD
- **ytd_high_date**: Date of the year-to-date highest closing price
- **52_w_low_price**: 52-week lowest closing price in SGD
- **52_w_low_date**: Date of the 52-week lowest closing price
- **52_w_high_price**: 52-week highest closing price in SGD
- **52_w_high_date**: Date of the 52-week highest closing price
- **90_d_low_price**: 90-day lowest closing price in SGD
- **90_d_low_date**: Date of the 90-day lowest closing price
- **90_d_high_price**: 90-day highest closing price in SGD
- **90_d_high_date**: Date of the 90-day highest closing price
- **all_time_low_price**: All-time lowest closing price in SGD
- **all_time_low_date**: Date of the all-time lowest closing price
- **all_time_high_price**: All-time highest closing price in SGD
- **all_time_high_date**: Date of the all-time highest closing price



**How to Use:** Must use bracket notation `field[YYYY]` to access data for a specific year. Supports all numeric operators, field-to-field comparisons, and arithmetic expressions.


- `where=revenue[2023] > earnings[2023] * 5`
- `where=roe[2023] > 0.15 and roe[2022] > 0.15`
- `where=pe[2024] < pe_peer_avg[2024]`


- **revenue**: Annual revenue in SGD. Use: `revenue[2024]`.
- **earnings**: Annual net profit/loss in SGD. Use: `earnings[2024]`.
- **total_dividend**: Total dividends paid per share for the year (SGD). Use: `total_dividend[2024]`.
- **total_yield**: Total dividend yield for the year (decimal). Use: `total_yield[2024]`.
- **operating_cash_flow**: Operating cash flow in SGD. Use: `operating_cash_flow[2024]`. _(coverage: Big caps only)_
- **investing_cash_flow**: Investing cash flow in SGD. Use: `investing_cash_flow[2024]`. _(coverage: Big caps only)_
- **financing_cash_flow**: Financing cash flow in SGD. Use: `financing_cash_flow[2024]`. _(coverage: Big caps only)_
- **free_cash_flow**: Free cash flow in SGD. Use: `free_cash_flow[2024]`. _(coverage: Big caps only)_
- **net_cash_flow**: Net cash flow in SGD. Use: `net_cash_flow[2024]`. _(coverage: Big caps only)_
- **capital_expenditure**: Capital expenditure in SGD. Use: `capital_expenditure[2024]`. _(coverage: Big caps only)_
- **ebit**: EBIT (earnings before interest and tax) in SGD. Use: `ebit[2024]`. _(coverage: Big caps only)_
- **ebitda**: EBITDA in SGD. Use: `ebitda[2024]`. _(coverage: Big caps only)_
- **gross_income**: Gross income in SGD. Use: `gross_income[2024]`. _(coverage: Big caps only)_
- **cost_of_revenue**: Cost of revenue in SGD. Use: `cost_of_revenue[2024]`. _(coverage: Big caps only)_
- **operating_income**: Operating income in SGD. Use: `operating_income[2024]`. _(coverage: Big caps only)_
- **operating_expense**: Operating expense in SGD. Use: `operating_expense[2024]`. _(coverage: Big caps only)_
- **pretax_income**: Pre-tax income in SGD. Use: `pretax_income[2024]`. _(coverage: Big caps only)_
- **income_taxes**: Income taxes paid in SGD. Use: `income_taxes[2024]`. _(coverage: Big caps only)_
- **total_asset**: Total assets in SGD. Use: `total_asset[2024]`. _(coverage: Big caps only)_
- **total_equity**: Total equity in SGD. Use: `total_equity[2024]`. _(coverage: Big caps only)_
- **total_liabilities**: Total liabilities in SGD. Use: `total_liabilities[2024]`. _(coverage: Big caps only)_
- **working_capital**: Working capital in SGD. Use: `working_capital[2024]`. _(coverage: Big caps only)_
- **total_current_asset**: Total current assets in SGD. Use: `total_current_asset[2024]`. _(coverage: Big caps only)_
- **total_non_current_asset**: Total non-current assets in SGD. Use: `total_non_current_asset[2024]`. _(coverage: Big caps only)_
- **net_interest_income**: Net interest income in SGD. Use: `net_interest_income[2024]`. _(coverage: Banks only)_
- **interest_income**: Total interest income in SGD. Use: `interest_income[2024]`. _(coverage: Banks only)_
- **interest_expense**: Total interest expense in SGD. Use: `interest_expense[2024]`. _(coverage: Banks only)_
- **net_fee_and_commission_income**: Net fee and commission income in SGD. Use: `net_fee_and_commission_income[2024]`. _(coverage: Banks only)_
- **net_trading_income**: Net trading income in SGD. Use: `net_trading_income[2024]`. _(coverage: Banks only)_
- **net_loan**: Net loans outstanding in SGD. Use: `net_loan[2024]`. _(coverage: Banks only)_
- **gross_loan**: Gross loans outstanding in SGD. Use: `gross_loan[2024]`. _(coverage: Banks only)_
- **total_deposit**: Total customer deposits in SGD. Use: `total_deposit[2024]`. _(coverage: Banks only)_
- **core_capital_tier1**: Core capital (Tier 1) in SGD. Use: `core_capital_tier1[2024]`. _(coverage: Banks only)_
- **total_risk_weighted_asset**: Total risk-weighted assets in SGD. Use: `total_risk_weighted_asset[2024]`. _(coverage: Banks only)_



**How to Use:** Must use bracket notation `field[Qi-YYYY]` to access data for a specific quarter.


- `where=revenue_q[Q1-2024] > 1000000000`
- `where=earnings_q[Q4-2023] > earnings_q[Q3-2023]`






**How to Use:** The query checks if **any** object in the list matches the condition. Use `=` or `like` for strings, numeric operators for numbers.


- `where=major_shareholders_name like 'PT%' and major_shareholders_share_percentage > 0.1`
- `where=key_executives_name = 'Prajogo Pangestu'`








> 💳 **Credits**: Costs 1 API credit for structured queries. Using the natural-language `?q=` parameter costs 3 API credits.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `where` | `query` | `string` | Tidak | `-` | SQL-like conditions for advanced filtering. Ignored if `q` is present. Supports operators `=`, `!=`, `>`, `>=`, `<`, `<=`, `like`, `in` combined with `and`/`or`. Use bracket notation for yearly fields: `revenue[2024] > 1000000000`. Supports arithmetic on both sides: `earnings[2024] / earnings[2023] > 1.25`. |
| `q` | `query` | `string` | Tidak | `-` | A natural language query (e.g. `top 5 SGX banks by market cap`). When `q` is provided, all other query parameters (`where`, `order_by`, etc.) are ignored as the LLM will generate them. |
| `order_by` | `query` | `string` | Tidak | `symbol` | Field to sort results by. Use `-` prefix for descending order (e.g. `-market_cap`). Supports arithmetic expressions (e.g. `-(earnings[2024]/earnings[2023])`). Ignored if `q` is present. |
| `desc` | `query` | `boolean` | Tidak | `False` | Sort in descending order. Ignored if `q` is present. |
| `limit` | `query` | `integer` | Tidak | `50` | Maximum number of results to return. Max: 200. Ignored if `q` is present. |
| `offset` | `query` | `integer` | Tidak | `0` | Number of results to skip for pagination. Ignored if `q` is present. |
| `include_query_values` | `query` | `boolean` | Tidak | `False` | If `true`, the response includes a `query_values` object showing the field values used in filtering/sorting. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/sgx/companies/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

## Sub-Kategori: SGX - Helper Lists

### 39. List all SGX sectors
- **Method & Path**: `GET https://api.sectors.app/v2/sgx/sectors/`
- **Kategori**: `Singapore (SGX)` / `SGX - Helper Lists`
- **Biaya Kredit**: `Costs 1 API credit.`

**Penjelasan**:
Returns all available SGX sector slugs as a flat array.

**Used by:** [SGX Companies](https://docs.sectors.app/api-references/v2/singapore/screener/sgx-companies), [SGX Top Companies](https://docs.sectors.app/api-references/v2/singapore/ranking/top-companies)

> 💳 **Credits**: Costs 1 API credit.

*Endpoint ini tidak membutuhkan parameter input query atau path.*

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/sgx/sectors/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 40. SGX Subsectors
- **Method & Path**: `GET https://api.sectors.app/v2/sgx/subsectors/`
- **Kategori**: `Singapore (SGX)` / `SGX - Helper Lists`
- **Biaya Kredit**: `Costs 1 API credit.`

**Penjelasan**:
Returns all available SGX sector/subsector pairs as kebab-case slugs. Use these values as inputs to `sector` and `sub_sector` parameters.

**Used by:** [SGX Companies](https://docs.sectors.app/api-references/v2/singapore/screener/sgx-companies)

> 💳 **Credits**: Costs 1 API credit.

*Endpoint ini tidak membutuhkan parameter input query atau path.*

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/sgx/subsectors/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 41. SGX News Tags
- **Method & Path**: `GET https://api.sectors.app/v2/sgx/tags/`
- **Kategori**: `Singapore (SGX)` / `SGX - Helper Lists`
- **Biaya Kredit**: `Costs 1 API credit.`

**Penjelasan**:
Returns the complete list of distinct tag slugs found across all SGX news articles. Use these values with the `tags` parameter of the [SGX News](https://docs.sectors.app/api-references/v2/singapore/news/sgx-news) endpoint.

> 💳 **Credits**: Costs 1 API credit.

*Endpoint ini tidak membutuhkan parameter input query atau path.*

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/sgx/tags/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

## Sub-Kategori: SGX - Detailed Reports

### 42. Full company report for an SGX-listed symbol
- **Method & Path**: `GET https://api.sectors.app/v2/sgx/company/report/`
- **Kategori**: `Singapore (SGX)` / `SGX - Detailed Reports`
- **Biaya Kredit**: `Costs 1 API credit per requested section. Default behavior (all 4 sections) consumes 4 credits.`

**Penjelasan**:
> 💡 **Note**: SGX symbol: 3-4 characters (letters or digits), optionally followed by `.SI` (case-insensitive) on input. E.g. `D05`, `U11`, `Z74`. Output always carries the `.SI` suffix.

Returns a comprehensive company report organized into distinct sections. Use `sections` to fetch only the data you need and reduce response size.


- **overview**: Market cap, volume, sector, sub-sector, price changes (1d/7d/1m/1y/3y/ytd), all-time price highs/lows
- **valuation**: PE, PS, PCF, PB ratios
- **financials**: Historical revenue and earnings by year, EPS, margins, ratios
- **dividend**: Dividend yield, growth rate, payout ratio, historical dividends


> 💳 **Credits**: Costs 1 API credit per requested section. Default behavior (all 4 sections) consumes 4 credits.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `symbol` | `path` | `string` | Ya | `-` | SGX symbol symbol. E.g. `D05`, `U11`, `Z74`. |
| `sections` | `query` | `array` | Tidak | `-` | Comma-separated sections to include. Options: `overview`, `valuation`, `financials`, `dividend`. Default: all sections. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/sgx/company/report/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 43. Full company report for an SGX-listed symbol
- **Method & Path**: `GET https://api.sectors.app/v2/sgx/company/report/{symbol}/`
- **Kategori**: `Singapore (SGX)` / `SGX - Detailed Reports`
- **Biaya Kredit**: `Costs 1 API credit per requested section. Default behavior (all 4 sections) consumes 4 credits.`

**Penjelasan**:
> 💡 **Note**: SGX symbol: 3-4 characters (letters or digits), optionally followed by `.SI` (case-insensitive) on input. E.g. `D05`, `U11`, `Z74`. Output always carries the `.SI` suffix.

Returns a comprehensive company report organized into distinct sections. Use `sections` to fetch only the data you need and reduce response size.


- **overview**: Market cap, volume, sector, sub-sector, price changes (1d/7d/1m/1y/3y/ytd), all-time price highs/lows
- **valuation**: PE, PS, PCF, PB ratios
- **financials**: Historical revenue and earnings by year, EPS, margins, ratios
- **dividend**: Dividend yield, growth rate, payout ratio, historical dividends


> 💳 **Credits**: Costs 1 API credit per requested section. Default behavior (all 4 sections) consumes 4 credits.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `symbol` | `path` | `string` | Ya | `-` | SGX symbol symbol. E.g. `D05`, `U11`, `Z74`. |
| `sections` | `query` | `array` | Tidak | `-` | Comma-separated sections to include. Options: `overview`, `valuation`, `financials`, `dividend`. Default: all sections. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/sgx/company/report/BBCA/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

## Sub-Kategori: SGX - Transaction Data

### 44. SGX Share Buybacks
- **Method & Path**: `GET https://api.sectors.app/v2/sgx/buybacks/`
- **Kategori**: `Singapore (SGX)` / `SGX - Transaction Data`
- **Biaya Kredit**: `Costs 1 API credit.`

**Penjelasan**:
Returns SGX share buyback records. Each row includes the purchase date, buyback type, price range, total value, total shares purchased, treasury shares after purchase, and mandate details.

> 💡 **Note**: SGX symbol: 3-4 characters (letters or digits). E.g. `D05`, `U11`, `Z74`, `TCPD`. Output always carries the `.SI` suffix.

> 💡 **Note**: Date filters: both `start` and `end` are independent and optional — omit either side to leave that bound unconstrained. Future `end` dates return 400.

> 💳 **Credits**: Costs 1 API credit.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `symbol` | `query` | `string` | Tidak | `-` | SGX symbol to filter by. E.g. `D05`, `U11`. |
| `start` | `query` | `string` | Tidak | `-` | Start date in `YYYY-MM-DD` format. Optional; if omitted, no lower bound is applied. Filters on `purchase_date`. |
| `end` | `query` | `string` | Tidak | `-` | End date in `YYYY-MM-DD` format. Optional; if omitted, no upper bound is applied. Future dates return 400. |
| `limit` | `query` | `integer` | Tidak | `20` | Items per page. Max 30. |
| `offset` | `query` | `integer` | Tidak | `0` | Number of items to skip. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/sgx/buybacks/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 45. SGX Daily Full-Universe Close
- **Method & Path**: `GET https://api.sectors.app/v2/sgx/close/`
- **Kategori**: `Singapore (SGX)` / `SGX - Transaction Data`
- **Biaya Kredit**: `Costs 1 API credit per page. The full universe (roughly 560-600 tickers) is about 20 pages at the maximum `limit` of 30 (~20 credits per full pull).`

**Penjelasan**:
Returns the daily closing price for **every** SGX ticker on a single trading day, in one paginated feed — instead of calling the per-symbol [SGX Daily Price Data](https://docs.sectors.app/api-references/v2/singapore/transaction/daily) endpoint once per ticker.

> 💡 **Note**: Defaults to the most recent trading day. Pass `date` (`YYYY-MM-DD`) to pull a specific day. Future dates return 400.

> 💡 **Note**: Tickers with no recorded close for the requested day are omitted. Output symbols always carry the `.SI` suffix; prices are in SGD.

> 💳 **Credits**: Costs 1 API credit per page. The full universe (roughly 560-600 tickers) is about 20 pages at the maximum `limit` of 30 (~20 credits per full pull).

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `limit` | `query` | `integer` | Tidak | `20` | Maximum number of tickers to return per page. Max: 30. |
| `offset` | `query` | `integer` | Tidak | `0` | Number of tickers to skip for pagination. |
| `date` | `query` | `string` | Tidak | `-` | Trading day to pull, in `YYYY-MM-DD` format. Defaults to the most recent trading day with data. Future dates return 400. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/sgx/close/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 46. SGX Daily Price Data
- **Method & Path**: `GET https://api.sectors.app/v2/sgx/daily/{symbol}/`
- **Kategori**: `Singapore (SGX)` / `SGX - Transaction Data`
- **Biaya Kredit**: `Costs 1 API credit.`

**Penjelasan**:
Returns daily close price and volume for a given SGX-listed company over a date range of up to 90 days.

> 💡 **Note**: SGX symbol: 3-4 characters (letters or digits). E.g. `D05`, `U11`, `Z74`, `TCPD`. Output always carries the `.SI` suffix.

> 💡 **Note**: Date range: defaults to last 30 days. Max window 90 days; wider ranges are clamped to the most recent 90 days ending at `end`. Future `end` dates return 400.

> 💳 **Credits**: Costs 1 API credit.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `symbol` | `path` | `string` | Ya | `-` | SGX symbol. E.g. `D05`, `U11`. |
| `start` | `query` | `string` | Tidak | `-` | Start date in `YYYY-MM-DD` format. Defaults to 30 days before `end`. Wider ranges are clamped to the most recent 90 days. |
| `end` | `query` | `string` | Tidak | `-` | End date in `YYYY-MM-DD` format. Defaults to today. Future dates return 400. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/sgx/daily/BBCA/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 47. SGX Short Sell
- **Method & Path**: `GET https://api.sectors.app/v2/sgx/short-sell/`
- **Kategori**: `Singapore (SGX)` / `SGX - Transaction Data`
- **Biaya Kredit**: `Costs 1 API credit.`

**Penjelasan**:
Returns SGX short sell data. Supports filtering by symbol and date range, and sorting via `order_by` (e.g. `start=2025-05-02&end=2025-05-02&order_by=-value` lists the most shorted stocks that day).

> 💡 **Note**: SGX symbol: 3-4 characters (letters or digits). E.g. `D05`, `U11`, `Z74`, `TCPD`. Output always carries the `.SI` suffix.

> 💡 **Note**: Date filters: both `start` and `end` are independent and optional — omit either side to leave that bound unconstrained. Future `end` dates return 400.

> 💳 **Credits**: Costs 1 API credit.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `symbol` | `query` | `string` | Tidak | `-` | SGX symbol to filter by. E.g. `D05`, `U11`. |
| `start` | `query` | `string` | Tidak | `-` | Start date in `YYYY-MM-DD` format. Optional; if omitted, no lower bound is applied. Filters on `date`. |
| `end` | `query` | `string` | Tidak | `-` | End date in `YYYY-MM-DD` format. Optional; if omitted, no upper bound is applied. Future dates return 400. |
| `order_by` | `query` | `string` | Tidak | `-date` | Sort field; prefix with `-` for descending. Default `-date` (newest first). |
| `limit` | `query` | `integer` | Tidak | `20` | Items per page. Max 30. |
| `offset` | `query` | `integer` | Tidak | `0` | Number of items to skip. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/sgx/short-sell/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

## Sub-Kategori: SGX - Rankings

### 48. Top SGX companies by classification
- **Method & Path**: `GET https://api.sectors.app/v2/sgx/companies/top/`
- **Kategori**: `Singapore (SGX)` / `SGX - Rankings`
- **Biaya Kredit**: `Costs 1 API credit per requested classification. Default behavior (all 5 classifications) consumes 5 credits.`

**Penjelasan**:
Returns top SGX-listed companies ranked by one or more classifications.


`dividend_yield`, `revenue`, `earnings`, `market_cap`, `pe`


> 💡 **Note**: Get valid sector slugs from the [SGX Sectors](https://docs.sectors.app/api-references/v2/singapore/helper-list/sgx-sectors) endpoint.

> 💳 **Credits**: Costs 1 API credit per requested classification. Default behavior (all 5 classifications) consumes 5 credits.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `sector` | `query` | `string` | Tidak | `-` | Filter by sector slug. E.g. `financial-services`, `technology`. Default: all sectors. |
| `n_stock` | `query` | `integer` | Tidak | `-` | Number of top companies to return per classification. Max 10. Default: 5. |
| `classifications` | `query` | `array` | Tidak | `-` | Comma-separated list of classifications. Options: `dividend_yield`, `revenue`, `earnings`, `market_cap`, `pe`. Default: all. |
| `min_mcap_million` | `query` | `integer` | Tidak | `-` | Minimum market cap in million SGD. Default: 1000. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/sgx/companies/top/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

## Sub-Kategori: SGX - News & Filings

### 49. SGX Insider Filings
- **Method & Path**: `GET https://api.sectors.app/v2/sgx/filings/`
- **Kategori**: `Singapore (SGX)` / `SGX - News & Filings`
- **Biaya Kredit**: `Costs 1 API credit.`

**Penjelasan**:
Returns SGX insider trading filings — buy/sell transactions by company insiders and major shareholders. Supports filtering by symbol, transaction type, holder type, and date range.

> 💡 **Note**: SGX symbol: 3-4 characters (letters or digits). E.g. `D05`, `U11`, `Z74`, `TCPD`. Output always carries the `.SI` suffix.

> 💡 **Note**: Date filters: both `start` and `end` are independent and optional — omit either side to leave that bound unconstrained. Future `end` dates return 400.

> 💳 **Credits**: Costs 1 API credit.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `symbol` | `query` | `string` | Tidak | `-` | SGX symbol to filter by. E.g. `D05`, `U11`. |
| `start` | `query` | `string` | Tidak | `-` | Start date in `YYYY-MM-DD` format. Optional; if omitted, no lower bound is applied. Filters on `timestamp`. |
| `end` | `query` | `string` | Tidak | `-` | End date in `YYYY-MM-DD` format. Optional; if omitted, no upper bound is applied. Future dates return 400. |
| `limit` | `query` | `integer` | Tidak | `20` | Number of results to return. Maximum: 30. |
| `offset` | `query` | `integer` | Tidak | `0` | Number of results to skip for pagination. |
| `transaction_type` | `query` | `string` | Tidak | `-` | Filter by transaction type (case-insensitive). |
| `holder_type` | `query` | `string` | Tidak | `-` | Filter by holder type (case-insensitive). |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/sgx/filings/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 50. SGX News
- **Method & Path**: `GET https://api.sectors.app/v2/sgx/news/`
- **Kategori**: `Singapore (SGX)` / `SGX - News & Filings`
- **Biaya Kredit**: `Costs 1 API credit.`

**Penjelasan**:
Returns paginated SGX news articles. Supports filtering by sector, sub-sector, tags, symbols, and date range.

> 💡 **Note**: SGX symbol: 3-4 characters (letters or digits). E.g. `D05`, `U11`, `Z74`, `TCPD`. Output always carries the `.SI` suffix.

> 💡 **Note**: Date filters: both `start` and `end` are independent and optional — omit either side to leave that bound unconstrained. Future `end` dates return 400.

> 💳 **Credits**: Costs 1 API credit.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `sector` | `query` | `string` | Tidak | `-` | Filter by sector (case-insensitive). |
| `sub_sector` | `query` | `string` | Tidak | `-` | Filter by sub-sector (case-insensitive). |
| `start` | `query` | `string` | Tidak | `-` | Start date in `YYYY-MM-DD` format. Optional; if omitted, no lower bound is applied. Filters on `timestamp`. |
| `end` | `query` | `string` | Tidak | `-` | End date in `YYYY-MM-DD` format. Optional; if omitted, no upper bound is applied. Future dates return 400. |
| `limit` | `query` | `integer` | Tidak | `20` | Items per page. Max 30. |
| `offset` | `query` | `integer` | Tidak | `0` | Number of items to skip. |
| `tags` | `query` | `string` | Tidak | `-` | Comma-separated tag slugs. Get values from [SGX Tags](https://docs.sectors.app/api-references/v2/singapore/helper-list/sgx-tags). |
| `symbols` | `query` | `string` | Tidak | `-` | Comma-separated SGX symbols. E.g. `D05,U11`. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/sgx/news/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

# Malaysia (KLSE)

## Sub-Kategori: KLSE

### 51. List KLSE companies filtered by sector
- **Method & Path**: `GET https://api.sectors.app/v2/klse/companies/`
- **Kategori**: `Malaysia (KLSE)` / `KLSE`
- **Biaya Kredit**: `Costs 1 API credit.`

**Penjelasan**:
Returns all KLSE-listed companies in a given sector as `symbol` + `company_name` pairs.

> 💡 **Note**: Get valid sector slugs from the [KLSE Sectors](https://docs.sectors.app/api-references/v2/malaysia/klse-sectors) endpoint. Format: **kebab-case** (lowercase, hyphen-separated). E.g. `financials`, `healthcare`, `consumer-cyclicals`.

**Used by:** [KLSE Company Report](https://docs.sectors.app/api-references/v2/malaysia/klse-report)

> 💳 **Credits**: Costs 1 API credit.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `sector` | `query` | `string` | Ya | `-` | Kebab-case sector slug. E.g. `financials`, `healthcare`. Get valid values from the [KLSE Sectors](https://docs.sectors.app/api-references/v2/malaysia/klse-sectors) endpoint. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/klse/companies/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 52. Top KLSE companies by classification
- **Method & Path**: `GET https://api.sectors.app/v2/klse/companies/top/`
- **Kategori**: `Malaysia (KLSE)` / `KLSE`
- **Biaya Kredit**: `Costs 1 API credit per requested classification. Default behavior (all 5 classifications) consumes 5 credits.`

**Penjelasan**:
Returns top KLSE-listed companies ranked by one or more classifications.


`dividend_yield`, `revenue`, `earnings`, `market_cap`, `pe`


> 💡 **Note**: Get valid sector slugs from the [KLSE Sectors](https://docs.sectors.app/api-references/v2/malaysia/klse-sectors) endpoint.

> 💳 **Credits**: Costs 1 API credit per requested classification. Default behavior (all 5 classifications) consumes 5 credits.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `sector` | `query` | `string` | Tidak | `-` | Filter by sector slug. E.g. `financials`, `healthcare`. Default: all sectors. |
| `n_stock` | `query` | `integer` | Tidak | `-` | Number of top companies to return per classification. Max 10. Default: 5. |
| `classifications` | `query` | `array` | Tidak | `-` | Comma-separated list of classifications. Options: `dividend_yield`, `revenue`, `earnings`, `market_cap`, `pe`. Default: all. |
| `min_mcap_million` | `query` | `integer` | Tidak | `-` | Minimum market cap in million MYR. Default: 1000. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/klse/companies/top/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 53. Full company report for a KLSE-listed symbol
- **Method & Path**: `GET https://api.sectors.app/v2/klse/company/report/`
- **Kategori**: `Malaysia (KLSE)` / `KLSE`
- **Biaya Kredit**: `Costs 1 API credit per requested section. Default behavior (all 4 sections) consumes 4 credits.`

**Penjelasan**:
> 💡 **Note**: KLSE symbol: 4-digit numeric code. E.g. `1155`, `4197`, `5225`.

Returns a comprehensive company report organized into distinct sections. Use `sections` to fetch only the data you need and reduce response size.


- **overview**: Market cap, volume, sector, sub-sector, price changes (1d/7d)
- **valuation**: PE, PB, PS, PCF ratios (TTM and historical)
- **financials**: Historical revenue and earnings by year, EPS, margins, ratios
- **dividend**: Dividend history and yield


> 💳 **Credits**: Costs 1 API credit per requested section. Default behavior (all 4 sections) consumes 4 credits.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `symbol` | `path` | `string` | Ya | `-` | KLSE symbol symbol (4-digit numeric code). E.g. `1155`, `4197`. |
| `sections` | `query` | `array` | Tidak | `-` | Comma-separated sections to include. Options: `overview`, `valuation`, `financials`, `dividend`. Default: all sections. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/klse/company/report/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 54. Full company report for a KLSE-listed symbol
- **Method & Path**: `GET https://api.sectors.app/v2/klse/company/report/{symbol}/`
- **Kategori**: `Malaysia (KLSE)` / `KLSE`
- **Biaya Kredit**: `Costs 1 API credit per requested section. Default behavior (all 4 sections) consumes 4 credits.`

**Penjelasan**:
> 💡 **Note**: KLSE symbol: 4-digit numeric code. E.g. `1155`, `4197`, `5225`.

Returns a comprehensive company report organized into distinct sections. Use `sections` to fetch only the data you need and reduce response size.


- **overview**: Market cap, volume, sector, sub-sector, price changes (1d/7d)
- **valuation**: PE, PB, PS, PCF ratios (TTM and historical)
- **financials**: Historical revenue and earnings by year, EPS, margins, ratios
- **dividend**: Dividend history and yield


> 💳 **Credits**: Costs 1 API credit per requested section. Default behavior (all 4 sections) consumes 4 credits.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `symbol` | `path` | `string` | Ya | `-` | KLSE symbol symbol (4-digit numeric code). E.g. `1155`, `4197`. |
| `sections` | `query` | `array` | Tidak | `-` | Comma-separated sections to include. Options: `overview`, `valuation`, `financials`, `dividend`. Default: all sections. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/klse/company/report/BBCA/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 55. List all KLSE sectors
- **Method & Path**: `GET https://api.sectors.app/v2/klse/sectors/`
- **Kategori**: `Malaysia (KLSE)` / `KLSE`
- **Biaya Kredit**: `Costs 1 API credit.`

**Penjelasan**:
Returns all available KLSE sector slugs as a flat array.

**Used by:** [KLSE Companies](https://docs.sectors.app/api-references/v2/malaysia/klse-companies), [KLSE Top Companies](https://docs.sectors.app/api-references/v2/malaysia/klse-top-companies)

> 💳 **Credits**: Costs 1 API credit.

*Endpoint ini tidak membutuhkan parameter input query atau path.*

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/klse/sectors/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

# Mining (Extension)

## Sub-Kategori: Companies

### 56. List Mining Companies
- **Method & Path**: `GET https://api.sectors.app/v2/mining/companies/`
- **Kategori**: `Mining (Extension)` / `Companies`
- **Biaya Kredit**: `Costs 1 API credit.`

**Penjelasan**:
Searches for Indonesian mining companies by name, symbol, slug, or key operation. Supports filtering by commodity type and company type.

> 💳 **Credits**: Costs 1 API credit.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `commodity_type` | `query` | `string` | Tidak | `-` | Filter by commodity. E.g. `Coal`, `Nickel`, `Gold`. |
| `limit` | `query` | `integer` | Tidak | `20` | Results per page. Default 20. |
| `offset` | `query` | `integer` | Tidak | `0` | Items to skip for pagination. |
| `keyword` | `query` | `string` | Tidak | `-` | Search across company name, IDX symbol, slug, and key operations (case-insensitive). |
| `company_type` | `query` | `string` | Tidak | `-` | Filter by company type. |
| `has_financials` | `query` | `boolean` | Tidak | `-` | If `true`, return only companies with financial data available. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/mining/companies/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 57. Mining Company Financials
- **Method & Path**: `GET https://api.sectors.app/v2/mining/companies/financials/{slug}/`
- **Kategori**: `Mining (Extension)` / `Companies`
- **Biaya Kredit**: `Costs 1 API credit.`

**Penjelasan**:
Returns annual financial records (assets, revenue, profit with breakdowns) for a mining company. All monetary values are in USD millions. Defaults to the latest available year.

> 💳 **Credits**: Costs 1 API credit.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `slug` | `path` | `string` | Ya | `-` | Company slug. |
| `year` | `query` | `integer` | Tidak | `-` | Year to retrieve. Defaults to the latest available year. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/mining/companies/financials/pt-vale-indonesia-tbk/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 58. Mining Company Ownership
- **Method & Path**: `GET https://api.sectors.app/v2/mining/companies/ownership/{slug}/`
- **Kategori**: `Mining (Extension)` / `Companies`
- **Biaya Kredit**: `Costs 1 API credit.`

**Penjelasan**:
Returns the corporate ownership tree for a mining company — showing parent companies (who owns it) and subsidiaries (what it owns) with percentage stakes.

> 💳 **Credits**: Costs 1 API credit.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `slug` | `path` | `string` | Ya | `-` | Company slug. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/mining/companies/ownership/pt-vale-indonesia-tbk/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 59. Mining Company Performance
- **Method & Path**: `GET https://api.sectors.app/v2/mining/companies/performance/{slug}/`
- **Kategori**: `Mining (Extension)` / `Companies`
- **Biaya Kredit**: `Costs 1 API credit.`

**Penjelasan**:
Returns production volume, sales volume, strip ratio, and resources/reserves data for a mining company for a given year. Defaults to the latest available year.

> 💳 **Credits**: Costs 1 API credit.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `slug` | `path` | `string` | Ya | `-` | Company slug. |
| `commodity_type` | `query` | `string` | Tidak | `-` | Filter by commodity. E.g. `Coal`, `Nickel`. Case-insensitive. |
| `year` | `query` | `integer` | Tidak | `-` | Year to retrieve. Defaults to the latest available year. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/mining/companies/performance/pt-vale-indonesia-tbk/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 60. Mining Company Detail
- **Method & Path**: `GET https://api.sectors.app/v2/mining/companies/{slug}/`
- **Kategori**: `Mining (Extension)` / `Companies`
- **Biaya Kredit**: `Costs 1 API credit.`

**Penjelasan**:
Returns comprehensive operational details for a single mining company including activities, commodity types, licenses, contracts, and site count.

> 💳 **Credits**: Costs 1 API credit.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `slug` | `path` | `string` | Ya | `-` | Company slug. Get valid slugs from the [Mining Companies List](https://docs.sectors.app/api-references/v2/mining/companies/mining-companies) endpoint. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/mining/companies/pt-vale-indonesia-tbk/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

## Sub-Kategori: Commodities & Trade

### 61. List Commodities
- **Method & Path**: `GET https://api.sectors.app/v2/mining/commodities/`
- **Kategori**: `Mining (Extension)` / `Commodities & Trade`
- **Biaya Kredit**: `Costs 1 API credit.`

**Penjelasan**:
Lists all commodities available in the price database with coverage metadata. Use this as a discovery endpoint before querying [Commodity Price History](https://docs.sectors.app/api-references/v2/mining/commodities-trade/commodity-price) endpoint.

> 💡 **Note**: 
Most commodities only have data in the price table. Cross-table data (production, exports, reserves, sites) is limited to: **Coal**, **Gold**, **Nickel**, **Copper** — and partially Silver, Cobalt, Bauxite.


> 💳 **Credits**: Costs 1 API credit.

*Endpoint ini tidak membutuhkan parameter input query atau path.*

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/mining/commodities/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 62. Commodity Price History
- **Method & Path**: `GET https://api.sectors.app/v2/mining/commodities/{commodity_name}/price/`
- **Kategori**: `Mining (Extension)` / `Commodities & Trade`
- **Biaya Kredit**: `Costs 1 API credit.`

**Penjelasan**:
Retrieves historical price data for a commodity by year range. Data is monthly (bi-weekly for recent Coal entries). Maximum range: 3 years.

> 💡 **Note**: Use [List Commodities](https://docs.sectors.app/api-references/v2/mining/commodities-trade/commodities) to discover all available commodity names.

> ⚠️ **Warning**: Requesting more than 3 years will return a 400 error.

> 💳 **Credits**: Costs 1 API credit.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `commodity_name` | `path` | `string` | Ya | `-` | The commodity name (e.g., `Gold`, `Coal`). Get valid names from the [List Commodities](https://docs.sectors.app/api-references/v2/mining/commodities-trade/commodities) endpoint. |
| `start_year` | `query` | `integer` | Tidak | `-` | Start year (e.g., `2022`). Defaults to current year − 2. |
| `end_year` | `query` | `integer` | Tidak | `-` | End year inclusive (e.g., `2024`). Defaults to current year. Maximum 3-year range from `start_year`. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/mining/commodities/coal/price/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 63. Top Export Destinations
- **Method & Path**: `GET https://api.sectors.app/v2/mining/exports/`
- **Kategori**: `Mining (Extension)` / `Commodities & Trade`
- **Biaya Kredit**: `Costs 1 API credit.`

**Penjelasan**:
Ranks countries by total export value for a given year and commodity, showing the top destinations for Indonesian commodity exports.

> 💡 **Note**: Available `commodity_type` values: `Gold`, `Copper`, `Coal`.

`export_usd` is in base USD. Volume unit is specified per row in `volume_unit` (typically `Mt`). Two volume sources are provided: **BPS** (Badan Pusat Statistik) and **ESDM** (Energi Sumber Daya Mineral) — values may differ due to methodology.

> 💳 **Credits**: Costs 1 API credit.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `commodity_type` | `query` | `string` | Ya | `-` | The commodity to analyze (e.g., `Gold`, `Coal`). |
| `year` | `query` | `integer` | Ya | `-` | The year to analyze export data for (e.g., `2024`). |
| `limit` | `query` | `integer` | Tidak | `20` | Number of top countries to return. Maximum: 30. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/mining/exports/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 64. Global Commodity Data
- **Method & Path**: `GET https://api.sectors.app/v2/mining/global-commodity/`
- **Kategori**: `Mining (Extension)` / `Commodities & Trade`
- **Biaya Kredit**: `Costs 1 API credit.`

**Penjelasan**:
Retrieves global commodity data including production, reserves, and trade information. At least one of `commodity_type` or `country` must be provided.

> 💡 **Note**: Available `commodity_type` values: `Coal`, `Gold`, `Nickel`, `Copper`, `Bauxite`.

> 💳 **Credits**: Costs 1 API credit.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `commodity_type` | `query` | `string` | Tidak | `-` | Filter by commodity type. Required if `country` not provided. |
| `country` | `query` | `string` | Tidak | `-` | Filter by country (exact match, e.g., `Australia`). Required if `commodity_type` not provided. |
| `limit` | `query` | `integer` | Tidak | `20` | Number of results to return. Maximum: 30. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/mining/global-commodity/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 65. Company Sales Destinations
- **Method & Path**: `GET https://api.sectors.app/v2/mining/sales-destination/{slug}/`
- **Kategori**: `Mining (Extension)` / `Commodities & Trade`
- **Biaya Kredit**: `Costs 1 API credit.`

**Penjelasan**:
Retrieves sales destination breakdown for a specific mining company by its slug, showing revenue and volume distribution by country for a specific year. Defaults to the latest available year if none is specified.

`revenue_usd` is in base USD. Volume unit is specified per country entry in `unit` (e.g., `Mt`).

> 💳 **Credits**: Costs 1 API credit.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `slug` | `path` | `string` | Ya | `-` | The company's unique identifier slug (e.g., `adaro-energy`). |
| `year` | `query` | `integer` | Tidak | `-` | The year to retrieve. Defaults to the latest available year. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/mining/sales-destination/pt-vale-indonesia-tbk/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

## Sub-Kategori: Production & Sites

### 66. Resources & Reserves Index
- **Method & Path**: `GET https://api.sectors.app/v2/mining/resources-reserves/`
- **Kategori**: `Mining (Extension)` / `Production & Sites`
- **Biaya Kredit**: `Costs 1 API credit.`

**Penjelasan**:
Discovery index showing which provinces, years, and commodities have resources and reserves data available. Use this before querying the detail endpoint to confirm data availability.

> 💡 **Note**: This index endpoint does not accept any query parameters.

Use [Resources & Reserves Detail](https://docs.sectors.app/api-references/v2/mining/sites-production/commodity-resources-reserves-detail) to retrieve actual values.

> 💳 **Credits**: Costs 1 API credit.

*Endpoint ini tidak membutuhkan parameter input query atau path.*

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/mining/resources-reserves/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 67. Resources & Reserves Detail
- **Method & Path**: `GET https://api.sectors.app/v2/mining/resources-reserves/{province}/`
- **Kategori**: `Mining (Extension)` / `Production & Sites`
- **Biaya Kredit**: `Costs 1 API credit.`

**Penjelasan**:
Returns resources and reserves data for a single province, nested by year then by commodity. Each commodity entry contains the full breakdown: `exploration_target`, `total_inventory`, `resources`, `reserves`, and `unit`.

> 💡 **Note**: Available `commodity_type` values: `Coal`, `Gold`, `Silver`, `Copper`, `Nickel`, `Cobalt`, `Tin`.

> 💳 **Credits**: Costs 1 API credit.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `province` | `path` | `string` | Ya | `-` | Exact province name (e.g., `Kalimantan Timur`). Case-insensitive. |
| `commodity_type` | `query` | `string` | Tidak | `-` | Restrict results to a specific commodity. |
| `year` | `query` | `integer` | Tidak | `-` | Restrict results to a specific year. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/mining/resources-reserves/sulawesi-tengah/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 68. Mining Sites
- **Method & Path**: `GET https://api.sectors.app/v2/mining/sites/`
- **Kategori**: `Mining (Extension)` / `Production & Sites`
- **Biaya Kredit**: `Costs 1 API credit.`

**Penjelasan**:
Lists mining sites with advanced filtering for location, commodity type, and production volume, plus sorting capabilities and detailed site information.

> 💡 **Note**: Available `commodity_type` values: `Coal`, `Gold`, `Nickel`, `Copper`.

Prefix `order_by` with `-` for descending order (e.g. `-production_volume`).

> 💳 **Credits**: Costs 1 API credit.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `province` | `query` | `string` | Tidak | `-` | Filter by exact province name (e.g., `Kalimantan Timur`). |
| `commodity_type` | `query` | `string` | Tidak | `-` | Filter by commodity type. Case-insensitive. |
| `company` | `query` | `string` | Tidak | `-` | Filter by company slug. |
| `year` | `query` | `integer` | Tidak | `-` | Filter by reporting year. |
| `order_by` | `query` | `string` | Tidak | `-` | Sort field. Prefix with `-` for descending. Default: `-year`. |
| `min_production` | `query` | `number` | Tidak | `-` | Filter for sites with `production_volume` ≥ this value. |
| `limit` | `query` | `integer` | Tidak | `20` | Number of results to return. Maximum: 30. |
| `offset` | `query` | `integer` | Tidak | `0` | Number of results to skip. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/mining/sites/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 69. Mining Site Detail
- **Method & Path**: `GET https://api.sectors.app/v2/mining/sites/{slug}/`
- **Kategori**: `Mining (Extension)` / `Production & Sites`
- **Biaya Kredit**: `Costs 1 API credit.`

**Penjelasan**:
Returns full details for a single mining site by its slug, including parsed resources/reserves and location (with latitude and longitude).

Use [Mining Sites](https://docs.sectors.app/api-references/v2/mining/sites-production/mining-sites) to discover site slugs.

> 💳 **Credits**: Costs 1 API credit.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `slug` | `path` | `string` | Ya | `-` | URL-friendly identifier for the mining site. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/mining/sites/pt-vale-indonesia-tbk/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 70. Total Commodity Production
- **Method & Path**: `GET https://api.sectors.app/v2/mining/total-production/`
- **Kategori**: `Mining (Extension)` / `Production & Sites`
- **Biaya Kredit**: `Costs 1 API credit.`

**Penjelasan**:
Returns total national production for a commodity across all years, including year-over-year percentage change. Results are ordered by year descending.

> 💡 **Note**: Available `commodity_type` values: `Coal`, `Nickel`, `Gold`, `Copper`.

> 💳 **Credits**: Costs 1 API credit.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `commodity_type` | `query` | `string` | Ya | `-` | The commodity to analyze (e.g., `Coal`). Required. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/mining/total-production/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

## Sub-Kategori: Contracts & Licenses

### 71. Mining Contracts
- **Method & Path**: `GET https://api.sectors.app/v2/mining/contracts/`
- **Kategori**: `Mining (Extension)` / `Contracts & Licenses`
- **Biaya Kredit**: `Costs 1 API credit.`

**Penjelasan**:
Returns active mining contracts linking mine owners to their service contractors. Optionally filter by owner or contractor slug.

> 💳 **Credits**: Costs 1 API credit.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `contractor` | `query` | `string` | Tidak | `-` | Filter by contractor company slug. |
| `mine_owner` | `query` | `string` | Tidak | `-` | Filter by mine owner company slug. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/mining/contracts/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 72. Mining License Auctions
- **Method & Path**: `GET https://api.sectors.app/v2/mining/license-auctions/`
- **Kategori**: `Mining (Extension)` / `Contracts & Licenses`
- **Biaya Kredit**: `Costs 1 API credit.`

**Penjelasan**:
Lists mining license auctions scraped from the ESDM Minerba portal. Phases and participants are omitted from list results — use the detail endpoint for the full auction record.

> 💡 **Note**: Available `commodity_type` values: `Nickel`, `Coal`, `Gold`, `Copper`.

Use `participant` + `qualified=true` to find auctions where a specific company passed pre-qualification.

> 💳 **Credits**: Costs 1 API credit.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `province` | `query` | `string` | Tidak | `-` | Filter by province (e.g., `Sulawesi Selatan`). Case-insensitive. |
| `commodity_type` | `query` | `string` | Tidak | `-` | Filter by commodity (e.g., `Nickel`, `Coal`). Case-insensitive. |
| `order_by` | `query` | `string` | Tidak | `-` | Sort field. Prefix with `-` for descending. Default: `-winner_date`. |
| `limit` | `query` | `integer` | Tidak | `20` | Number of results to return. Maximum: 30. |
| `offset` | `query` | `integer` | Tidak | `0` | Number of results to skip. |
| `area_type` | `query` | `string` | Tidak | `-` | Filter by area type (e.g., `WIUPK`). Case-insensitive. |
| `status` | `query` | `string` | Tidak | `-` | Filter by auction status (e.g., `Lelang Selesai`). Case-insensitive. |
| `participant` | `query` | `string` | Tidak | `-` | Filter auctions where a company name (partial match) participated. |
| `qualified` | `query` | `boolean` | Tidak | `-` | When `true`, only return auctions where the `participant` passed qualification. Requires `participant`. |
| `min_participants` | `query` | `integer` | Tidak | `-` | Only return auctions with at least this many participants. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/mining/license-auctions/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 73. Mining License Auction Detail
- **Method & Path**: `GET https://api.sectors.app/v2/mining/license-auctions/{wiup_code}/`
- **Kategori**: `Mining (Extension)` / `Contracts & Licenses`
- **Biaya Kredit**: `Costs 1 API credit.`

**Penjelasan**:
Retrieves the full record for a single mining license auction by its WIUP code, including the parsed phases timeline and participant qualification list.

> 💳 **Credits**: Costs 1 API credit.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `wiup_code` | `path` | `string` | Ya | `-` | The unique WIUP code identifier for the auction. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/mining/license-auctions/WIUP-SAMPLE-01/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

### 74. Mining Licenses
- **Method & Path**: `GET https://api.sectors.app/v2/mining/licenses/`
- **Kategori**: `Mining (Extension)` / `Contracts & Licenses`
- **Biaya Kredit**: `Costs 1 API credit.`

**Penjelasan**:
Lists mining licenses (IUP/IUPK) from the ESDM Minerba portal with filters for status, commodity, location, and expiry date.

> 💡 **Note**: Top `commodity_type` values: `Coal`, `Nickel`, `Non-Metallic Mineral`, `Sand/Stone/Gravel`, `Limestone`, `Gold`, `Tin`, `Iron`, `Bauxite`, `Clay`, `Copper`.

Prefix `order_by` with `-` for descending order. Default sort: `license_expiry_date` (soonest expiring first).

> 💳 **Credits**: Costs 1 API credit.

**Parameter Request:**
| Nama | Lokasi | Tipe | Wajib? | Default | Keterangan |
|---|---|---|---|---|---|
| `province` | `query` | `string` | Tidak | `-` | Filter by province. Exact match. |
| `commodity_type` | `query` | `string` | Tidak | `-` | Filter by commodity. Case-insensitive. |
| `company` | `query` | `string` | Tidak | `-` | Filter by company slug. |
| `order_by` | `query` | `string` | Tidak | `-` | Sort field. Prefix with `-` for descending. Default: `license_expiry_date`. |
| `limit` | `query` | `integer` | Tidak | `20` | Number of results to return. Maximum: 30. |
| `offset` | `query` | `integer` | Tidak | `0` | Number of results to skip. |
| `expiring_soon` | `query` | `boolean` | Tidak | `-` | Set to `true` to find licenses expiring within the next 365 days. |
| `license_type` | `query` | `string` | Tidak | `-` | Filter by license type (e.g., `IUP`, `IUPK`). Case-insensitive. |
| `activity` | `query` | `string` | Tidak | `-` | Filter by activity stage (e.g., `Eksplorasi`, `Operasi Produksi`). Case-insensitive. |
| `cnc` | `query` | `boolean` | Tidak | `-` | Filter by Clear & Clean status. Case-insensitive. |

**Contoh Pemanggilan Python:**
```python
import os, requests

url = "https://api.sectors.app/v2/mining/licenses/"
headers = {
    "Authorization": os.getenv("SECTORS_API_KEY"),
    "User-Agent": "SectorsMiddleware/1.0"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Success:", data)
else:
    print("Error:", response.status_code, response.text)
```

---

# 5. Panduan Sectors MCP Server (Model Context Protocol)

Sectors menyediakan MCP Server siap pakai berbasis **Streamable HTTP Transport**:
- **Endpoint MCP**: `https://sectors-mcp.supertype.ai/mcp`
- **Header**: `Authorization: Bearer <SECTORS_API_KEY>`

### Konfigurasi MCP Client:

#### Cursor (~/.cursor/mcp.json):
```json
{
  "mcpServers": {
    "sectors": {
      "url": "https://sectors-mcp.supertype.ai/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_SECTORS_API_KEY"
      }
    }
  }
}
```

#### Claude Code CLI:
```bash
claude mcp add -t http sectors https://sectors-mcp.supertype.ai/mcp \
  -H "Authorization: Bearer YOUR_SECTORS_API_KEY"
```

### 10 Tools Utama Sectors MCP:
1. `fetch-company-report`: Overview, valuation, financials, dividend, manajemen emiten.
2. `fetch-companies-by-subsector`: Screener emiten berbasis SQL (`where`, `order_by`) atau natural language (`q`).
3. `fetch-companies-top-changes`: Top gainers dan losers periode 1d/7d/14d/30d/365d.
4. `fetch-most-traded-stocks`: Saham paling aktif diperdagangkan berdasarkan volume.
5. `fetch-quarterly-financials`: Laporan keuangan laba-rugi & neraca kuartalan.
6. `fetch-daily-transaction`: Data historis harga penutupan, volume, kapitalisasi pasar.
7. `fetch-foreign-flow`: Arus dana investor asing masuk/keluar harian per emiten.
8. `fetch-broker-summary`: Rangkuman transaksi broker per emiten.
9. `fetch-top-brokers`: Broker paling aktif di bursa berdasarkan nilai transaksi.
10. `get-subsectors`: Daftar slug seluruh subsektor IDX.

---

# 6. Implementasi Python Middleware (`API/`)

Proyek middleware di dalam direktori `API/` dibangun menggunakan FastAPI dengan tujuan:
1. **Credit Shield**: Melindungi kuota kredit dengan caching berbasis SQLite & TTL cerdas.
2. **Unified API Gateway**: Menyediakan antarmuka yang bersih untuk Web Portal & AI Agent (Garda).
3. **WhatsApp Notification Engine**: Otomasi pengiriman briefing pasar & alert anomali ke WhatsApp (`https://wa.inovasiuitjbt.uk`).
4. **Credit Audit Metrics**: Endpoint `/api/v1/metrics/credits` untuk memantau konsumsi kredit secara real-time.