# NeuroAI Frontend - Lovable Prompt

## Project Overview

**NeuroAI** is a multimodal AI platform for computational drug discovery focused on neurodegenerative diseases (Alzheimer's, Parkinson's, ALS). This is a **pre-trained models only** architecture using:

- **GraphDTA** for binding affinity predictions
- **MedGemma-7B** for toxicity assessment and medical reasoning
- **ESM-2-33M** for protein embeddings
- **RDKit** for molecular feature extraction

All predictions are **exploratory and NOT clinically validated**.

---

## Backend API Configuration

**Base URL**: `http://localhost:8000/api/v1/`  
**Framework**: Django REST Framework  
**Authentication**: None (for development)  
**Response Format**: JSON

---

## API Endpoints

### 1. Drug Management

#### List All Drugs

```
GET /api/v1/drugs/
```

**Query Parameters:**

- `search`: Search by name, drugbank_id, or chembl_id
- `cns_viable`: Filter by CNS viability (true/false)
- `is_approved`: Filter by approval status (true/false)
- `ordering`: Sort by name, cns_mpo_score, or molecular_weight
- `page`: Pagination (default page size: 20)

**Response Example:**

```json
{
  "count": 150,
  "next": "http://localhost:8000/api/v1/drugs/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "drugbank_id": "DB00001",
      "chembl_id": "CHEMBL1234",
      "name": "Levodopa",
      "is_approved": true,
      "molecular_weight": 197.19,
      "logp": -1.45,
      "cns_mpo_score": 5.2,
      "cns_viable": true,
      "pains_alerts": 0
    }
  ]
}
```

**Fields Explanation:**

- `cns_mpo_score`: CNS Multiparameter Optimization score (0-6, higher is better)
- `cns_viable`: Flag indicating CNS penetration capability
- `pains_alerts`: Number of Pan-Assay Interference compound alerts
- `logp`: Lipophilicity measure (optimal: 1-3)
- `molecular_weight`: In Daltons

---

#### Get Drug Details

```
GET /api/v1/drugs/{id}/
```

**Response Example:**

```json
{
  "id": 1,
  "drugbank_id": "DB00001",
  "chembl_id": "CHEMBL1234",
  "name": "Levodopa",
  "synonyms": ["L-DOPA", "Levodopa"],
  "is_approved": true,
  "approval_status": "FDA approved",
  "smiles": "NC(Cc1ccc(O)c(O)c1)C(O)=O",
  "molecular_weight": 197.19,
  "logp": -1.45,
  "hbd": 3,
  "hba": 5,
  "tpsa": 102.5,
  "pka": 2.18,
  "rotatable_bonds": 3,
  "cns_mpo_score": 5.2,
  "cns_viable": true,
  "cns_score_explanation": {
    "mw_score": 1.0,
    "logp_score": 1.2,
    "hbd_score": 0.8,
    "tpsa_score": 1.2
  },
  "pains_alerts": 0,
  "structural_alerts": [],
  "description": "Dopamine precursor for Parkinson treatment",
  "categories": ["Neurotransmitter precursor", "Anti-Parkinson agent"],
  "target_interactions": [
    {
      "id": 1,
      "target": 5,
      "target_gene_symbol": "SLC6A3",
      "target_name": "Dopamine transporter",
      "affinity_nm": 150.5,
      "affinity_type": "IC50",
      "activity_type": "substrate",
      "confidence_score": 0.95,
      "evidence_level": "high",
      "source": "DrugBank",
      "is_off_target": false,
      "is_toxicity_associated": false
    }
  ],
  "pathway_effects": [
    {
      "id": 1,
      "drug": 1,
      "drug_name": "Levodopa",
      "pathway": 3,
      "pathway_name": "Dopamine Synthesis and Neurotransmission",
      "pathway_category": "neurotransmission",
      "perturbation_score": 0.85,
      "direction": "activation",
      "disease_impact": "beneficial",
      "confidence": 0.92,
      "contributing_targets": ["SLC6A3", "COMT"],
      "explanation": "Restores dopamine synthesis...",
      "has_safety_concern": false,
      "computed_at": "2025-02-20T10:30:00Z"
    }
  ],
  "safety_summary": {
    "has_warnings": false,
    "warning_count": 0,
    "warnings": []
  },
  "created_at": "2025-01-15T08:00:00Z",
  "updated_at": "2025-02-20T10:00:00Z"
}
```

