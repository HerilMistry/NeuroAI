# NeuroDegenRx

A mechanism-aware decision support platform for neurodegenerative drug discovery.

> **⚠️ Research Use Only**
> This platform does NOT provide clinical predictions, diagnostic recommendations, or medical advice.
> It is an early-stage reasoning and triage system for improving decision quality before preclinical studies.

## Philosophy

- **Biological plausibility over prediction** - Model known mechanisms, not clinical outcomes
- **Explicit uncertainty** - All scores include confidence indicators
- **Safety first** - Toxicity-associated targets are prominently flagged
- **Transparent logic** - Rule-based scoring with visible parameters
- **Auditability** - All calculations are traceable

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 15+
- Docker (optional)

### With Docker

```bash
docker-compose up
```

Access:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api/v1/

### Manual Setup

#### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Set environment variables
set DATABASE_URL=postgres://user:pass@localhost:5432/neurodegenrx
set DEBUG=True

# Initialize database
python manage.py migrate
python manage.py seed_sample_data  # Optional: add sample data

# Run server
python manage.py runserver
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
neurodegenrx/
├── backend/
│   ├── core/                   # Django app with models and logic
│   │   ├── models.py           # Drug, Target, Pathway, etc.
│   │   ├── logic.py            # BBB scoring, toxicity, perturbation
│   │   ├── simulation.py       # Disease progression simulation
│   │   └── api/                # DRF serializers and views
│   └── data_files/             # Local data files (gitignored)
├── frontend/
│   ├── src/
│   │   ├── pages/              # Dashboard, DrugExplorer, etc.
│   │   ├── components/         # Layout, Sidebar, Header
│   │   ├── api/                # API client with TypeScript types
│   │   └── store/              # Zustand state management
│   └── ...
└── docker-compose.yml
```

## Data Ingestion

Place data files in `backend/data_files/` and run:

```bash
python manage.py ingest_drugbank --file data_files/drugbank.csv --version 5.1.10
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/drugs/` | List drugs with CNS viability |
| `GET /api/v1/drugs/{id}/` | Drug details with targets and pathways |
| `GET /api/v1/pathways/` | Disease-relevant pathways |
| `POST /api/v1/simulate/` | Run disease progression simulation |

## Core Features

1. **CNS MPO Scoring** - Rule-based BBB penetration assessment
2. **Toxicity Flagging** - Known toxicity-associated target detection
3. **Pathway Perturbation** - Drug effects on disease pathways
4. **Progression Simulation** - Mechanistic exploration (NOT clinical prediction)

## License

Research use only. Not for clinical or diagnostic purposes.
