"""STEP 4 - FastAPI server: serves the data as JSON, the chart images, and the website.

Run:  cd backend && uvicorn main:app --reload
Open: http://127.0.0.1:8000
"""
import json
from pathlib import Path

import pandas as pd
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

import pipeline
from clean_data import CLEAN_FILE

BASE = Path(__file__).resolve().parent.parent
app = FastAPI(title="NHAI Toll Analytics")


def load_df():
    if not CLEAN_FILE.exists():
        pipeline.run_pipeline()
    return pd.read_csv(CLEAN_FILE)


@app.get("/api/summary")
def summary():
    df = load_df()
    meta = json.loads(pipeline.META_FILE.read_text()) if pipeline.META_FILE.exists() else {}
    return {
        "total_plazas": int(len(df)),
        "total_states": int(df["state"].nunique()),
        "avg_car_fee": round(float(df["fee_car"].mean()), 2),
        "max_car_fee": float(df["fee_car"].max()),
        "meta": meta,
    }


@app.get("/api/states")
def states():
    return sorted(load_df()["state"].unique().tolist())


@app.get("/api/tolls")
def tolls(state: str = "", limit: int = 50):
    df = load_df()
    if state:
        df = df[df["state"].str.lower() == state.lower()]
    return json.loads(df.head(limit).to_json(orient="records"))


@app.post("/api/refresh")
def refresh():
    """Re-fetch, re-clean and redraw all charts."""
    return pipeline.run_pipeline()


app.mount("/charts", StaticFiles(directory=BASE / "charts", check_dir=False), name="charts")


@app.get("/")
def home():
    return FileResponse(BASE / "frontend" / "index.html")


app.mount("/static", StaticFiles(directory=BASE / "frontend"), name="static")
