# OpsVista — Enterprise Operations Intelligence Platform

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.14-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/MySQL-8.0-4479A1?style=for-the-badge&logo=mysql&logoColor=white"/>
  <img src="https://img.shields.io/badge/Power%20BI-Dashboard-F2C811?style=for-the-badge&logo=powerbi&logoColor=black"/>
  <img src="https://img.shields.io/badge/pandas-2.0-150458?style=for-the-badge&logo=pandas&logoColor=white"/>
  <img src="https://img.shields.io/badge/Status-Active-2ea043?style=for-the-badge"/>
</p>

<p align="center">
  <b>An end-to-end enterprise data analytics platform built for a manufacturing company — covering Procurement, Inventory, Supplier Performance, and Logistics.</b>
</p>

<p align="center">
  <a href="#project-overview">Overview</a> •
  <a href="#business-problem">Problem</a> •
  <a href="#dataset">Dataset</a> •
  <a href="#project-modules">Modules</a> •
  <a href="#dashboard">Dashboard</a> •
  <a href="#sql-analytics">SQL</a> •
  <a href="#predictive-analytics">Predictive</a> •
  <a href="#key-insights">Insights</a> •
  <a href="#folder-structure">Structure</a> •
  <a href="#how-to-run">Run</a>
</p>

---

## Project Overview

OpsVista is a **portfolio-grade analytics project** built to simulate the kind of work done at consulting and analytics firms like Deloitte, KPMG, ZS Associates, ProcDNA, and Tredence.

A mid-sized manufacturing company manages procurement, inventory, warehouses, and logistics through disconnected Excel files. Management cannot answer critical operational questions in time. **OpsVista centralizes this data into a single intelligence platform** that answers:

- Which vendors are causing delays and costing the business money?
- Which products are about to run out of stock?
- Which warehouses are overcrowded or underutilized?
- Which regions suffer the most shipment delays?
- What actions should management take right now?

> **Type:** Business Intelligence & Data Analytics Project  
> **Domain:** Manufacturing · Supply Chain · Procurement · Logistics  
> **Role simulated:** Data Analyst at a consulting firm

---

## Business Problem

| Problem Area | Issue |
|---|---|
| Procurement | Rising costs, vendor delays, no unified view of supplier performance |
| Inventory | Stockouts in fast-moving materials, overstock in slow-moving SKUs |
| Warehouse | Some warehouses critically overcrowded, others underutilized |
| Logistics | High shipment delay rates in certain regions and with certain partners |
| Reporting | No centralized dashboard — management relies on manually updated Excel sheets |

---

## Dataset

**Fully synthetic data generated using Python (Faker + NumPy) with realistic business patterns.**

| Table | Rows | Description |
|---|---|---|
| categories | 8 | Product category master |
| products | 68 | SKUs across 8 categories |
| suppliers | 80 | 28 reliable · 32 average · 20 poor |
| warehouses | 10 | Pan-India warehouse network |
| customers | 600 | B2B customer base |
| purchase_orders | 6,000 | 3 years of procurement records |
| purchase_order_items | 18,000+ | Line items per purchase order |
| inventory | 410 | Stock levels per product per warehouse |
| sales_orders | 12,000 | Customer order transactions |
| shipments | 9,619 | Delivery records with delay tracking |
| returns | 673 | Product return records |
| **Total** | **47,548** | **Rows across 11 tables** |

### Business Patterns Embedded in Data

- **Seasonality** — Q4 (Oct–Dec) shows 40% higher procurement and sales volume
- **Vendor profiles** — Poor vendors have 35–50% delay rates; reliable vendors stay below 8%
- **Regional logistics gaps** — East region records 25% shipment delay rate vs 12% in South
- **Stockouts** — 5% of inventory records are deliberately set to zero stock
- **Overstocking** — 10% of inventory records are set at 3–6x normal levels
- **Return patterns** — ~7% of delivered orders result in returns

---

## Tech Stack

