"""STEP 1 - Fetch NHAI toll data from data.gov.in (Open Government Data API).

How to get live data:
  1. Register at https://data.gov.in and copy your API key (My Account).
  2. Open an NHAI toll plaza dataset, copy its "resource id" from the API tab.
  3. Set them before running:
        export DATA_GOV_API_KEY="your_key"
        export DATA_GOV_RESOURCE_ID="resource_id_here"

If the key/resource id is missing or the request fails, we create SAMPLE data
(with deliberate mess in it) so you can still practise cleaning and plotting.
"""
import os
from pathlib import Path

import numpy as np
import pandas as pd
import requests

RAW_FILE = Path(__file__).resolve().parent.parent / "data" / "raw" / "nhai_toll_raw.csv"
API_URL = "https://api.data.gov.in/resource/{resource_id}"


def fetch_from_api(api_key, resource_id, limit=1000):
    """Download records from data.gov.in page by page."""
    records, offset = [], 0
    while True:
        params = {"api-key": api_key, "format": "json", "limit": limit, "offset": offset}
        resp = requests.get(API_URL.format(resource_id=resource_id), params=params, timeout=30)
        resp.raise_for_status()
        batch = resp.json().get("records", [])
        if not batch:
            break
        records.extend(batch)
        offset += limit
    return pd.DataFrame(records)


def make_sample_data(n=300, seed=42):
    """Fake-but-realistic toll plaza data with typical real-world problems."""
    rng = np.random.default_rng(seed)
    states = ["Maharashtra", "Uttar Pradesh", "Gujarat", "Rajasthan", "Karnataka",
              "Tamil Nadu", "Madhya Pradesh", "Andhra Pradesh", "Haryana", "Punjab",
              "West Bengal", "Odisha", "Kerala", "Bihar"]
    weights = np.array([12, 14, 10, 11, 8, 8, 9, 7, 5, 4, 4, 3, 2, 3], dtype=float)
    state = rng.choice(states, size=n, p=weights / weights.sum())
    length = rng.uniform(20, 250, n).round(1)
    car = (45 + length * rng.uniform(0.2, 0.5, n)).round(0)
    df = pd.DataFrame({
        "Toll Plaza Name": [f"Plaza {i:03d}" for i in range(1, n + 1)],
        "State": state,
        "NH Number": rng.choice(["NH-48", "NH-44", "NH-27", "NH-19", "NH-16", "NH-52", "NH-58"], n),
        "Stretch Length (km)": length,
        "Lanes": rng.choice([2, 4, 6], n, p=[0.25, 0.55, 0.20]),
        "Year Commissioned": rng.integers(2005, 2025, n),
        "Fee Car": [f"Rs. {int(x):,}" for x in car],                       # text, not number
        "Fee LCV": [f"Rs. {int(x * 1.6):,}" for x in car],
        "Fee Bus/Truck": [f"Rs. {int(x * 3.2):,}" for x in car],
    })
    # ---- add mess ----
    df.loc[rng.choice(n, 12, replace=False), "Fee Car"] = np.nan             # missing values
    df.loc[rng.choice(n, 8, replace=False), "Stretch Length (km)"] = np.nan
    df.loc[rng.choice(n, 5, replace=False), "Fee Bus/Truck"] = "NA"
    df.loc[rng.choice(n, 20, replace=False), "State"] = (
        df["State"].str.upper() + " ")                                       # inconsistent case/spaces
    df.loc[rng.choice(n, 2, replace=False), "Stretch Length (km)"] = 9999    # outlier / typo
    df = pd.concat([df, df.sample(6, random_state=1)], ignore_index=True)    # duplicates
    return df


def get_raw_data():
    api_key = os.getenv("DATA_GOV_API_KEY")
    resource_id = os.getenv("DATA_GOV_RESOURCE_ID")
    source = "sample"
    df = None
    if api_key and resource_id:
        try:
            df = fetch_from_api(api_key, resource_id)
            source = "data.gov.in"
            print(f"Fetched {len(df)} rows from data.gov.in")
        except Exception as e:
            print("API fetch failed:", e)
    if df is None or df.empty:
        print("Using SAMPLE data (set DATA_GOV_API_KEY and DATA_GOV_RESOURCE_ID for live data)")
        df = make_sample_data()
        source = "sample"
    RAW_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(RAW_FILE, index=False)
    return df, source


if __name__ == "__main__":
    data, src = get_raw_data()
    print(f"Saved {len(data)} raw rows ({src}) -> {RAW_FILE}")
