"""
Downloads CMS Hospital Readmissions Reduction Program (HRRP) data.
Source: https://data.cms.gov — publicly available, no account needed.
Run once before launching the dashboard: python download_data.py
"""

import requests
import pandas as pd
from pathlib import Path

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
OUTPUT = DATA_DIR / "readmissions.csv"

# CMS Provider Data Catalog API — Hospital Readmissions Reduction Program
# Dataset: 9n3s-kdb3  (~18k rows, FY2024)
BASE = "https://data.cms.gov/provider-data/api/1/datastore/query/9n3s-kdb3/0"
FIELDS = ["facility_name", "state", "measure_name", "number_of_discharges",
          "excess_readmission_ratio", "predicted_readmission_rate",
          "expected_readmission_rate", "number_of_readmissions", "start_date", "end_date"]

print("Downloading CMS HRRP data...")
rows, offset, page_size = [], 0, 1000
while True:
    url = f"{BASE}?limit={page_size}&offset={offset}"
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    batch = resp.json().get("results", [])
    if not batch:
        break
    rows.extend(batch)
    print(f"  Fetched {len(rows)} rows...")
    offset += len(batch)
    if len(batch) < page_size:
        break

df = pd.DataFrame(rows)
print(f"  Raw rows: {len(df)}")

# Coerce numerics
numeric_cols = [
    "number_of_discharges",
    "excess_readmission_ratio",
    "predicted_readmission_rate",
    "expected_readmission_rate",
    "number_of_readmissions",
]
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Drop rows where key metrics are missing (CMS suppresses small hospitals)
df = df.dropna(subset=["excess_readmission_ratio", "predicted_readmission_rate", "state"])
print(f"  After cleaning: {len(df)} rows")

df.to_csv(OUTPUT, index=False)
print(f"Saved to {OUTPUT}")
print("\nConditions in dataset:")
print(df["measure_name"].value_counts().to_string())
