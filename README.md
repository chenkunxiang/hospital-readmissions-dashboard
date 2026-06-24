# Hospital Readmissions Dashboard

An interactive dashboard analyzing 30-day hospital readmission rates across the United States, built with real CMS data.

![Python](https://img.shields.io/badge/Python-3.8+-blue) ![Dash](https://img.shields.io/badge/Plotly_Dash-2.17-purple) ![Data](https://img.shields.io/badge/Data-CMS_HRRP_FY2024-green)

## Overview

This project uses the [CMS Hospital Readmissions Reduction Program (HRRP)](https://data.cms.gov/provider-data/dataset/9n3s-kdb3) dataset — a publicly available federal dataset covering ~4,800 hospitals across 6 high-priority conditions. The dashboard enables exploration of which hospitals and states have excess readmission rates above or below the national expectation.

**Key question answered:** *Which hospitals are readmitting patients at rates higher than their patient population would predict — and where are they concentrated?*

## Dashboard Features

| Chart | What it shows |
|---|---|
| Choropleth map | Average excess readmission ratio by state |
| Bar chart | Top 20 highest excess-ratio hospitals |
| Scatter plot | Predicted vs expected rate per hospital (bubble = discharge volume) |
| Histogram | Distribution of excess ratios with mean and 1.0 benchmarks |

**Filters:** Condition (6 options) × State — all 4 charts and KPI cards update live.

## Data Source

- **Dataset:** CMS Hospital Readmissions Reduction Program (HRRP)
- **Coverage:** FY2024 (July 2021 – June 2024)
- **Rows:** ~11,700 hospital-condition pairs after cleaning
- **Conditions:** Heart Failure, Heart Attack (AMI), Pneumonia, COPD, Hip/Knee Replacement, Coronary Bypass (CABG)
- **Key metric:** Excess Readmission Ratio (ERR) — values > 1.0 mean a hospital readmits more than expected given its patient mix

> CMS suppresses data for hospitals with too few cases (< ~25 discharges), so some hospitals appear in only some conditions.

## Setup

```bash
# 1. Clone and install
git clone https://github.com/chenkunxiang/hospital-readmissions-dashboard.git
cd hospital-readmissions-dashboard
pip install -r requirements.txt

# 2. Download data from CMS (run once)
python download_data.py

# 3. Launch dashboard
python app.py
```

Open **http://localhost:8050** in your browser.

## Project Structure

```
├── app.py               # Dash app — layout, callbacks, charts
├── download_data.py     # Fetches data from CMS Provider Data API
├── requirements.txt
└── data/
    └── readmissions.csv # Downloaded by download_data.py (not tracked in git)
```

## Key Findings

- **Heart Failure** has the highest average excess readmission ratio nationally
- Hospitals above ERR 1.0 face CMS payment penalties under the HRRP
- Larger hospitals (more discharges) tend to cluster near the expected rate — smaller hospitals show more variance
- Southern states show elevated ERRs for COPD compared to the national average

## Skills Demonstrated

- Data acquisition from a federal API (CMS Provider Data Catalog)
- Data cleaning with pandas (handling suppressed/N/A values, numeric coercion)
- Interactive multi-page filtering with Plotly Dash callbacks
- Healthcare domain knowledge: HRRP, excess readmission ratio, CMS payment penalties