---

#### Get Drug Targets

```
GET /api/v1/drugs/{id}/targets/
```

**Response:** Array of drug-target interactions with binding affinities.

---

#### Get Drug Pathway Effects

```
GET /api/v1/drugs/{id}/pathway_effects/
```

**Response:** Array of pathway perturbations caused by the drug.

---

#### Get Drug CNS Viability Summary

```
GET /api/v1/drugs/{id}/mechanism_summary/
```

**Response:**

```json
{
  "drug": "Levodopa",
  "mechanism_summary": "Dopamine replacement therapy targeting..."
}
```

---

#### Filter CNS-Viable Drugs

```
GET /api/v1/drugs/cns_viable/
```

**Response:** Returns only drugs with CNS MPO score ≥ 4.0.

---

### 2. Target Management

#### List All Targets

```
GET /api/v1/targets/
```

**Query Parameters:**

- `search`: Search by gene_symbol, gene_name, or protein_name
- `is_toxicity_associated`: Filter toxicity flags (true/false)
- `brain_expression_level`: Filter by expression (high/medium/low/not_detected)
- `ordering`: Sort by gene_symbol or disease_relevance_score
- `page`: Pagination

**Response Example:**

```json
{
  "count": 500,
  "results": [
    {
      "id": 1,
      "gene_symbol": "APOE",
      "gene_name": "Apolipoprotein E",
      "uniprot_id": "P02649",
      "protein_name": "Apolipoprotein E",
      "protein_class": "Lipoproteins",
      "disease_relevance_score": 0.95,
      "is_toxicity_associated": false,
      "toxicity_categories": [],
      "brain_expression_level": "high"
    }
  ]
}
```

---

#### Get Target Details

```
GET /api/v1/targets/{id}/
```

**Response Example:**

```json
{
  "id": 1,
  "gene_symbol": "APOE",
  "gene_name": "Apolipoprotein E",
  "uniprot_id": "P02649",
  "ensembl_id": "ENSG00000130203",
  "entrez_id": "348",
  "protein_name": "Apolipoprotein E",
  "protein_class": "Lipoproteins",
  "subcellular_location": ["Extracellular space", "Plasma membrane"],
  "disease_associations": [
    {
      "disease": "Alzheimer disease",
      "score": 0.98,
      "source": "DisGeNET"
    }
  ],
  "disease_relevance_score": 0.95,
  "is_toxicity_associated": false,
  "toxicity_categories": [],
  "toxicity_evidence": null,
  "known_drug_count": 12,
  "is_promiscuous_target": false,
  "brain_expression_level": "high",
  "description": "Key player in lipid transport and amyloid-beta clearance",
  "created_at": "2025-01-10T00:00:00Z",
  "updated_at": "2025-02-20T00:00:00Z",
  "data_source": "uniprot"
}
```

---

#### Get Drugs for a Target

```
GET /api/v1/targets/{id}/drugs/
```

**Response:** Array of drugs binding to this target with affinity data.

---

### 3. Pathway Management

#### List All Pathways

```
GET /api/v1/pathways/
```

**Query Parameters:**

- `search`: Search by pathway name or ID
- `category`: Filter by category (neuroinflammation, mitochondrial, protein_aggregation, synaptic, autophagy, oxidative_stress, apoptosis, neurotransmission, metabolism)
- `disease_relevance`: Filter by relevance (high/medium/low)
- `page`: Pagination