| Tool / Library | Version | Purpose |
|---|---|---|
| Python | 3.14 | Data generation, cleaning, EDA, predictive analytics |
| pandas | 2.0 | Data manipulation and feature engineering |
| NumPy | 1.26 | Numerical operations |
| Faker | Latest | Synthetic data generation |
| Matplotlib | 3.8 | EDA chart generation |
| MySQL | 8.0 | Relational database and SQL analytics |
| mysql-connector-python | Latest | Python to MySQL ETL |
| Power BI Desktop | Latest | 4-page interactive dashboard |

---

## Project Modules

### Module 1 — Synthetic Data Generation
**Script:** `scripts/generate_data.py`

Generates all 11 CSV files with realistic enterprise ERP-like patterns. Uses Faker for Indian business context, NumPy for controlled randomness, and custom logic for seasonality, vendor delay profiles, and regional shipping gaps.

```
Key design decisions:
- Suppliers assigned profiles (reliable/average/poor) before data generation
- Each profile has different delay_rate, return_rate, and lead_time_base
- Seasonal multiplier (1.4x for Q4) applied to both procurement cost and sales quantity
- Regional delay probability hardcoded per region (East = 25%, South = 12%)
```

---

### Module 2 — Data Cleaning
**Script:** `scripts/clean_data.py`

Reads all 11 raw CSVs and produces cleaned versions with engineered features.

| Operation | Detail |
|---|---|
| Duplicate removal | `drop_duplicates()` on primary key columns |
| Null handling | Median for numeric · logical defaults for categorical |
| Date parsing | `pd.to_datetime()` on all date columns |
| Feature: `lead_days` | actual_delivery_date − order_date |
| Feature: `delay_days` | actual_delivery_date − expected_delivery_date (clipped to 0) |
| Feature: `stock_status` | Stock-Out / Low Stock / Healthy / Overstock |
| Feature: `days_of_stock_left` | quantity_on_hand ÷ avg_daily_usage |
| Feature: `reorder_flag` | 1 if quantity_on_hand ≤ reorder_point |
| Feature: `delay_severity` | On Time / Minor / Moderate / Severe Delay |
| Feature: `supplier_tier` | Tier 1 / Tier 2 / Tier 3 from profile |
| Feature: `risk_flag` | 1 if delay_rate > 30% or return_rate > 10% |

---

### Module 3 — MySQL Database
**Script:** `sql/opsvista_queries.sql`

Normalized relational schema with 11 tables, primary keys, foreign keys, and indexes.

```sql
-- Schema follows 3rd Normal Form (3NF)
-- Parent tables: categories, suppliers, warehouses, customers, products
-- Child tables: purchase_orders, sales_orders, inventory
-- Transaction tables: purchase_order_items, shipments, returns
```

---

### Module 4 — ETL Pipeline
**Script:** `scripts/load_data.py`

Python script that reads all clean CSVs and loads them into MySQL using `mysql-connector-python`. Handles:
- `TRUNCATE` before reload (idempotent pipeline)
- `SET FOREIGN_KEY_CHECKS=0` to manage load order
- `None` substitution for NaN values (MySQL NULL compatibility)
- `executemany()` for batch inserts (performance)

---

### Module 5 — SQL Analytics
**File:** `sql/opsvista_queries.sql`

**45 business SQL queries across 7 sections:**

| Section | Queries | Key Techniques |
|---|---|---|
| Procurement Analysis | Q1–Q5 | GROUP BY · Running totals · Window SUM |
| Supplier Performance | Q6–Q12 | RANK() · LAG() · HAVING · Weighted scoring |
| Inventory Analysis | Q13–Q20 | CASE WHEN · ABC classification · NTILE |
| Sales Analysis | Q21–Q27 | Running totals · YoY · Top N |
| Shipment Analysis | Q28–Q34 | DENSE_RANK() · DATE_FORMAT · Conditional |
| Returns Analysis | Q35–Q38 | LEFT JOIN · Proportion window |
| Advanced / Combined | Q39–Q45 | CTEs · Multi-table joins · NTILE · Subqueries |

**Sample query — Supplier Performance Score:**
```sql
SELECT
    s.supplier_name,
    s.profile,
    ROUND(AVG(po.lead_days), 1) AS avg_lead,
    ROUND(SUM(po.is_delayed)/COUNT(*)*100, 1) AS delay_pct,
    ROUND(
        100
        - (SUM(po.is_delayed)/COUNT(*)*100 * 1.5)
        - ((AVG(po.lead_days) - 7) * 0.5)
    , 1) AS performance_score
FROM suppliers s
JOIN purchase_orders po ON s.supplier_id = po.supplier_id
GROUP BY s.supplier_id, s.supplier_name, s.profile
ORDER BY performance_score DESC;
```

