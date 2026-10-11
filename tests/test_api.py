from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_commodities():
    r = client.get("/api/commodities")
    assert r.status_code == 200
    assert {x["id"] for x in r.json()} == {"crude_oil", "copper", "fertilizers"}

def test_series_has_monthly_data():
    r = client.get("/api/series/copper")
    assert r.status_code == 200
    assert len(r.json()) == 120
    assert r.json()[0]["month"] == "2015-01"

def test_investigation_discloses_demo_data():
    r = client.get("/api/investigate/crude_oil")
    assert r.status_code == 200
    body = r.json()
    assert "synthetic" in body["summary"].lower()
    assert body["workflow_trace"][-1]["status"] in {"abstained", "insufficient_evidence"}

def test_unknown_commodity_is_rejected():
    assert client.get("/api/series/gold").status_code == 404

def test_report_export():
    assert client.get("/api/report/copper.json").status_code == 200
    assert client.get("/api/report/copper.csv").status_code == 200
