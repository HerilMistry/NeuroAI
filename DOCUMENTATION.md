# NeuroDegenRx Documentation

## Overview

**NeuroDegenRx** is a mechanism-aware decision support platform for neurodegenerative drug discovery.

> **Research Use Only:** This platform does **not** provide clinical predictions, diagnostic recommendations, or medical advice. It is an early-stage reasoning and triage system for improving decision quality before preclinical studies.

---

## Architecture

- **Backend:** Django + Django REST Framework (Python)
- **Frontend:** React (Vite, TypeScript, Zustand, TailwindCSS)
- **Database:** PostgreSQL (default), SQLite (dev option)
- **Containerization:** Docker Compose for full-stack orchestration
- **LLM Integration:** MedGemma via vllm for efficient local inference

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

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 15+
- Docker (recommended)
- CUDA-enabled GPU (for MedGemma local inference)

### With Docker

```bash
docker-compose up
```
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api/v1/

### Manual Setup

#### Backend

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
cd frontend
npm install
npm run dev
```
- Access at http://localhost:5173

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

## Backend Details

- **Framework:** Django 5+, Django REST Framework, django-filter, django-cors-headers, whitenoise
- **API:** Versioned under `/api/v1/`
- **Models:** Drug, Target, Pathway, DiseaseState, DrugTarget, DrugPathwayEffect, Provenance
- **Logic:** CNS MPO scoring, toxicity filtering, pathway perturbation, simulation
- **Management Commands:**  
  - `ingest_drugbank` — Ingest DrugBank data  
  - `seed_sample_data` — Populate with sample data for development

### MedGemma Integration

**MedGemma** is integrated for advanced biomedical text analysis and mechanism summarization. The model is locally inferenceable using vllm for efficient GPU inference.

- **Module:** `core.medgemma.inference`
- **Example Use:** Drug mechanism summarization, literature evidence extraction, pathway annotation
- **Dependencies:** `vllm`

#### API Endpoint

`GET /api/v1/drugs/{id}/mechanism_summary/`

Returns a MedGemma-generated summary of the drug's mechanism of action.

**Example Response:**
```json
{
  "drug": "Donepezil",
  "mechanism_summary": "Donepezil is an acetylcholinesterase inhibitor that increases acetylcholine levels in the brain, improving cognitive function in Alzheimer's disease."
}
```

### API Endpoints

| Endpoint                  | Description                                   |
|---------------------------|-----------------------------------------------|
| `GET /api/v1/drugs/`      | List drugs with CNS viability                 |
| `GET /api/v1/drugs/{id}/` | Drug details with targets and pathways        |
| `GET /api/v1/drugs/{id}/mechanism_summary/` | MedGemma mechanism summary |
| `GET /api/v1/pathways/`   | Disease-relevant pathways                     |
| `POST /api/v1/simulate/`  | Run disease progression simulation            |
| `GET /api/v1/system-info/`| Platform info, statistics, disclaimers        |

---

## Frontend Details

- **Framework:** React, Vite, TypeScript, Zustand, TailwindCSS
- **Pages:** Dashboard, DrugExplorer, DrugDetail, Pathways, Simulation
- **Components:** Header, Sidebar, Layout, StatCard, MechanismItem, ApproachItem
- **API Client:** Typed API calls to backend
- **Store:** Zustand for state management

---

## Core Features

1. **CNS MPO Scoring:** Rule-based blood-brain barrier penetration assessment
2. **Toxicity Flagging:** Detection of known toxicity-associated targets
3. **Pathway Perturbation:** Drug effects on disease pathways
4. **Progression Simulation:** Mechanistic exploration (not clinical prediction)
5. **MedGemma Summarization:** Advanced mechanism summaries using LLM

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

---

**For more details, see the in-code docstrings and comments throughout the repository.**
If you need API schema or further technical details, see the backend API code or ask for more specifics.