**Response Example:**

```json
{
  "count": 45,
  "results": [
    {
      "id": 1,
      "pathway_id": "KEGG_AD01",
      "name": "Neuroinflammation in Alzheimer's Disease",
      "description": "TNF-alpha and NF-kB signaling cascades...",
      "category": "neuroinflammation",
      "disease_relevance": "high",
      "activation_effect": "detrimental",
      "source": "kegg",
      "target_count": 24
    }
  ]
}
```

**Categories:**

- `neuroinflammation`: Immune signaling pathways
- `mitochondrial`: Energy metabolism and dysfunction
- `protein_aggregation`: Tau, amyloid-beta, alpha-synuclein
- `synaptic`: Synaptic plasticity and transmission
- `autophagy`: Proteostasis and autophagy
- `oxidative_stress`: Reactive oxygen species handling
- `apoptosis`: Cell death pathways
- `neurotransmission`: Dopamine, serotonin, glutamate
- `metabolism`: Glucose and lipid metabolism

---

#### Get Pathway Details

```
GET /api/v1/pathways/{id}/
```

**Response:** Detailed pathway with description, disease relevance, and target count.

---

#### Get Targets in Pathway

```
GET /api/v1/pathways/{id}/targets/
```

**Response Example:**

```json
{
  "count": 24,
  "results": [
    {
      "id": 1,
      "target": 10,
      "target_gene_symbol": "TNF",
      "role": "activator",
      "influence_weight": 4.5,
      "evidence_level": "high"
    }
  ]
}
```

---

#### Get Drug Effects on Pathway

```
GET /api/v1/pathways/{id}/drug_effects/
```

**Response:** All drugs and their effects on this pathway.

---

### 4. Drug-Pathway Effects

#### List All Pathway Effects

```
GET /api/v1/pathway-effects/
```

**Query Parameters:**

- `direction`: Filter by effect direction (activation/inhibition/modulation/unknown)
- `disease_impact`: Filter by impact (beneficial/detrimental/unknown)
- `has_safety_concern`: Filter by safety flags (true/false)
- `ordering`: Sort by perturbation_score or confidence
- `page`: Pagination

**Response Example:**

```json
{
  "count": 1200,
  "results": [
    {
      "id": 1,
      "drug": 5,
      "drug_name": "TNF-alpha inhibitor",
      "pathway": 1,
      "pathway_name": "Neuroinflammation",
      "pathway_category": "neuroinflammation",
      "perturbation_score": 0.87,
      "direction": "inhibition",
      "disease_impact": "beneficial",
      "confidence": 0.94,
      "contributing_targets": ["TNF", "TNFR1"],
      "explanation": "Reduces TNF-alpha signaling and microglial activation",
      "has_safety_concern": false,
      "computed_at": "2025-02-20T10:30:00Z"
    }
  ]
}
```

**Fields:**

- `perturbation_score`: Magnitude of pathway perturbation (0-1)
- `direction`: activation/inhibition/modulation/unknown
- `disease_impact`: beneficial/detrimental/unknown
- `confidence`: Confidence in prediction (0-1)
- `contributing_targets`: Array of target gene symbols involved
- `has_safety_concern`: True if off-target effects detected

---

### 5. Disease States

#### List Disease States

```
GET /api/v1/disease-states/
```

**Response Example:**

```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "name": "Alzheimer's Early Stage",
      "description": "Mild cognitive impairment baseline",
      "disease_type": "Alzheimer's Disease",
      "parameters": {
        "amyloid_burden": 0.3,
        "tau_aggregation": 0.2,
        "neuroinflammation": 0.25,
        "mitochondrial_stress": 0.15,
        "synaptic_loss": 0.1
      },
      "baseline_trajectory": [...],
      "uncertainty_bounds": {...},
      "simulation_config": {...},
      "is_default": false,
      "created_at": "2025-01-20T00:00:00Z",
      "updated_at": "2025-02-20T00:00:00Z"
    }
  ]
}
```

