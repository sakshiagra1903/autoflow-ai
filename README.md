# SupplyShield AI
### India's Supply Chain Early-Warning & Impact Intelligence Platform

SupplyShield AI is an AI/ML research project designed to identify unusual monthly import movements, analyze partner-country concentration, explore downstream industry dependencies, and generate transparent, evidence-aware investigation reports.

The platform combines statistical anomaly detection, supply-chain graph analysis, a REST API, and an interactive dashboard to support supply-chain research and risk analysis.

> **Disclaimer:** This is an educational decision-support prototype. The bundled trade and price datasets are synthetic demonstration data, not official statistics. Anomaly signals do not prove shortages, predict prices with certainty, or establish real-world supply disruptions.

## Key Features

- **Anomaly Detection:** Rolling z-score baseline and Isolation Forest comparison.
- **Feature Engineering:** Monthly percentage changes, rolling statistics, import values, quantities, and reference prices.
- **Partner Concentration Analysis:** Calculate each partner's share of the selected commodity's import value.
- **Supply-Chain Dependency Graph:** Explore relationships between partner countries, commodities, and downstream industries.
- **Evidence-Aware Investigations:** Structured analysis, impact assessment, evidence review, and verification steps.
- **Explainable Results:** Display reasons behind flagged observations and clearly identify unsupported claims.
- **Data Quality Monitoring:** Inspect monthly coverage, missing values, and dataset provenance.
- **Interactive Dashboard:** Explore commodity trends, anomaly signals, dependency graphs, and investigation history within the application.
- **Report Export:** Export investigation results as JSON and flagged signals as CSV.
- **REST API:** Access core application features through FastAPI endpoints.
- **Reproducible Testing:** Automated API tests and deterministic model configuration.

## Technology Stack

| Layer | Technologies |
|---|---|
| Programming Language | Python |
| Backend | FastAPI, Uvicorn |
| Data Processing | pandas, NumPy |
| Machine Learning | scikit-learn |
| Graph Analysis | NetworkX |
| Frontend | HTML, CSS, JavaScript |
| Data Storage | CSV and JSON files |
| Testing | pytest, FastAPI TestClient |
| Deployment | Docker, Docker Compose (optional) |

## System Architecture

```text
Monthly Trade & Price Data
           |
           v
    Data Validation
           |
           v
   Feature Engineering
           |
           +-------------------+
           |                   |
           v                   v
   Rolling Z-Score      Isolation Forest
           |                   |
           +---------+---------+
                     |
                     v
             Anomaly Signals
                     |
          +----------+----------+
          |                     |
          v                     v
  Partner Concentration   Dependency Graph
          |                     |
          +----------+----------+
                     |
                     v
          Evidence-Aware Workflow
       Analysis -> Impact -> Evidence
                     |
                     v
                Verification
                     |
                     v
             FastAPI REST API
                     |
                     v
             Interactive Dashboard
```

The current investigation workflow uses deterministic Python logic and structured steps. LangGraph orchestration and live LLM-based agents are potential future enhancements, not implemented features in this release.

## Supported Commodities

| Commodity | HS Classification |
|---|---|
| Crude Oil | HS 2709 |
| Refined Copper | HS 7403 and relevant Chapter 74 codes |
| Fertilizers | HS Chapter 31 |

The current dataset covers monthly demonstration records from January 2015 through December 2024.

## Getting Started

### Prerequisites

- Python 3.12 recommended
- Git
- A modern web browser
- Internet access for installing Python dependencies

No paid API key is required to run the bundled demonstration.

### Installation on Windows

**1. Clone the repository**

```powershell
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY
```

Replace the repository URL with your actual GitHub repository URL.

**2. Create a virtual environment**

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**3. Install dependencies**

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**4. Start the application**

```powershell
python -m uvicorn app.main:app --reload
```

**5. Open the application**

- Dashboard: http://127.0.0.1:8000
- Interactive API documentation: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/api/health

Keep the terminal running while using the dashboard.

### Run with Docker (Optional)

If Docker Desktop is installed and running:

```bash
docker compose up --build
```

