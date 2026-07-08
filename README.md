# OpsVista — Enterprise Operations Intelligence Platform

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.14-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/MySQL-8.0-4479A1?style=for-the-badge&logo=mysql&logoColor=white"/>
  <img src="https://img.shields.io/badge/Power%20BI-Dashboard-F2C811?style=for-the-badge&logo=powerbi&logoColor=black"/>
  <img src="https://img.shields.io/badge/pandas-2.0-150458?style=for-the-badge&logo=pandas&logoColor=white"/>
</p>

An end-to-end data analytics platform built for a manufacturing company — centralizing Procurement, Inventory, Supplier Performance, and Logistics data into a single intelligence solution.

---

## Problem

A manufacturing company manages operations through disconnected Excel reports. No unified view exists across procurement, inventory, and logistics — making it impossible to identify vendor risks, stockouts, or warehouse bottlenecks in time to act.

---

## What This Project Does

- Generates 47,548 rows of realistic ERP-like data across 11 tables with embedded business patterns (seasonality, vendor delay profiles, regional logistics variance)
- Cleans and engineers features using a Python pipeline (lead days, stock status, delay severity, reorder flags)
- Loads data into a normalized MySQL schema and runs 45 business SQL queries using CTEs, window functions, and rankings
- Produces 10 EDA charts using Matplotlib
- Runs three predictive models — Vendor Risk Scoring, Inventory Reorder Prediction, and an AI Recommendation Engine
- Visualizes everything in a 4-page dark-theme Power BI dashboard

---

## Dataset

| Table | Rows |
|---|---|
| Purchase Orders | 6,000 |
| Sales Orders | 12,000 |
| Shipments | 9,619 |
| Suppliers | 80 |
| Warehouses | 10 |
| + 6 more tables | — |
| **Total** | **47,548** |

Data is synthetic, generated using Python (Faker + NumPy). Patterns are deliberately embedded — not random.

---

## Tech Stack

`Python` `pandas` `NumPy` `Faker` `Matplotlib` `MySQL` `Power BI`

---

## Predictive Models

**Vendor Risk Score**
Weighted composite: `(delay rate × 50) + (return rate × 30) + (lead time score × 20)`
Classifies each supplier as High / Medium / Low risk with a recommended action.

**Inventory Reorder Prediction**
Flags SKUs where `days_of_stock_left < avg_supplier_lead_time`.
Outputs urgency level (Critical / High / Medium) and suggested order quantity.

**AI Recommendation Engine**
Rule-based engine that generates business action cards from operational thresholds — stockouts, warehouse congestion, delay spikes, return rate breaches.

---

## Dashboard — 4 Pages

| Page | Focus |
|---|---|
| Executive Dashboard | KPIs, procurement trend, regional delay analysis |
| Supplier Performance | Scorecard table, delay rates, spend ranking |
| Inventory & Warehouse | Utilization, stock health, reorder alerts |
| Predictive Analytics | Risk scores, reorder predictions, recommendations |

---

## Key Findings

- 20 of 80 suppliers have delay rates above 35% — classified High Risk
- 15 SKUs at zero stock, 43 below reorder point
- Mumbai-WH2 (98.8%) and Delhi-WH1 (97.1%) are critically congested
- East region records the highest shipment delay rate at 25%
- Return rate at 7% — above the 5% operational threshold

---

## How to Run

```bash
git clone https://github.com/jasminek-18/OpsVista.git
cd OpsVista
pip install pandas numpy faker matplotlib mysql-connector-python

cd scripts
python generate_data.py    # generates data/raw/
python clean_data.py       # generates data/clean/
python eda.py              # generates eda_charts/

cd ../predictive
python predictive_analytics.py   # generates CSVs for Power BI
```

Open `OpsVista_Dashboard.pbix` in Power BI Desktop.  
Update file paths in Data Source Settings if needed.

---

## Folder Structure

```
OpsVista/
├── data/raw/               Raw generated CSVs
├── data/clean/             Cleaned CSVs with engineered features
├── scripts/                generate_data · clean_data · load_data · eda
├── sql/                    45 SQL queries
├── eda_charts/             10 Matplotlib PNGs
├── predictive/             Risk scores · reorder predictions · recommendations
└── OpsVista_Dashboard.pbix Power BI dashboard
```

---

**Jasmine** · ECE · UIET, Panjab University, Chandigarh · [github.com/jasminek-18](https://github.com/jasminek-18)
