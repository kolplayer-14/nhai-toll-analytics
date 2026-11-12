"""STEP 3 - Make toll graphs with matplotlib and save them as PNG files."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # no pop-up window; just save images
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

CHARTS_DIR = Path(__file__).resolve().parent.parent / "charts"
COLOR = "#e8590c"


def _save(fig, name):
    CHARTS_DIR.mkdir(exist_ok=True)
    fig.tight_layout()
    fig.savefig(CHARTS_DIR / name, dpi=110)
    plt.close(fig)


def plazas_per_state(df):
    s = df["state"].value_counts().head(10).sort_values()
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.barh(s.index, s.values, color=COLOR)
    ax.set_title("Top 10 States by Number of Toll Plazas")
    ax.set_xlabel("Toll plazas")
    _save(fig, "plazas_per_state.png")


def avg_car_fee_by_state(df):
    s = df.groupby("state")["fee_car"].mean().sort_values(ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.bar(s.index, s.values, color="#1c7ed6")
    ax.set_title("Average Car Toll Fee by State (Top 10)")
    ax.set_ylabel("Fee (Rs.)")
    plt.setp(ax.get_xticklabels(), rotation=40, ha="right")
    _save(fig, "avg_car_fee_by_state.png")


def fee_by_vehicle(df):
    cols = ["fee_car", "fee_lcv", "fee_bus_truck"]
    cols = [c for c in cols if c in df.columns]
    labels = [c.replace("fee_", "").replace("_", "/").upper() for c in cols]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.boxplot([df[c].dropna() for c in cols], tick_labels=labels)
    ax.set_title("Toll Fee Spread by Vehicle Type")
    ax.set_ylabel("Fee (Rs.)")
    _save(fig, "fee_by_vehicle.png")


def fee_vs_length(df):
    x, y = df["stretch_length_km"].to_numpy(), df["fee_car"].to_numpy()
    slope, intercept = np.polyfit(x, y, 1)          # straight trend line
    r = np.corrcoef(x, y)[0, 1]                      # correlation
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.scatter(x, y, alpha=0.5, color="#2f9e44")
    xs = np.linspace(x.min(), x.max(), 50)
    ax.plot(xs, slope * xs + intercept, color="black", label=f"trend (r = {r:.2f})")
    ax.set_title("Car Fee vs Stretch Length")
    ax.set_xlabel("Stretch length (km)")
    ax.set_ylabel("Car fee (Rs.)")
    ax.legend()
    _save(fig, "fee_vs_length.png")


def plazas_by_year(df):
    s = df["year_commissioned"].dropna().astype(int).value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(s.index, s.values, marker="o", color="#862e9c")
    ax.set_title("Toll Plazas Commissioned per Year")
    ax.set_xlabel("Year")
    ax.set_ylabel("Count")
    ax.grid(alpha=0.3)
    _save(fig, "plazas_by_year.png")


def make_all(df):
    for fn in (plazas_per_state, avg_car_fee_by_state, fee_by_vehicle, fee_vs_length, plazas_by_year):
        fn(df)
    return sorted(p.name for p in CHARTS_DIR.glob("*.png"))


if __name__ == "__main__":
    from clean_data import CLEAN_FILE
    print(make_all(pd.read_csv(CLEAN_FILE)))