---

#### Get Default Disease State

```
GET /api/v1/disease-states/default/
```

**Response:** The default disease state with pre-configured parameters for simulations.

---

#### Create New Disease State (POST)

```
POST /api/v1/disease-states/
Content-Type: application/json

{
  "name": "Custom Disease State",
  "disease_type": "Parkinson's Disease",
  "parameters": {
    "dopamine_depletion": 0.5,
    "alpha_synuclein_aggregation": 0.6,
    "mitochondrial_dysfunction": 0.4
  },
  "is_default": false
}
```

---

### 6. Predictions (Pre-trained Models)

#### Binding Affinity Prediction

```
POST /api/v1/predictions/binding-affinity/
Content-Type: application/json

{
  "molecule_smiles": "CCO",
  "target_name": "TNF-alpha",
  "target_sequence": "MGSSDQ..." (optional)
}
```

**Response Example:**

```json
{
  "molecule_analysis": {
    "smiles": "CCO",
    "molecular_weight": 46.04,
    "logp": -0.31,
    "hbd": 1,
    "hba": 1,
    "tpsa": 20.23,
    "num_rotatable_bonds": 0,
    "pains_alerts": 0,
    "drug_likeness": "good",
    "morgan_fingerprint": [0, 1, 0, ...] (2048-bit)
  },
  "binding_affinity": {
    "target": "TNF-alpha",
    "binding_score": 7.5,
    "confidence": "high",
    "method": "GraphDTA (pre-trained)",
    "reasoning": "Favorable molecular properties and target complementarity"
  },
  "status": "success",
  "model_info": {
    "method": "GraphDTA (pre-trained weights)",
    "paper": "Öztürk et al., 2020",
    "validation": "MedGemma medical reasoning"
  }
}
```

---

#### Toxicity Assessment

```
POST /api/v1/predictions/toxicity/
Content-Type: application/json

{
  "molecule_smiles": "CCO",
  "molecule_name": "Ethanol" (optional)
}
```

**Response Example:**

```json
{
  "toxicity": {
    "molecule": "Ethanol",
    "toxicity_risk": "low",
    "mechanism": "Metabolic degradation to acetaldehyde",
    "confidence": "medium",
    "reasoning": "Small alcohol with well-understood metabolism"
  },
  "status": "success",
  "model": "MedGemma-7B (medical reasoning)"
}
```

---

#### Drug Response Prediction

```
POST /api/v1/predictions/drug-response/
Content-Type: application/json

{
  "molecule_smiles": "CCO",
  "target_name": "TNF-alpha",
  "target_sequence": "MGSSDQ..." (optional),
  "disease_context": "Neuroinflammation" (optional)
}
```

**Response Example:**

```json
{
  "drug_response_prediction": {
    "molecule_analysis": {...},
    "binding_prediction": {...},
    "toxicity_assessment": {...},
    "overall_recommendation": "Potentially viable for neuroinflammation targeting",
    "risk_factors": ["Unknown metabolic stability"],
    "next_steps": ["Synthetic accessibility assessment", "Pharmacokinetics modeling"]
  },
  "status": "success",
  "models_used": [
    "GraphDTA (binding affinity)",
    "MedGemma-7B (toxicity, reasoning)",
    "ESM-2 (protein embeddings)",
    "RDKit (molecular features)"
  ]
}
```

---

#### Quick Molecule Analysis

```
POST /api/v1/predictions/molecule-analysis/
Content-Type: application/json

{
  "molecule_smiles": "CCO"
}
```

**Response Example:**

```json
{
  "analysis": {
    "smiles": "CCO",
    "molecular_weight": 46.04,
    "logp": -0.31,
    "hbd": 1,
    "hba": 1,
    "tpsa": 20.23,
    "num_rotatable_bonds": 0,
    "pains_alerts": 0,
    "drug_likeness": "good"
  },
  "status": "success"
}
```

