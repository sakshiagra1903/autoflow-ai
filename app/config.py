from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
STATIC_DIR = PROJECT_ROOT / "frontend"
TRADE_DATA = DATA_DIR / "sample_trade_monthly.csv"
PRICE_DATA = DATA_DIR / "sample_commodity_prices.csv"
EVIDENCE_DATA = DATA_DIR / "evidence_sources.json"
APP_NAME = "SupplyShield AI"
VERSION = "1.0.0"