---

### Module 6 — Python EDA
**Script:** `scripts/eda.py`  
**Output:** `eda_charts/` (10 PNG files)

| Chart | Business Question Answered |
|---|---|
| 01_monthly_procurement.png | Is procurement cost trending up or down? |
| 02_supplier_delay_profile.png | How much does vendor profile affect delays? |
| 03_warehouse_utilization.png | Which warehouses are at capacity risk? |
| 04_category_spend.png | Where is the procurement budget going? |
| 05_stock_status.png | How healthy is current inventory? |
| 06_shipment_delay_region.png | Which regions have logistics problems? |
| 07_monthly_sales.png | Is revenue growing month over month? |
| 08_top_suppliers_spend.png | Who are the highest spend suppliers? |
| 09_return_reasons.png | Why are products being returned? |
| 10_delay_severity.png | How severe are shipment delays? |

All charts use a dark theme (`#0d1117` background) matching the Power BI dashboard for visual consistency.

---

### Module 7 — Predictive Analytics
**Script:** `predictive/predictive_analytics.py`  
**Outputs:** `predictive/vendor_risk_scores.csv` · `predictive/reorder_predictions.csv` · `predictive/ai_recommendations.csv`

#### Model 1 — Vendor Risk Score (Weighted Scoring)

```
Risk Score = (Delay Rate × 50) + (Return Rate × 30) + (Lead Time Score × 20)

Why weighted scoring over ML:
- Business logic is well-understood and explainable to non-technical clients
- Transparent formula is auditable — a client can verify the score
- Same quality result as logistic regression for this use case
- Easier to adjust weights based on business priorities
```

| Risk Category | Score Range | Vendors | Action |
|---|---|---|---|
| High Risk | 60–100 | 20 | Immediate SLA review |
| Medium Risk | 30–60 | 32 | Monitor closely |
| Low Risk | 0–30 | 28 | Preferred vendors |

#### Model 2 — Inventory Reorder Prediction (Days of Stock)

```
Logic: If days_of_stock_left < avg_supplier_lead_time → flag for reorder

days_of_stock_left = quantity_on_hand ÷ avg_daily_usage
avg_daily_usage    = reorder_point ÷ 30

Urgency levels:
- Critical  : quantity_on_hand = 0 (immediate action)
- High      : days_of_stock_left < 7
- Medium    : days_of_stock_left < 20
- Low       : sufficient stock
```

#### Model 3 — AI Recommendation Engine (Business Rules)

Generates automated action cards based on threshold triggers:

```python
# Rule examples:
if vendor_risk_score >= 60    → "Initiate SLA review within 14 days"
if stockout_count > 0         → "Raise emergency purchase orders"
if warehouse_utilization > 90 → "Redistribute inventory immediately"
if region_delay_rate > 20     → "Migrate shipments to better partner"
if return_rate > 5            → "Conduct supplier quality audit"
```

---

### Module 8 — Power BI Dashboard
**File:** `OpsVista_Dashboard.pbix`

4-page interactive dashboard with dark theme (`#0d1117`), conditional formatting, and navigation buttons.

---

## Dashboard

### Page 1 — Executive Dashboard
**Answers: What is the overall state of operations?**

- 8 KPI cards — Procurement Cost · On-Time Delivery · Lead Time · Return Rate · Inventory Value · Shipment Delay · Stockouts · Supplier Count
- Monthly procurement cost trend line (24 months)
- Procurement spend by category (donut chart)
- YoY procurement vs sales comparison (bar chart)
- Shipment delay % by region (conditional bar chart — Red/Yellow/Green)

### Page 2 — Supplier Performance
**Answers: Which vendors should we keep, watch, or replace?**

- Supplier scorecard table with conditional formatting on delivery performance
- On-time delivery % per supplier (top 15, color-coded bars)
- Top suppliers by procurement spend (top 10)
- KPIs — Reliable · Average · Poor supplier counts

