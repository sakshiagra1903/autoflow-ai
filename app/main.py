from __future__ import annotations
import csv, io, json
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.config import APP_NAME, VERSION, STATIC_DIR
from app.data import data_quality_report
from app.risk import COMMODITIES, compute_signals, partner_shares, chart_series
from app.graph import build_graph
from app.investigation import investigate

app = FastAPI(title=APP_NAME, version=VERSION, description="Evidence-aware supply-chain anomaly decision support; demo data is synthetic.")
app.add_middleware(CORSMiddleware, allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"], allow_methods=["GET"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def home():
    return (STATIC_DIR / "index.html").read_text(encoding="utf-8")

@app.get("/api/health")
def health():
    return {"status": "ok", "name": APP_NAME, "version": VERSION, "mode": "synthetic_demo"}

@app.get("/api/commodities")
def commodities():
    return [{"id": key, **value} for key, value in COMMODITIES.items()]

@app.get("/api/overview")
def overview():
    totals = []
    for key, value in COMMODITIES.items():
        series = chart_series(key)
        signals = compute_signals(key)
        totals.append({"id": key, "label": value["label"], "months": len(series), "flagged_months": len(signals), "latest_month": series[-1]["month"] if series else None, "latest_import_value_usd": series[-1]["import_value_usd"] if series else None})
    return {"dataset_mode": "SYNTHETIC DEMO DATA", "commodities": totals, "data_quality": data_quality_report()}

@app.get("/api/data-quality")
def quality():
    return data_quality_report()

@app.get("/api/series/{commodity}")
def series(commodity: str):
    if commodity not in COMMODITIES:
        raise HTTPException(404, "Unknown commodity")
    return chart_series(commodity)

@app.get("/api/signals/{commodity}")
def signals(commodity: str, limit: int = Query(20, ge=1, le=200)):
    if commodity not in COMMODITIES:
        raise HTTPException(404, "Unknown commodity")
    return compute_signals(commodity)[:limit]

@app.get("/api/partners/{commodity}")
def partners(commodity: str):
    if commodity not in COMMODITIES:
        raise HTTPException(404, "Unknown commodity")
    return partner_shares(commodity)

@app.get("/api/graph/{commodity}")
def graph(commodity: str):
    if commodity not in COMMODITIES:
        raise HTTPException(404, "Unknown commodity")
    return build_graph(commodity, partner_shares(commodity))

@app.get("/api/investigate/{commodity}")
def investigation(commodity: str, month: str | None = None):
    if commodity not in COMMODITIES:
        raise HTTPException(404, "Unknown commodity")
    try:
        return investigate(commodity, month)
    except ValueError as exc:
        raise HTTPException(400, str(exc))

@app.get("/api/report/{commodity}.json")
def export_json(commodity: str, month: str | None = None):
    try:
        report = investigate(commodity, month)
    except ValueError:
        raise HTTPException(404, "Unknown commodity")
    return report

@app.get("/api/report/{commodity}.csv")
def export_csv(commodity: str):
    if commodity not in COMMODITIES:
        raise HTTPException(404, "Unknown commodity")
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["month", "commodity", "import_value_usd", "quantity_tonnes", "price_usd_per_tonne", "rolling_z", "iforest_flag", "value_pct_change", "quantity_pct_change", "price_pct_change"])
    writer.writeheader()
    for row in compute_signals(commodity):
        writer.writerow({k: row.get(k) for k in writer.fieldnames})
    output.seek(0)
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=supplyshield-{commodity}-signals.csv"})