---

### 7. Simulations

#### Run Disease Progression Simulation

```
POST /api/v1/simulate/
Content-Type: application/json

{
  "drug_id": 5,
  "disease_state_id": 1,
  "initial_parameters": {} (optional),
  "time_steps": 10
}
```

**Response Example:**

```json
{
  "baseline": {
    "label": "No Intervention",
    "time_steps": 10,
    "trajectory": [
      {
        "time_step": 0,
        "parameters": {
          "amyloid_burden": 0.3,
          "tau_aggregation": 0.2
        },
        "uncertainty": 0.05
      },
      {
        "time_step": 1,
        "parameters": {
          "amyloid_burden": 0.32,
          "tau_aggregation": 0.21
        },
        "uncertainty": 0.06
      }
    ],
    "final_state": {...},
    "key_changes": ["Neuroinflammation increased 15%", "Mitochondrial stress stable"],
    "explanation": "Natural disease progression without intervention"
  },
  "intervention": {
    "label": "With TNF-alpha inhibitor",
    "time_steps": 10,
    "trajectory": [...],
    "final_state": {...},
    "key_changes": ["Neuroinflammation reduced 40%", "Amyloid burden stable"],
    "explanation": "Drug intervention slows progression"
  },
  "comparison": {
    "improvement": "35% reduction in disease progression",
    "time_benefit": "6 months delayed progression",
    "pathway_impact": ["Neuroinflammation pathway: -40%", "Amyloid pathway: +5%"]
  },
  "overall_assessment": "Drug shows protective effect through neuroinflammation modulation",
  "caveats": [
    "This is mechanistic exploration, NOT clinical prediction",
    "Simulations based on pre-trained models",
    "Real-world effects will differ significantly"
  ]
}
```

---

### 8. System Information

#### Get System Status and Statistics

```
GET /api/v1/system/
```

**Response Example:**

```json
{
  "platform": "NeuroAI",
  "version": "2.0.0",
  "description": "AI-powered drug discovery platform using pre-trained models...",
  "ml_models": {
    "binding_affinity": "GraphDTA (pre-trained)",
    "protein_embeddings": "ESM-2-33M (Meta)",
    "toxicity_assessment": "MedGemma-7B (Google)",
    "molecular_features": "RDKit + Morgan fingerprints + ChemBERTA",
    "reasoning": "MedGemma-7B (medical reasoning)"
  },
  "statistics": {
    "drug_count": 150,
    "target_count": 500,
    "pathway_count": 45,
    "cns_viable_drugs": 87
  },
  "data_sources": ["DrugBank", "DisGeNET", "KEGG", "Reactome"],
  "disclaimers": [
    "This platform uses pre-trained ML models for predictions",
    "All predictions are exploratory and NOT clinically validated",
    "Results should be reviewed by domain experts",
    "No diagnostic or treatment recommendations are made"
  ]
}
```

---

## Data Models Summary

### Drug

- **Primary Fields**: drugbank_id, chembl_id, name, smiles
- **Properties**: molecular_weight, logp, hbd, hba, tpsa, pka, rotatable_bonds
- **CNS Metrics**: cns_mpo_score, cns_viable, cns_score_explanation
- **Safety**: pains_alerts, structural_alerts
- **Relationships**: target_interactions, pathway_effects

### Target

- **Primary Fields**: gene_symbol, gene_name, uniprot_id, ensembl_id
- **Disease Data**: disease_relevance_score, disease_associations
- **Safety**: is_toxicity_associated, toxicity_categories, toxicity_evidence
- **Expression**: brain_expression_level
- **Relationships**: drug_interactions, pathway_memberships

### Pathway

- **Primary Fields**: pathway_id, name, category
- **Categories**: neuroinflammation, mitochondrial, protein_aggregation, synaptic, autophagy, oxidative_stress, apoptosis, neurotransmission, metabolism
- **Disease Data**: disease_relevance (high/medium/low), activation_effect
- **Source**: KEGG, Reactome, Gene Ontology, or manually curated
- **Relationships**: target_members, drug_effects