### Page 3 — Inventory & Warehouse
**Answers: Do we have the right stock in the right place?**

- Warehouse utilization % (color-coded — Red > 90%, Yellow > 75%)
- Stock health table — product · stock on hand · reorder point · days of stock left · status
- Inventory value by category
- SKU velocity mix (Fast / Medium / Slow donut)

### Page 4 — Predictive Analytics
**Answers: What risks are coming and what should we do?**

- Vendor risk scorecard from `vendor_risk_scores.csv`
- Risk distribution (High / Medium / Low donut)
- Shipment delay prediction by partner and region
- Reorder alert table from `reorder_predictions.csv` with urgency flags

---

## SQL Analytics

**45 queries covering:**

```sql
-- Window Functions used:
SUM() OVER (ORDER BY month)           -- Running totals
LAG() OVER (PARTITION BY supplier)    -- Month-over-month change
RANK() OVER (ORDER BY delay_pct)      -- Supplier delay ranking
DENSE_RANK() OVER (...)               -- Shipment partner ranking
NTILE(4) OVER (ORDER BY revenue)      -- Customer quartile segmentation
ROW_NUMBER() OVER (PARTITION BY cat)  -- Product rank within category

-- CTEs used for:
-- Supplier summary → performance tier assignment
-- Warehouse stock health → utilization calculation
-- ABC inventory classification

-- Business queries include:
-- Procurement cost running total by month
-- Supplier performance weighted score
-- Warehouse utilization %
-- ABC inventory classification
-- Month-over-month sales growth %
-- Customer revenue quartile segmentation
-- Products below reorder point sorted by urgency
```

---

## Predictive Analytics

### Vendor Risk Score Results

| Risk Level | Count | Avg Delay Rate | Avg Return Rate |
|---|---|---|---|
| High Risk | 20 | 40%+ | 12%+ |
| Medium Risk | 32 | 18–35% | 6–10% |
| Low Risk | 28 | < 8% | < 3% |

### Reorder Prediction Results

| Urgency | SKUs | Action |
|---|---|---|
| Critical (Stock-Out) | 15 | Emergency PO today |
| High (< 7 days stock) | 12 | PO within 48 hours |
| Medium (< 20 days) | 16 | PO this week |

---

## Key Insights

```
1. PROCUREMENT
   ↳ Procurement cost grew 7% YoY from 2022 to 2024
   ↳ Q4 consistently shows 40% cost spike due to seasonal demand
   ↳ Raw Materials and Machinery account for 65% of total spend

2. SUPPLIER PERFORMANCE  
   ↳ 20 of 80 suppliers have delay rates above 35% — classified High Risk
   ↳ Average lead time is 20.1 days vs industry target of 14 days
   ↳ Parker Hannifin, Kennametal, Sandvik are the highest-risk vendors

3. INVENTORY & WAREHOUSE
   ↳ 15 SKUs at complete zero stock — all are fast-moving raw materials
   ↳ Mumbai-WH2 (98.8%) and Delhi-WH1 (97.1%) are critically overcrowded
   ↳ Jaipur-WH9 (51%) and Lucknow-WH10 (37%) have significant spare capacity
   ↳ 43 SKUs currently below their reorder point

4. LOGISTICS
   ↳ East region: 25% shipment delay rate — highest in the network
   ↳ Ekart (22%) and DTDC (21%) are worst-performing shipment partners
   ↳ BlueDart and DHL both at 14% delay rate — best performers

5. RETURNS
   ↳ Return rate at 7% — above 5% threshold requiring quality audit
   ↳ "Defective Product" and "Quality Issue" are top return reasons
   ↳ 673 returns processed across the 3-year period
```

---

## Business Recommendations

| Priority | Area | Finding | Action |
|---|---|---|---|
| 🔴 Critical | Inventory | 15 SKUs at zero stock | Raise emergency POs immediately |
| 🔴 High | Supplier | 20 vendors with delay > 35% | SLA review within 14 days |
| 🟡 High | Warehouse | Mumbai & Delhi above 90% capacity | Redistribute to Jaipur/Lucknow |
| 🟡 Medium | Logistics | East region 25% delay rate | Switch to BlueDart/DHL for East |
| 🔵 Medium | Quality | Return rate 7% > 5% threshold | Supplier quality audit |
| 🔵 Opportunity | Cost | 7% YoY procurement cost increase | Consolidate with Tier 1 vendors |

