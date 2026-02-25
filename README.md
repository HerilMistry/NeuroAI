# NeuroAI

**Multimodal AI Platform for Computational Drug Discovery in Neurodegenerative Diseases**

NeuroAI is an integrated AI-driven system designed to accelerate early-stage drug discovery for neurodegenerative diseases including:

- Alzheimer’s Disease  
- Parkinson’s Disease  
- Amyotrophic Lateral Sclerosis (ALS)  
- Frontotemporal Dementia  

The platform combines molecular modeling, protein representation learning, toxicity assessment, and disease progression simulation into a unified research workflow.

---

## Overview

NeuroAI integrates multiple specialized AI models:

- **GraphDTA v2.1** – Drug–target binding affinity prediction (Graph Neural Networks)
- **MedGemma-7B** – Toxicity analysis and biomedical reasoning
- **ESM-2-33M** – Protein embedding model
- **RDKit** – Molecular descriptor and cheminformatics engine

The system produces:

- Binding affinity predictions (IC50, Kd)
- Off-target risk analysis
- Toxicity scoring
- CNS penetration scoring
- Drug response estimation
- Disease progression simulation

All results are generated in seconds using ensemble inference.

---

## Key Capabilities

### Drug Browser
- Explore 150+ compounds
- Filter by CNS viability
- Filter by approval status
- View molecular descriptors and SMILES

### Target Explorer
- 500+ biological targets
- Disease relevance scoring
- Expression profiling

### Pathway Browser
- 45+ disease-relevant pathways
- Intervention points
- Drug–pathway interaction mapping

### ML Predictions
- Binding affinity prediction
- Toxicity assessment
- Drug response modeling
- Disease progression simulation

---

## System Architecture

User Input (Drug + Target + Disease)  
↓  
GraphDTA → Binding Affinity  
MedGemma → Toxicity & Reasoning  
ESM-2 → Protein Embeddings  
RDKit → Molecular Features  
↓  
Ensemble Integration  
↓  
Disease Progression Model (Neural ODE)  
↓  
Risk–Efficacy Output + Simulation  

---

## Tech Stack

### Frontend
- React 18
- TypeScript
- Vite
- TailwindCSS
- shadcn/ui
- React Router

### Backend
- Django 5.0
- Django REST Framework
- SQLite (development)
- RDKit
- Pre-trained ML inference models

### ML Models
- Graph Neural Networks
- Transformer-based protein embeddings
- Biomedical large language model (MedGemma-7B)
- Disease simulation models

### Deployment
- Docker
- Local startup via `startup.sh`

---


