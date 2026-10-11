"""Validated data access for the demo dataset. Demo records are explicitly labelled."""
from __future__ import annotations
import json
import pandas as pd
from app.config import TRADE_DATA, PRICE_DATA, EVIDENCE_DATA

REQUIRED_TRADE = {"month", "commodity", "partner", "import_value_usd", "quantity_tonnes", "source", "data_period"}
REQUIRED_PRICE = {"month", "commodity", "price_usd_per_tonne", "source", "data_period"}

def _load_csv(path, required):
    df = pd.read_csv(path)
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{path.name} is missing required columns: {sorted(missing)}")
    df["month"] = pd.to_datetime(df["month"], errors="coerce")
    if df["month"].isna().any():
        raise ValueError(f"{path.name} contains invalid month values")
    return df

def load_trade() -> pd.DataFrame:
    df = _load_csv(TRADE_DATA, REQUIRED_TRADE)
    for col in ("import_value_usd", "quantity_tonnes"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

def load_prices() -> pd.DataFrame:
    df = _load_csv(PRICE_DATA, REQUIRED_PRICE)
    df["price_usd_per_tonne"] = pd.to_numeric(df["price_usd_per_tonne"], errors="coerce")
    return df

def load_evidence() -> list[dict]:
    with EVIDENCE_DATA.open(encoding="utf-8") as f:
        return json.load(f)

def data_quality_report() -> dict:
    trade, prices = load_trade(), load_prices()
    expected = pd.period_range("2015-01", "2024-12", freq="M")
    observed = set(trade["month"].dt.to_period("M"))
    price_observed = set(prices["month"].dt.to_period("M"))
    return {
        "dataset_mode": "DEMO / SYNTHETIC — not official trade statistics",
        "trade_rows": int(len(trade)),
        "price_rows": int(len(prices)),
        "trade_missing_numeric_cells": int(trade[["import_value_usd", "quantity_tonnes"]].isna().sum().sum()),
        "price_missing_cells": int(prices["price_usd_per_tonne"].isna().sum()),
        "trade_month_coverage": f"{trade['month'].min():%Y-%m} to {trade['month'].max():%Y-%m}",
        "price_month_coverage": f"{prices['month'].min():%Y-%m} to {prices['month'].max():%Y-%m}",
        "missing_trade_months_in_2015_2024": int(len(set(expected) - observed)),
        "missing_price_months_in_2015_2024": int(len(set(expected) - price_observed)),
        "retrieved_at_utc": "Bundled with project; no live retrieval performed"
    }