---

## Folder Structure

```
OpsVista/
│
├── data/
│   ├── raw/                    # 11 generated CSV files (47,548 rows)
│   └── clean/                  # 11 cleaned CSVs with engineered features
│
├── scripts/
│   ├── generate_data.py        # Synthetic data generation
│   ├── clean_data.py           # Data cleaning pipeline
│   ├── load_data.py            # ETL — CSV to MySQL
│   └── eda.py                  # EDA chart generation
│
├── sql/
│   └── opsvista_queries.sql    # 45 business SQL queries
│
├── eda_charts/                 # 10 Matplotlib charts (PNG)
│   ├── 01_monthly_procurement.png
│   ├── 02_supplier_delay_profile.png
│   ├── 03_warehouse_utilization.png
│   ├── 04_category_spend.png
│   ├── 05_stock_status.png
│   ├── 06_shipment_delay_region.png
│   ├── 07_monthly_sales.png
│   ├── 08_top_suppliers_spend.png
│   ├── 09_return_reasons.png
│   └── 10_delay_severity.png
│
├── predictive/
│   ├── predictive_analytics.py  # All 3 predictive models
│   ├── vendor_risk_scores.csv   # Vendor risk output
│   ├── reorder_predictions.csv  # Reorder alert output
│   └── ai_recommendations.csv  # Business recommendations
│
├── docs/
│   └── (documentation files)
│
├── OpsVista_Dashboard.pbix      # Power BI dashboard file
├── .gitignore
└── README.md
```

---

## How to Run

### 1. Clone the Repository
```bash
git clone https://github.com/jasminek-18/OpsVista.git
cd OpsVista
```

### 2. Install Dependencies
```bash
pip install pandas numpy faker matplotlib mysql-connector-python
```

### 3. Generate Data
```bash
cd scripts
python generate_data.py
```

### 4. Clean Data
```bash
python clean_data.py
```

### 5. Run EDA
```bash
python eda.py
```
Charts saved to `eda_charts/`

### 6. Run Predictive Analytics
```bash
cd ../predictive
python predictive_analytics.py
```

### 7. Load into MySQL (optional)
```bash
cd ../scripts
# Edit load_data.py — add your MySQL password
python load_data.py
```

### 8. Open Power BI Dashboard
- Open `OpsVista_Dashboard.pbix` in Power BI Desktop
- Update data source paths if needed (Get Data → Data source settings)

---

## Interview Q&A

**Q: Why did you choose manufacturing as the domain?**
> Manufacturing and supply chain analytics is one of the most in-demand domains at consulting firms like Deloitte, KPMG, ZS Associates, and ProcDNA. The business problems — vendor delays, inventory gaps, procurement cost leakage — are problems these firms solve for FMCG, pharma, and industrial clients daily.

**Q: Why synthetic data instead of real data?**
> Real enterprise ERP data is confidential and rarely publicly available at this scale. Synthetic data allowed me to embed specific business patterns — seasonal demand spikes, vendor delay profiles, regional logistics gaps — that make the analytics meaningful. Random data would produce flat, uninteresting insights.

**Q: Why weighted scoring for vendor risk instead of ML?**
> The business logic is well-understood: delays, returns, and lead time are the right factors. A weighted formula — 50% delay, 30% returns, 20% lead time — is transparent and explainable to a non-technical client. In consulting, explainability matters more than model complexity.

**Q: What would you add if you had more time?**
> A live data refresh pipeline using Apache Airflow, a cost optimization module that estimates potential savings from switching to Tier 1 vendors, and a customer segmentation analysis using RFM scoring on the sales data.

---

## About

Built by **Jasmine** — ECE student at UIET, Panjab University, Chandigarh  
Targeting analytics and consulting roles at ZS Associates · ProcDNA · Deloitte · KPMG · EY · Tredence

---

<p align="center">
  <i>If this project was useful, consider giving it a ⭐</i>
</p>
