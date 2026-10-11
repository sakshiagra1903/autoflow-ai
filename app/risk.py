"""Transparent anomaly baselines; anomalies are signals, not proof of disruption."""
from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from app.data import load_trade, load_prices

COMMODITIES = {
    "crude_oil": {"label": "Crude oil", "hs_codes": "2709"},
    "copper": {"label": "Refined copper", "hs_codes": "7403 / related Chapter 74"},
    "fertilizers": {"label": "Fertilizers", "hs_codes": "Chapter 31"},
}

def monthly_series(commodity: str) -> pd.DataFrame:
    trade = load_trade()
    trade = trade[trade.commodity == commodity].copy()
    if trade.empty:
        return pd.DataFrame(columns=["month", "import_value_usd", "quantity_tonnes", "price_usd_per_tonne"])
    monthly = trade.groupby("month", as_index=False).agg(
        import_value_usd=("import_value_usd", "sum"),
        quantity_tonnes=("quantity_tonnes", "sum"),
        partner_count=("partner", "nunique"),
    )
    prices = load_prices()
    prices = prices[prices.commodity == commodity][["month", "price_usd_per_tonne"]]
    return monthly.merge(prices, on="month", how="left").sort_values("month")

def compute_signals(commodity: str) -> list[dict]:
    df = monthly_series(commodity)
    if df.empty:
        return []
    df["value_pct_change"] = df["import_value_usd"].pct_change() * 100
    df["quantity_pct_change"] = df["quantity_tonnes"].pct_change() * 100
    df["price_pct_change"] = df["price_usd_per_tonne"].pct_change() * 100
    rolling_mean = df["import_value_usd"].rolling(12, min_periods=6).mean()
    rolling_std = df["import_value_usd"].rolling(12, min_periods=6).std(ddof=0).replace(0, np.nan)
    df["rolling_z"] = (df["import_value_usd"] - rolling_mean) / rolling_std
    # Fit only on numeric features and return an independent comparison label.
    features = df[["import_value_usd", "quantity_tonnes", "price_usd_per_tonne"]].replace([np.inf, -np.inf], np.nan)
    features = features.fillna(features.median()).fillna(0)
    if len(df) >= 24:
        model = IsolationForest(n_estimators=150, contamination=0.06, random_state=42)
        df["iforest_flag"] = model.fit_predict(features) == -1
        df["iforest_score"] = -model.score_samples(features)
    else:
        df["iforest_flag"] = False
        df["iforest_score"] = 0.0
    # Avoid early rolling warm-up being presented as a statistically stable z-score.
    df["signal"] = (df["rolling_z"].abs() >= 2.0) | df["iforest_flag"]
    results = []
    for _, row in df.iterrows():
        if not bool(row["signal"]):
            continue
        reasons = []
        if pd.notna(row["rolling_z"]) and abs(float(row["rolling_z"])) >= 2:
            reasons.append(f"import value is {float(row['rolling_z']):+.2f} rolling standard deviations from its 12-month baseline")
        if bool(row["iforest_flag"]):
            reasons.append("Isolation Forest also labels this month unusual")
        for field, label in [("value_pct_change", "import value"), ("quantity_pct_change", "quantity"), ("price_pct_change", "reference price")]:
            if pd.notna(row[field]):
                reasons.append(f"{label} changed {float(row[field]):+.1f}% month over month")
        results.append({
            "month": row["month"].strftime("%Y-%m"),
            "commodity": commodity,
            "commodity_label": COMMODITIES[commodity]["label"],
            "import_value_usd": round(float(row["import_value_usd"]), 2),
            "quantity_tonnes": round(float(row["quantity_tonnes"]), 2),
            "price_usd_per_tonne": None if pd.isna(row["price_usd_per_tonne"]) else round(float(row["price_usd_per_tonne"]), 2),
            "rolling_z": None if pd.isna(row["rolling_z"]) else round(float(row["rolling_z"]), 3),
            "iforest_flag": bool(row["iforest_flag"]),
            "iforest_score": round(float(row["iforest_score"]), 4),
            "value_pct_change": None if pd.isna(row["value_pct_change"]) else round(float(row["value_pct_change"]), 2),
            "quantity_pct_change": None if pd.isna(row["quantity_pct_change"]) else round(float(row["quantity_pct_change"]), 2),
            "price_pct_change": None if pd.isna(row["price_pct_change"]) else round(float(row["price_pct_change"]), 2),
            "explanation": reasons,
            "source_note": "Synthetic demo data. This signal is not evidence of a real disruption."
        })
    return sorted(results, key=lambda x: x["month"], reverse=True)

def partner_shares(commodity: str) -> list[dict]:
    trade = load_trade()
    df = trade[trade.commodity == commodity].groupby("partner", as_index=False)["import_value_usd"].sum()
    if df.empty:
        return []
    total = df.import_value_usd.sum()
    df["share_pct"] = df.import_value_usd / total * 100 if total else 0
    return [{"partner": r["partner"], "import_value_usd": round(float(r["import_value_usd"]), 2), "share_pct": round(float(r["share_pct"]), 2)} for r in df.sort_values("import_value_usd", ascending=False).to_dict("records")]

def chart_series(commodity: str) -> list[dict]:
    df = monthly_series(commodity)
    return [{
        "month": r["month"].strftime("%Y-%m"),
        "import_value_usd": round(float(r["import_value_usd"]), 2),
        "quantity_tonnes": round(float(r["quantity_tonnes"]), 2),
        "price_usd_per_tonne": None if pd.isna(r["price_usd_per_tonne"]) else round(float(r["price_usd_per_tonne"]), 2),
    } for r in df.to_dict("records")]