### DrugPathwayEffect

- **Core Data**: perturbation_score, direction (activation/inhibition), disease_impact
- **Metadata**: confidence, contributing_targets, explanation, has_safety_concern, computed_at
- **Relationships**: drug, pathway

### DiseaseState

- **Configuration**: parameters (dict of pathway/biomarker states)
- **Simulation Config**: baseline_trajectory, uncertainty_bounds, simulation_config
- **Metadata**: is_default, created_at, updated_at

---

## Frontend Features to Implement

### 1. **Drug Browser**

- List view with filtering (CNS viability, approval status)
- Search functionality (name, DrugBank ID, ChEMBL ID)
- Drug detail cards with:
  - Chemical structure visualization (SMILES)
  - CNS MPO scoring breakdown
  - Target interaction table
  - Pathway effects visualization
  - Safety summary with warning indicators

### 2. **Target Explorer**

- Browse all targets with disease relevance scoring
- Filter by toxicity association and brain expression
- Target detail view with:
  - Disease associations
  - Connected drugs table
  - Expression levels
  - Toxicity warnings if applicable

### 3. **Pathway Visualization**

- Pathway browser by disease category
- Network visualization of pathways and targets
- Drug effect on pathway display
- Perturbation score indicators

### 4. **Prediction Tools**

- **Binding Affinity Predictor**
  - SMILES input form
  - Target selection dropdown
  - Results with score and confidence
- **Toxicity Assessor**
  - SMILES input form
  - Toxicity risk output
  - Mechanism explanation
- **Drug Response Predictor**
  - Comprehensive form (molecule + target + disease context)
  - Multi-model results display
- **Molecule Analyzer**
  - Quick analysis for SMILES
  - Property visualization

### 5. **Simulation Dashboard**

- Disease state selector
- Drug selection for intervention
- Time steps configuration
- Baseline vs Intervention trajectory comparison
- Disease progression charts
- Impact assessment and key changes display

### 6. **Data Dashboard**

- Platform statistics (drug count, target count, pathways)
- ML models information
- Data source credits
- Important disclaimers

---

## Frontend Requirements

### Technology Stack

- **Framework**: React 18 with TypeScript (recommended)
- **Styling**: Tailwind CSS or similar
- **Charts**: Recharts, Chart.js, or D3.js for visualizations
- **HTTP Client**: Axios or Fetch API
- **Forms**: React Hook Form or Formik
- **State Management**: React Context or Redux Toolkit
- **UI Components**: Radix UI, Material-UI, or Chakra UI

### Key Features

1. **Responsive Design**: Mobile, tablet, and desktop support
2. **Data Visualization**: Charts for trajectories, networks for pathways
3. **Search & Filtering**: Real-time search and filter capabilities
4. **SMILES Visualization**: Display chemical structures (use RDKit web or similar)
5. **Error Handling**: User-friendly error messages and retry logic
6. **Loading States**: Proper loading indicators for API calls
7. **Pagination**: Handle large datasets efficiently
8. **Deep Linking**: URL-based navigation for bookmarking results

### Important Notes & Disclaimers

- Display prominent **disclaimers** on all prediction pages:
  - "This is exploratory AI, NOT clinical prediction"
  - "Results should be reviewed by domain experts"
  - "No diagnostic or treatment recommendations are made"
- Show **confidence levels** for all predictions
- Display **model attribution** (e.g., "GraphDTA (pre-trained)")
- Include **uncertainty bounds** in simulations
- Add **evidence level indicators** (high/medium/low) for interactions

---

## Deployment Instructions

### 1. Backend Setup

```bash
# Start backend (if not already running)
cd backend
python manage.py runserver 0.0.0.0:8000
```

### 2. Frontend Setup (Using Lovable)

