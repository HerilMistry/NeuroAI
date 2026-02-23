# NeuroDegenRx

A mechanism-aware decision support platform for neurodegenerative drug discovery.

> **⚠️ Research Use Only**
> This platform does NOT provide clinical predictions, diagnostic recommendations, or medical advice.
> It is an early-stage reasoning and triage system for improving decision quality before preclinical studies.

---

## Key Philosophy

- **Biological plausibility over prediction**: Model known mechanisms, not clinical outcomes
- **Explicit uncertainty**: All scores include confidence indicators
- **Safety first**: Toxicity-associated targets are prominently flagged
- **Transparent logic**: Rule-based scoring with visible parameters
- **Auditability**: All calculations are traceable

---

## Quick Start

### Easiest Way: Unified Startup Script

```bash
./run_project.sh
```

This interactive script lets you choose:
1. **Run Backend Only** - Local SQLite development
2. **Run Frontend Only** - Requires backend running
3. **Run Both** - Backend + Frontend (requires 2 terminals)
4. **Run with Docker Compose** - Full stack (PostgreSQL, recommended)
5. **Check System Requirements** - Verify all dependencies

### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 15+ (optional, for Docker mode)
- Docker (recommended for full stack)
- CUDA-enabled GPU (optional, for MedGemma local inference)

### Access URLs

Once running:
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000/api/v1
- **Admin Panel:** http://localhost:8000/admin

### Manual Setup (Alternative)

#### Backend

```bash
./run_backend.sh
```

Or manually:
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set environment variables (PostgreSQL)
export POSTGRES_DB=neurodegenrx
export POSTGRES_USER=neurodegenrx
export POSTGRES_PASSWORD=neurodegenrx_dev
export POSTGRES_HOST=localhost
export DEBUG=True

# Or use SQLite for development:
export USE_SQLITE=true

python manage.py migrate
python manage.py seed_sample_data  # Optional: add sample data
python manage.py runserver
```

#### Frontend

```bash
./run_frontend.sh
```

Or manually:
```bash
cd frontend
npm install
npm run dev
```

---

## MedGemma Integration

MedGemma is integrated for advanced biomedical text analysis and mechanism summarization. The model is locally inferenceable using vllm for efficient GPU inference.

- **Module:** `core.medgemma.inference`
- **API Endpoint:** `GET /api/v1/drugs/{id}/mechanism_summary/`
- **Dependencies:** `vllm`

---

## Project Structure

```
neurodegenrx/
├── backend/
│   ├── core/                   # Django app: models, logic, APIs
│   │   ├── models/             # Drug, Target, Pathway, etc.
│   │   ├── logic/              # BBB scoring, toxicity, perturbation
│   │   ├── simulations/        # Disease progression simulation
│   │   └── api/                # DRF serializers and views
│   ├── medgemma/               # MedGemma integration for local inference
│   ├── data_files/             # Local data files (gitignored)
│   └── management/commands/    # Data ingestion, seeding
├── frontend/
│   ├── src/
│   │   ├── pages/              # Dashboard, DrugExplorer, etc.
│   │   ├── components/         # Layout, Sidebar, Header
│   │   ├── api/                # API client (TypeScript)
│   │   └── store/              # Zustand state management
└── docker-compose.yml
```

---

## Data Ingestion

Place data files in `backend/data_files/`:

- `drugbank.xml` or `drugbank.csv` - DrugBank export
- `chembl_compounds.csv` - ChEMBL compound data
- `disgenet_gene_disease.csv` - DisGeNET associations

**Ingestion commands:**
```bash
python manage.py ingest_drugbank --file data_files/drugbank.csv --version 5.1.10
python manage.py seed_sample_data  # For development only
```

---

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/drugs/` | List drugs with CNS viability |
| `GET /api/v1/drugs/{id}/` | Drug details with targets and pathways |
| `GET /api/v1/drugs/{id}/mechanism_summary/` | MedGemma mechanism summary |
| `GET /api/v1/pathways/` | Disease-relevant pathways |
| `POST /api/v1/simulate/` | Run disease progression simulation |

---

## Core Features

1. **CNS MPO Scoring** - Rule-based BBB penetration assessment
2. **Toxicity Flagging** - Known toxicity-associated target detection
3. **Pathway Perturbation** - Drug effects on disease pathways
4. **Progression Simulation** - Mechanistic exploration (NOT clinical prediction)
5. **MedGemma Summarization** - Advanced mechanism summaries using LLM

---

## Development & Contribution

- Use Docker Compose for easiest setup.
- For backend-only development, use the provided `run_backend.sh` script (uses SQLite).
- Data files should be placed in `backend/data_files/` and are gitignored.
- See `backend/data_files/README.md` for data expectations.
- Extend models and logic in `backend/core/` as needed.
- Frontend code is in `frontend/src/`.

---

## Testing

- Backend: Use Django's test framework (`python manage.py test`)
- Frontend: Add tests with your preferred React testing library

---

## Deployment

- Production deployment should use Gunicorn (see backend Dockerfile).
- Static files are handled by Whitenoise.
- Set appropriate environment variables for production (disable DEBUG, set allowed hosts, use secure secrets).

---

## License

Research use only. Not for clinical or diagnostic purposes.
