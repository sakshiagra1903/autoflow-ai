"""A deterministic, auditable investigation workflow that runs without a paid LLM."""
from datetime import datetime, timezone
from app.risk import COMMODITIES, compute_signals, partner_shares
from app.data import load_evidence
from app.graph import build_graph, dependency_path

def investigate(commodity: str, month: str | None = None) -> dict:
    if commodity not in COMMODITIES:
        raise ValueError(f"Unsupported commodity: {commodity}")
    signals = compute_signals(commodity)
    signal = next((s for s in signals if s["month"] == month), None) if month else (signals[0] if signals else None)
    partners = partner_shares(commodity)
    graph = build_graph(commodity, partners)
    evidence = [e for e in load_evidence() if e.get("commodity") in (commodity, "all")]
    if signal is None:
        status = "insufficient_evidence"
        summary = "No flagged month was found for the selected criteria. This does not prove the absence of risk."
        findings = []
    else:
        status = "review_required"
        summary = f"A statistical anomaly signal was found for {COMMODITIES[commodity]['label']} in {signal['month']}. It warrants review; the underlying values are synthetic demo data and do not establish a shortage or real-world disruption."
        findings = [
            {"claim": f"Import value for {signal['month']} was ${signal['import_value_usd']:,.0f} in the bundled dataset.", "support": "sample_trade_monthly.csv", "verified": False, "reason": "The bundled dataset is synthetic and must not be treated as official statistics."},
            {"claim": f"{len(partners)} partner countries appear in the selected commodity dataset.", "support": "sample_trade_monthly.csv", "verified": False, "reason": "Partner mix is illustrative synthetic data."}
        ]
    # The bundled sources are context/evaluation fixtures, not evidence that a real event happened.
    return {
        "report_id": f"SS-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "commodity": commodity,
        "commodity_label": COMMODITIES[commodity]["label"],
        "selected_month": signal["month"] if signal else month,
        "status": status,
        "risk_level": "Review" if signal else "Unclassified",
        "summary": summary,
        "signal": signal,
        "partner_shares": partners,
        "dependency_graph": graph,
        "dependency_paths": [dependency_path(commodity, n["label"], graph) for n in graph["nodes"] if n["kind"] == "industry"],
        "claims": findings,
        "evidence_sources": evidence,
        "workflow_trace": [
            {"step": "analysis", "status": "completed", "detail": "Computed monthly deltas, rolling z-score and Isolation Forest comparison."},
            {"step": "impact", "status": "completed", "detail": "Traversed partner-to-commodity and commodity-to-industry graph; assumptions labelled."},
            {"step": "evidence", "status": "completed", "detail": f"Loaded {len(evidence)} dated evidence fixture(s); none establishes a live disruption."},
            {"step": "verification", "status": "abstained" if signal else "insufficient_evidence", "detail": "Real-world claim withheld because bundled demo records are synthetic and dated event evidence is not connected."}
        ],
        "limitations": [
            "Educational decision-support only; not a shortage, price or investment prediction.",
            "Bundled trade and price records are synthetic demo data, not official UN Comtrade or World Bank data.",
            "Industry dependency edges are assumptions until backed by a dated source.",
            "No live web/news retrieval was performed for this report."
        ]
    }