```bash
# Clone generated project from Lovable
cd neuroai-frontend

# Install dependencies
npm install

# Configure backend URL
# In .env or config file:
# REACT_APP_API_BASE_URL=http://localhost:8000

# Start development server
npm start
```

### 3. Docker Deployment

```bash
# Build frontend Docker image
docker build -t neuroai-frontend .

# Run container
docker run -p 3000:3000 -e REACT_APP_API_BASE_URL=http://backend:8000 neuroai-frontend
```

### 4. Production Build

```bash
npm run build
# Deploy build/ folder to your hosting (Vercel, Netlify, AWS S3, etc.)
```

---

## Environment Variables

Create a `.env` file in the frontend root:

```
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_API_TIMEOUT=30000
REACT_APP_ENABLE_ANALYTICS=false
REACT_APP_LOG_LEVEL=info
```

---

## API Integration Examples

### Fetching Drugs

```typescript
async function fetchDrugs(page = 1, filters = {}) {
  const params = new URLSearchParams({
    page,
    ...filters,
  });

  const response = await fetch(
    `${process.env.REACT_APP_API_BASE_URL}/api/v1/drugs/?${params}`,
  );
  return response.json();
}
```

### Getting Drug Details

```typescript
async function getDrugDetail(drugId) {
  const response = await fetch(
    `${process.env.REACT_APP_API_BASE_URL}/api/v1/drugs/${drugId}/`,
  );
  return response.json();
}
```

### Predicting Binding Affinity

```typescript
async function predictBindingAffinity(smiles, targetName) {
  const response = await fetch(
    `${process.env.REACT_APP_API_BASE_URL}/api/v1/predictions/binding-affinity/`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        molecule_smiles: smiles,
        target_name: targetName,
      }),
    },
  );
  return response.json();
}
```

### Running Simulation

```typescript
async function runSimulation(drugId, diseaseStateId, timeSteps = 10) {
  const response = await fetch(
    `${process.env.REACT_APP_API_BASE_URL}/api/v1/simulate/`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        drug_id: drugId,
        disease_state_id: diseaseStateId,
        time_steps: timeSteps,
      }),
    },
  );
  return response.json();
}
```

---

## Design Recommendations

### Color Scheme

- **Primary**: Blue (#0066CC) - Science/Trust
- **Success**: Green (#00AA44) - Beneficial effects
- **Warning**: Orange (#FF8800) - Caution needed
- **Danger**: Red (#CC0000) - Harmful effects
- **Neutral**: Gray - Data points
- **Background**: Light gray (#F5F5F5) with white cards

### Typography

- **Headers**: Sans-serif (Roboto, Inter, or similar)
- **Body**: Same sans-serif family
- **Monospace**: For SMILES strings and technical data

### Components

- **Card-based layout** for drug/target information
- **Tables** for interaction data with sorting/filtering
- **Charts** for pathway effects and simulations
- **Modals** for prediction entry forms
- **Tabs** for different sections (Details, Interactions, Pathways)

---

## Testing Checklist

- [ ] Drug list loads and filters work
- [ ] Drug detail page shows all relationships
- [ ] Target search returns correct results
- [ ] Pathway visualization displays correctly
- [ ] Binding affinity prediction returns results
- [ ] Toxicity assessment works
- [ ] Simulation comparison displays trajectories
- [ ] Mobile responsiveness verified
- [ ] All error states handled gracefully
- [ ] Disclaimers visible on all prediction pages

---

## Additional Resources

- Backend Source: `/backend/`
- API Documentation: `http://localhost:8000/api/v1/`
- Django Admin: `http://localhost:8000/admin/`
- Models Documentation: See model files in `/backend/core/models/`

---

## Contact & Support

For issues or questions:

1. Check backend logs: `docker logs neuroai-backend`
2. Check browser console for frontend errors
3. Verify API connectivity: `curl http://localhost:8000/api/v1/system/`