Open http://127.0.0.1:8000.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Check application status |
| GET | `/api/commodities` | List supported commodities |
| GET | `/api/overview` | Dashboard summary and data quality |
| GET | `/api/data-quality` | Inspect data coverage and missing values |
| GET | `/api/series/{commodity}` | Retrieve monthly time-series data |
| GET | `/api/signals/{commodity}` | Retrieve flagged anomaly signals |
| GET | `/api/partners/{commodity}` | Calculate partner concentration |
| GET | `/api/graph/{commodity}` | Retrieve dependency graph data |
| GET | `/api/investigate/{commodity}` | Run an investigation |
| GET | `/api/report/{commodity}.json` | Export an investigation report |
| GET | `/api/report/{commodity}.csv` | Export flagged signals |

Supported commodity identifiers:

- `crude_oil`
- `copper`
- `fertilizers`

Example request:

```text
http://127.0.0.1:8000/api/investigate/crude_oil
```

## Data Sources and API Requirements

The application currently uses bundled CSV and JSON files. External APIs are not required for the core demonstration.

For future live-data integration:

- **UN Comtrade:** Import values, quantities, and partner-country information. API access requirements and limits depend on the service and query.
- **World Bank Commodity Markets:** Reference commodity-price data.
- **DGCIS:** Potential source for cross-checking Indian trade statistics, subject to data access and applicable terms.

Reference links:

- [UN Comtrade API](https://comtradeapi.un.org/)
- [World Bank Commodity Markets](https://www.worldbank.org/en/research/commodity-markets)
- [Directorate General of Commercial Intelligence and Statistics](https://www.dgciskol.gov.in/)

These integrations are not yet implemented as live ingestion pipelines. Replace the demonstration datasets only after validating the source, publication date, reporting period, units, and licensing conditions.

## Machine Learning Methodology

### 1. Rolling Z-Score

Measures how unusual a monthly import value is compared with its rolling historical baseline.

An absolute z-score of at least 2 is used as a review threshold when sufficient historical data is available.

### 2. Isolation Forest

An unsupervised anomaly-detection model provides a comparison signal based on the numerical features.

### 3. Feature Engineering

The pipeline calculates:

- Month-over-month import-value changes
- Quantity changes
- Reference-price changes
- Rolling statistical features
- Partner-country concentration

These techniques identify statistically unusual observations. They do not establish the cause of a movement or prove that a supply disruption occurred.

## Evaluation and Limitations

The project includes automated API tests. A full empirical evaluation of anomaly-detection accuracy against a dated, independently labelled disruption benchmark has not yet been completed.

Future evaluation should include:

- Precision, recall, F1-score, and false-positive rate
- Point-in-time historical replay to reduce future-data leakage
- Retrieval Recall@5 and evidence coverage after document retrieval is implemented
- Claim-support rate and citation correctness
- Comparison against simple statistical and retrieval-based baselines

Other limitations include synthetic sample data, the absence of live news retrieval, and downstream industry relationships that require source validation.

## Project Structure

```text
SupplyShield-AI/
├── app/
│   ├── config.py
│   ├── data.py
│   ├── graph.py
│   ├── investigation.py
│   ├── main.py
│   └── risk.py
├── data/
│   ├── README.md
│   ├── evidence_sources.json
│   ├── sample_commodity_prices.csv
│   └── sample_trade_monthly.csv
├── frontend/
│   ├── app.js
│   ├── index.html
│   └── styles.css
├── tests/
│   └── test_api.py
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Run Tests

```powershell
pytest -q
```

## Future Development

- Integrate official monthly trade and commodity-price datasets.
- Implement point-in-time historical evaluation.
- Add dated-document retrieval with source-level citations.
- Introduce LangGraph-based investigation orchestration.
- Add an optional open-weight or hosted LLM with structured outputs and verification.
- Expand evidence-backed industry dependency relationships.
- Add scheduled monitoring and alerts.

## Responsible Use

SupplyShield AI is intended for educational research, experimentation, and decision support. Results should be independently verified before operational, procurement, policy, or financial decisions.

<img width="1920" height="1080" alt="Screenshot 2026-10-11 164231" src="https://github.com/user-attachments/assets/7b4f5d76-f515-4e4b-8828-e904428dfa8e" />
<img width="1920" height="1080" alt="Screenshot 2026-10-11 164219" src="https://github.com/user-attachments/assets/d05303dc-0c77-4508-b4b9-378f9b7cbddd" />
<img width="1920" height="1080" alt="Screenshot 2026-10-11 164206" src="https://github.com/user-attachments/assets/49775306-ef40-4784-8afc-1ea12934bae4" />
<img width="1920" height="1080" alt="Screenshot 2026-10-11 164130" src="https://github.com/user-attachments/assets/54400c1f-0797-41b2-833f-fa0d4c9b91df" />


