"""STEP 2 - Clean the raw toll data with pandas + numpy."""
from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parent.parent
RAW_FILE = BASE / "data" / "raw" / "nhai_toll_raw.csv"
CLEAN_FILE = BASE / "data" / "clean" / "nhai_toll_clean.csv"


def to_number(series):
    """'Rs. 1,250' -> 1250.0 ; 'NA' / blanks -> NaN"""
    no_commas = series.astype(str).str.replace(",", "", regex=False)
    found = no_commas.str.extract(r"(\d+(?:\.\d+)?)", expand=False)   # first number in the text
    return pd.to_numeric(found, errors="coerce")


def clean(df):
    report = {"rows_raw": int(len(df))}

    # 1. Tidy column names: "Fee Bus/Truck" -> "fee_bus_truck"
    df = df.copy()
    df.columns = (df.columns.str.strip().str.lower()
                  .str.replace(r"[^a-z0-9]+", "_", regex=True).str.strip("_"))

    # 2. Remove duplicate rows
    before = len(df)
    df = df.drop_duplicates()
    report["duplicates_removed"] = int(before - len(df))

    # 3. Fix text columns (spaces, upper/lower case)
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()
    df["state"] = df["state"].str.title()

    # 4. Convert fee columns from text to numbers
    fee_cols = [c for c in df.columns if c.startswith("fee_")]
    for col in fee_cols:
        df[col] = to_number(df[col])

    for col in ["stretch_length_km", "lanes", "year_commissioned"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # 5. Outliers: lengths above 500 km are impossible for one toll stretch -> NaN
    bad = df["stretch_length_km"] > 500
    report["outliers_fixed"] = int(bad.sum())
    df["stretch_length_km"] = np.where(bad, np.nan, df["stretch_length_km"])

    # 6. Missing values: fill with the MEDIAN of that state (then overall median)
    report["missing_before"] = int(df[fee_cols + ["stretch_length_km"]].isna().sum().sum())
    for col in fee_cols + ["stretch_length_km"]:
        df[col] = df[col].fillna(df.groupby("state")[col].transform("median"))
        df[col] = df[col].fillna(df[col].median())
    report["missing_after"] = int(df[fee_cols + ["stretch_length_km"]].isna().sum().sum())

    # 7. New column: fee per km for cars
    df["car_fee_per_km"] = np.round(df["fee_car"] / df["stretch_length_km"], 2)

    df = df.dropna(subset=["toll_plaza_name", "state"]).reset_index(drop=True)
    report["rows_clean"] = int(len(df))
    return df, report


def run():
    raw = pd.read_csv(RAW_FILE)
    df, report = clean(raw)
    CLEAN_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CLEAN_FILE, index=False)
    return df, report


if __name__ == "__main__":
    _, rep = run()
    print(rep)
