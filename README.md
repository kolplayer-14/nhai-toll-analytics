# NHAI Toll Plaza Analytics (beginner data project)

Fetch NHAI toll data from data.gov.in -> clean with pandas/numpy -> plot with matplotlib -> serve with FastAPI -> view on a simple HTML/CSS/JS website.

## Folder layout
```
backend/
  fetch_data.py   step 1: download from data.gov.in API (or make sample data)
  clean_data.py   step 2: pandas + numpy cleaning
  charts.py       step 3: matplotlib graphs -> charts/*.png
  pipeline.py     runs steps 1-3
  main.py         step 4: FastAPI server (JSON API + website)
frontend/         index.html, style.css, script.js
data/raw, data/clean, charts/   generated outputs
```

## Run it
```bash
pip install -r requirements.txt
cd backend
uvicorn main:app --reload
```
Open http://127.0.0.1:8000 (API docs at /docs). The pipeline runs automatically on first start.

## Use LIVE data.gov.in data
1. Create a free account on https://data.gov.in and copy your API key.
2. Find an NHAI toll plaza dataset, open its API tab and copy the resource id.
3. ```bash
   export DATA_GOV_API_KEY="your_key"
   export DATA_GOV_RESOURCE_ID="resource_id"
   ```
4. Click **Refresh data** on the website (or run `python pipeline.py`).

Without these, the project uses generated SAMPLE data (with missing values, duplicates, bad text and outliers) so you can practise.

**Important:** real datasets have their own column names. If cleaning fails, open `data/raw/nhai_toll_raw.csv`,
look at the columns, and adjust the names in `clean_data.py` / `charts.py`.

## What the cleaning does
tidy column names, drop duplicates, fix state names, "Rs. 1,250" -> 1250, remove impossible lengths,
fill gaps with state median, add `car_fee_per_km`.

## API
GET /api/summary · GET /api/states · GET /api/tolls?state=Gujarat&limit=20 · POST /api/refresh
