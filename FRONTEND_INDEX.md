# NeuroAI Frontend Generation - Complete Guide Index

## 📋 Files Created for Lovable Frontend Generation

This directory now contains everything needed to generate a complete frontend for your NeuroAI platform using Lovable.

### Generated Files

1. **[LOVABLE_QUICK_PROMPT.txt](./LOVABLE_QUICK_PROMPT.txt)** ⭐ START HERE
   - **Purpose**: Quick copy-paste prompt for Lovable chat
   - **When to use**: If you want fast frontend generation with all essentials
   - **Time to read**: 2-3 minutes
   - **How to use**:
     1. Go to [Lovable](https://lovable.dev)
     2. Copy entire contents of this file
     3. Paste into Lovable chat
     4. Let it generate!

2. **[LOVABLE_PROMPT.md](./LOVABLE_PROMPT.md)** 🔍 DETAILED VERSION
   - **Purpose**: Comprehensive, detailed specification for Lovable
   - **When to use**: If you want extensive documentation and examples
   - **Time to read**: 15-20 minutes
   - **Includes**: Full API documentation, examples, design guidelines

3. **[FRONTEND_SETUP_GUIDE.md](./FRONTEND_SETUP_GUIDE.md)** 🚀 SETUP & INTEGRATION
   - **Purpose**: How to set up backend, run Lovable, and integrate
   - **When to use**: After generating with Lovable, for setup and deployment
   - **Time to read**: 10 minutes
   - **Includes**: Setup instructions, troubleshooting, TypeScript types

4. **[FRONTEND_INDEX.md](./FRONTEND_INDEX.md)** (THIS FILE)
   - **Purpose**: Navigation guide for all frontend documentation
   - **When to use**: When you're lost or need to find something

---

## 🚀 Quick Start (Choose One Path)

### Path A: I Just Want a Working Frontend (5-10 minutes)

1. Start backend: `cd backend && python manage.py runserver`
2. Copy [LOVABLE_QUICK_PROMPT.txt](./LOVABLE_QUICK_PROMPT.txt)
3. Paste into [Lovable](https://lovable.dev) chat
4. Download generated project
5. Follow [FRONTEND_SETUP_GUIDE.md](./FRONTEND_SETUP_GUIDE.md) to set up

### Path B: I Want Full Control & Details (20-30 minutes)

1. Start backend: `cd backend && python manage.py runserver`
2. Read [LOVABLE_PROMPT.md](./LOVABLE_PROMPT.md) thoroughly
3. Copy it to Lovable with modifications if desired
4. Download and customize generated project
5. Follow setup guide for integration

---

## 📚 API Endpoints Summary

### Quick Reference

| Resource           | GET List                   | GET Detail               | POST                                         |
| ------------------ | -------------------------- | ------------------------ | -------------------------------------------- |
| **Drugs**          | `/api/v1/drugs/`           | `/api/v1/drugs/{id}/`    | ❌                                           |
| **Targets**        | `/api/v1/targets/`         | `/api/v1/targets/{id}/`  | ❌                                           |
| **Pathways**       | `/api/v1/pathways/`        | `/api/v1/pathways/{id}/` | ❌                                           |
| **PathwayEffects** | `/api/v1/pathway-effects/` | ❌                       | ❌                                           |
| **Predictions**    | ❌                         | ❌                       | ✅ binding-affinity, toxicity, drug-response |
| **Simulations**    | ❌                         | ❌                       | ✅ `/api/v1/simulate/`                       |
| **System**         | `/api/v1/system/`          | ❌                       | ❌                                           |

### Full Endpoint List

```
GET    /api/v1/drugs/                              - List drugs with filters
GET    /api/v1/drugs/{id}/                         - Get drug details
GET    /api/v1/drugs/{id}/targets/                 - Get drug targets
GET    /api/v1/drugs/{id}/pathway_effects/         - Get pathway effects
GET    /api/v1/drugs/{id}/mechanism_summary/       - Get mechanism summary
GET    /api/v1/drugs/cns_viable/                   - Get CNS viable drugs

GET    /api/v1/targets/                            - List targets with filters
GET    /api/v1/targets/{id}/                       - Get target details
GET    /api/v1/targets/{id}/drugs/                 - Get drugs for target

GET    /api/v1/pathways/                           - List pathways with filters
GET    /api/v1/pathways/{id}/                      - Get pathway details
GET    /api/v1/pathways/{id}/targets/              - Get targets in pathway
GET    /api/v1/pathways/{id}/drug_effects/         - Get drug effects on pathway

GET    /api/v1/pathway-effects/                    - List pathway effects

GET    /api/v1/disease-states/                     - List disease states
GET    /api/v1/disease-states/default/             - Get default disease state
POST   /api/v1/disease-states/                     - Create disease state

POST   /api/v1/predictions/binding-affinity/       - Predict binding affinity
POST   /api/v1/predictions/toxicity/               - Assess toxicity
POST   /api/v1/predictions/drug-response/          - Comprehensive prediction
POST   /api/v1/predictions/molecule-analysis/      - Quick molecule analysis

POST   /api/v1/simulate/                           - Run simulation

GET    /api/v1/system/                             - Get system info
```

---

## 🎯 What Should Be Built

### Core Pages

- ✅ Home/Dashboard (statistics, quick links)
- ✅ Drug Browser (list, filter, search with pagination)
- ✅ Drug Detail (full info, interactions, pathways)
- ✅ Target Browser (list, filter, search)
- ✅ Target Detail (disease data, connected drugs)
- ✅ Pathway Browser (category-based browsing)
- ✅ Pathway Detail (targets, drug effects)
- ✅ Binding Affinity Predictor (form + results)
- ✅ Toxicity Assessor (form + results)
- ✅ Drug Response Predictor (comprehensive)
- ✅ Molecule Analyzer (quick analysis)
- ✅ Simulation Dashboard (baseline vs intervention)
- ✅ System Info / About

### Key Features

- ✅ Search & filtering across all browsers
- ✅ Pagination for large datasets
- ✅ Client-side error handling
- ✅ Loading indicators
- ✅ Responsive mobile design
- ✅ Color-coded safety indicators
- ✅ Confidence level displays
- ✅ Model attribution
- ✅ Prominent disclaimers

### Visualizations

- ✅ Trajectory charts (disease progression)
- ✅ Pathway impact tables
- ✅ Safety indicators
- ✅ SMILES structure display
- ✅ Network graphs (optional)

---

## 🏗️ Directory Structure (After Generation)

```
/home/daddy/Downloads/MedGemma/neuroai2/NeuroAI/
├── frontend/                          ← Generated by Lovable (goes here)
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── api/
│   │   ├── types/
│   │   └── App.tsx
│   ├── package.json
│   ├── .env
│   └── ...
│
├── backend/                           ← Existing Django backend
│   ├── core/
│   │   ├── api/
│   │   ├── models/
│   │   ├── ml/
│   │   └── ...
│   └── manage.py
│
├── android/                           ← Existing Android app
│
└── [Documentation Files]
    ├── LOVABLE_QUICK_PROMPT.txt       ← Use this for Lovable
    ├── LOVABLE_PROMPT.md              ← Or this for detailed version
    ├── FRONTEND_SETUP_GUIDE.md        ← Setup instructions
    ├── FRONTEND_INDEX.md              ← THIS FILE
    └── [Other docs]
```

---

## ⚙️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Browser (Frontend)                          │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  React 18 + TypeScript + Tailwind                          │ │
│  │  - Drug/Target/Pathway Browsers                            │ │
│  │  - Prediction Tools                                        │ │
│  │  - Simulation Dashboard                                    │ │
│  └────────────────────────────────────────────────────────────┘ │
│              ↓ HTTP/JSON API Calls                               │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  http://localhost:3000                                     │ │
└─────────────────────────────────────────────────────────────────┘

                          ↓↑ REST API

┌─────────────────────────────────────────────────────────────────┐
│                     Backend (Django)                            │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Django REST Framework                                     │ │
│  │  - ViewSets & APIViews for each endpoint                  │ │
│  │  - Serializers for data transformation                    │ │
│  └────────────────────────────────────────────────────────────┘ │
│              ↓                   ↓                                │
│  ┌──────────────────┐  ┌──────────────────────────────────────┐ │
│  │  SQLite DB       │  │  ML Models (Pre-trained)             │ │
│  │  - Drugs         │  │  - GraphDTA (binding affinity)       │ │
│  │  - Targets       │  │  - MedGemma-7B (toxicity, reasoning) │ │
│  │  - Pathways      │  │  - ESM-2 (protein embeddings)        │ │
│  │  - Simulations   │  │  - RDKit (molecular features)        │ │
│  └──────────────────┘  └──────────────────────────────────────┘ │
│  http://localhost:8000/api/v1/                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔑 Key Data Models

### Drug

```json
{
  "id": 1,
  "drugbank_id": "DB00001",
  "name": "Levodopa",
  "cns_mpo_score": 5.2,
  "cns_viable": true,
  "molecular_weight": 197.19,
  "pains_alerts": 0,
  "target_interactions": [...],
  "pathway_effects": [...]
}
```

### Target

```json
{
  "id": 1,
  "gene_symbol": "APOE",
  "protein_name": "Apolipoprotein E",
  "disease_relevance_score": 0.95,
  "is_toxicity_associated": false,
  "brain_expression_level": "high"
}
```

### Pathway

```json
{
  "id": 1,
  "name": "Neuroinflammation",
  "category": "neuroinflammation",
  "disease_relevance": "high",
  "target_count": 24
}
```

### DrugPathwayEffect

```json
{
  "id": 1,
  "drug_name": "Levodopa",
  "pathway_name": "Dopamine Synthesis",
  "perturbation_score": 0.85,
  "direction": "activation",
  "disease_impact": "beneficial",
  "confidence": 0.92
}
```

---

## ⚡ Performance Considerations

### API Response Times

- **GET /drugs/**: ~200ms (paginated, filtered)
- **GET /drugs/{id}/**: ~400ms (includes related data)
- **POST /predictions/binding-affinity/**: ~10-25s (first call loads model)
- **POST /predictions/binding-affinity/**: ~2-5s (subsequent calls)
- **POST /simulate/**: ~3-8s (depends on time steps)

### Frontend Optimizations

- Implement pagination (20 items per page default)
- Cache prediction models after first use
- Show loading indicators for long operations
- Debounce search inputs (300ms)
- Use React.memo for expensive components
- Lazy load route components

---

## 🎨 Design System

### Colors

- **Primary**: #0066CC (Science/Trust)
- **Success**: #00AA44 (Beneficial)
- **Warning**: #FF8800 (Caution)
- **Danger**: #CC0000 (Harmful)
- **Neutral**: #666666 (Info)
- **Background**: #F5F5F5
- **Cards**: #FFFFFF

### Spacing

- Use Tailwind's 4px base unit
- Standard gaps: 4px, 8px, 16px, 24px, 32px

### Typography

- **Headlines**: Bold, sans-serif
- **Body**: Regular, sans-serif
- **Monospace**: For SMILES, IDs, technical data

---

## 🚨 Important Guardrails

### Must Display Disclaimers

> "This is exploratory AI, NOT clinical prediction"
> "Results should be reviewed by domain experts"
> "No diagnostic or treatment recommendations are made"

Display these on ALL prediction pages and simulation results.

### Safety Indicators

- Show confidence levels (high/medium/low)
- Display model attribution (e.g., "GraphDTA (pre-trained)")
- Highlight toxicity warnings prominently
- Show uncertainty bounds in simulations
- Link to safety concerns and off-target effects

### Data Accuracy

- Drug data from DrugBank, ChEMBL
- Targets from UniProt, DisGeNET
- Pathways from KEGG, Reactome
- All predictions are exploratory only

---

## 🔗 Useful Links

- **Live API**: http://localhost:8000/api/v1/ (when backend running)
- **Django Admin**: http://localhost:8000/admin/
- **Lovable**: https://lovable.dev
- **React Docs**: https://react.dev
- **Tailwind CSS**: https://tailwindcss.com
- **Django REST**: https://www.django-rest-framework.org/

---

## 📞 Getting Help

### Common Issues

**Q: Frontend can't connect to backend**

- Check: `curl http://localhost:8000/api/v1/system/`
- Verify CORS settings in Django
- Check api base URL in .env file

**Q: Predictions are very slow on first call**

- Normal! ML models take 10-15s to load on first request
- Display loading indicator with estimated wait
- Subsequent calls are 2-5s

**Q: Pagination isn't working**

- Ensure query params: `?page=1`
- Responses include `count`, `next`, `previous`, `results`

**Q: Environment variables not loading**

- Restart dev server after changing .env
- Check file is named exactly `.env`
- Restart webpack dev server

---

## 📝 Next Steps

1. **Choose your prompt**: Quick or Detailed?
2. **Start backend**: `python manage.py runserver`
3. **Go to Lovable**: https://lovable.dev
4. **Copy & Paste**: Your chosen prompt
5. **Generate**: Let Lovable create the frontend
6. **Download**: Get the generated project
7. **Setup**: Follow [FRONTEND_SETUP_GUIDE.md](./FRONTEND_SETUP_GUIDE.md)
8. **Run**: `npm install && npm start`
9. **Test**: http://localhost:3000

---

## 📄 Document Glossary

| Document                   | Purpose             | Read When                   |
| -------------------------- | ------------------- | --------------------------- |
| LOVABLE_QUICK_PROMPT.txt   | Fast copy-paste     | Starting Lovable generation |
| LOVABLE_PROMPT.md          | Complete spec       | Need full documentation     |
| FRONTEND_SETUP_GUIDE.md    | Setup & integration | After Lovable generation    |
| FRONTEND_INDEX.md          | Navigation help     | When lost or searching      |
| README.md                  | Project overview    | Learning about NeuroAI      |
| TECHNICAL_DOCUMENTATION.md | Deep dive           | Understanding architecture  |

---

**Created**: February 25, 2026  
**For**: NeuroAI Frontend Generation via Lovable  
**Status**: Ready to use ✅
