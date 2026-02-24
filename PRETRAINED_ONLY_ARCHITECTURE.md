# NeuroAI: Pretrained-Only Production Architecture

**Date**: February 24, 2026  
**Status**: Ready for implementation ✅  
**Constraint**: No custom model training, use only pre-trained weights  
**Platform**: Backend (Django API) + Android mobile app

---

## 1. Problem Statement

**Current Situation**:
- ❌ 5 custom ML models designed but not trained
- ❌ Training requires 15+ hours GPU time
- ❌ We don't have time for training
- ❌ Some models (7B LLM) too large for Android

**Solution**:
- ✅ Remove custom model architectures
- ✅ Use only pre-trained models from literature
- ✅ Optimize for Android (lightweight, fast inference)
- ✅ Keep MedGemma reasoning on backend service

---

## 2. Available Pre-trained Models

### ✅ Tier 1: Already Available

| Model | Source | Size | Purpose | Speed | Status |
|-------|--------|------|---------|-------|--------|
| **ESM-2 (33M)** | Meta | 350MB | Protein sequences → embeddings | Fast | ✅ Ready |
| **RDKit** | Open source | Built-in | Molecular descriptors | Very fast | ✅ Ready |
| **Morgan FP** | RDKit | Built-in | 2048-bit molecular fingerprints | Very fast | ✅ Ready |
| **MedGemma-7B** | Google | 14GB | Medical reasoning + validation | Medium | ✅ Ready (backend only) |

### ✅ Tier 2: Pre-trained Models Available Online

| Model | Source | Size | Purpose | Usage |
|-------|--------|------|---------|-------|
| **ChemBERTA-77M** | DeepChem | 300MB | Molecule tokenization | Pre-train layer |
| **PrLM (Transformer)** | Various | 100-500MB | Protein language models | Alternative to ESM-2 |
| **GraphDTA weights** | Paper repo | ~100MB | Pre-trained binding affinity | Direct use |
| **TransDTA weights** | Paper repo | ~150MB | Transformer binding affinity | Direct use |
| **DeepDTA checkpoint** | Paper repo | ~200MB | DTA reference model | Direct use |

### ✅ Tier 3: Lightweight Models for Android

| Model | Source | Size | Purpose | Android |
|-------|--------|------|---------|---------|
| **MobileNet-based** | TensorFlow Hub | 10-50MB | Image/feature processing | ✅ Native |
| **DistilBERT** | Hugging Face | 268MB | Lightweight BERT | ⚠️ ~300MB model |
| **TFLite quantized** | Various | 1-10MB | Quantized models | ✅ Very fast |
| **ONNX quantized** | Models Hub | 1-10MB | Optimized inference | ✅ Fast |

---

## 3. New System Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    NeuroAI System (Pretrained-Only)          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐              ┌──────────────────────────┐  │
│  │  Android App │◄──REST API──►│  Django Backend (Linux)  │  │
│  │              │              │                          │  │
│  │ • Feature    │              │ • ESM-2 inference        │  │
│  │   extraction │              │ • RDKit processing       │  │
│  │ • UI/UX      │              │ • Pre-trained models     │  │
│  │ • Local cache│              │ • MedGemma service       │  │
│  │              │              │ • PostgreSQL + Redis     │  │
│  └──────────────┘              └──────────────────────────┘  │
│       ↓                                       ↓               │
│   SQLite (local)              ┌──────────────────────────┐   │
│   ~5-20MB                     │  Pre-trained Models      │   │
│                               │                          │   │
│                               │ • ESM-2 (TFLite)         │   │
│                               │ • ChemBERTA              │   │
│                               │ • RDKit (Python)         │   │
│                               │ • MedGemma-7B (API only) │   │
│                               │ • GraphDTA/TransDTA      │   │
│                               |   (checkpoint weights)   |   │
│                               └──────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

**Workflow 1: Molecular Representation (Local on Android)**
```
SMILES Input
    ↓
RDKit Descriptors (10 features) ──→ Cache
    ↓
Morgan Fingerprints (2048-bit) ──→ Cache
    ↓
ChemBERTA Encoding (384-dim) ──→ Cache
    ↓
Feature Vector (2,000+ dimensions) ──→ Combined representation
```

**Workflow 2: Protein Representation (Backend)**
```
Protein Sequence
    ↓
ESM-2-33M Inference (GPU or CPU)
    ↓
Token Embeddings (1024-dim × seq_length)
    ↓
Mean Pooling → 1024-dim protein vector
    ↓
Cache in Redis
```

**Workflow 3: Binding Affinity Prediction (Backend)**
```
Combined Features
(Molecular + Protein)
    ↓
Pre-trained Model
(GraphDTA or TransDTA)
    ↓
Binding Score (IC50, pKd, classification)
    ↓
MedGemma Plausibility Check
    ↓
Result to Android
```

**Workflow 4: Toxicity Assessment (Backend)**
```
Molecule Features
    ↓
Tox21 Pre-trained Classifier
(if available)
    OR
MedGemma Medical Reasoning
    ↓
Toxicity Class + Explanation
    ↓
Result to Android
```

---

## 4. Components Being Removed

### ❌ To Remove (Not Using Pre-trained Weights)

1. **MolecularGraphEncoder** (custom GNN)
   - ❌ Was: Custom PyTorch graph network
   - ✅ Replace with: RDKit + ChemBERTA
   - Reason: RDKit is mature, ChemBERTA is pre-trained

2. **TargetEmbedder** (custom Transformer)
   - ❌ Was: Custom Transformer encoder
   - ✅ Replace with: ESM-2-33M
   - Reason: ESM-2 is pre-trained and optimized

3. **BindingAffinityPredictor** (custom multi-task)
   - ❌ Was: Custom neural network
   - ✅ Replace with: GraphDTA/TransDTA/DeepDTA checkpoint
   - Reason: Published models with available weights

4. **DiseaseStateVAE** (custom VAE)
   - ❌ Was: Custom variational autoencoder
   - ✅ Replace with: Remove (not needed for v1)
   - Reason: Disease progression not critical for drug discovery

5. **NeuralODE** (custom dynamics)
   - ❌ Was: Neural ODE equations
   - ✅ Replace with: Remove (not needed for v1)
   - Reason: Focus on drug-target interactions first

### ✅ To Keep (Already Pre-trained or Lightweight)

1. **RDKit Descriptors** ✅
2. **Morgan Fingerprints** ✅
3. **ESM-2 Protein Encoder** ✅
4. **MedGemma-7B** ✅ (backend only)
5. **RAG Knowledge Base** ✅
6. **PostgreSQL + Redis** ✅
7. **Django REST API** ✅
8. **Android UI** ✅

---

## 5. New ML Directory Structure

### Before (Training-Focused)
```
backend/core/ml/
├── molecular_representations.py    (custom GNN)
├── target_engagement.py             (custom models)
├── disease_models.py                (custom VAE, ODE)
├── medgemma_service.py
├── training.py                      (training pipeline)
└── datasets.py                      (dataset loaders)
```

### After (Inference-Only, Pre-trained)
```
backend/core/ml/
├── pretrained_models.py             (model loading)
├── feature_extraction.py            (RDKit + ChemBERTA)
├── binding_affinity.py              (GraphDTA inference)
├── medgemma_service.py              (unchanged)
├── inference.py                     (unified inference)
└── utils.py                         (helpers)
```

---

## 6. Specific Pre-trained Models to Use

### A. Molecular Representation Pipeline

**Step 1: RDKit Descriptors** (Always)
```python
# Always compute these (lightweight, no training)
from rdkit import Chem
from rdkit.Chem import Descriptors

descriptors = {
    'MolWt': Descriptors.MolWt(mol),
    'LogP': Descriptors.MolLogP(mol),
    'HBA': Descriptors.NumHBD(mol),
    'HBD': Descriptors.NumHBD(mol),
    'RotBonds': Descriptors.NumRotatableBonds(mol),
    'AromaticRings': Descriptors.NumAromaticRings(mol),
    'TPSA': Descriptors.TPSA(mol),
    'PSA': Descriptors.PSA(mol),
    'LabuteASA': Descriptors.LabuteASA(mol),
    'BertzCT': Descriptors.BertzCT(mol),
}
# Total: 10 features
```

**Step 2: Morgan Fingerprints** (Always)
```python
# Standard molecular fingerprint (pre-defined algorithm)
from rdkit.Chem import AllChem

fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius=2, nBits=2048)
# Total: 2048-bit vector
```

**Step 3: ChemBERTA Embedding** (Pre-trained, optional for enrichment)
```python
# Pre-trained SMILES tokenizer + embeddings
# Source: DeepChem HuggingFace Hub
# Model size: ~300MB
# Output: 384-dimensional embedding

from transformers import AutoTokenizer, AutoModel
tokenizer = AutoTokenizer.from_pretrained("deepchem/ChemBERTA-77M-MLM")
model = AutoModel.from_pretrained("deepchem/ChemBERTA-77M-MLM")

inputs = tokenizer(smiles, return_tensors="pt")
outputs = model(**inputs)
embedding = outputs.last_hidden_state.mean(dim=1)  # 384-dim
```

**Combined**: 2,058+ dimensional representation (10 + 2048 + 384)

### B. Protein Representation (ESM-2)

```python
# Pre-trained protein language model
# Source: Meta AI
# Model size: 350MB (tokenizer + weights)
# Output: 1024-dimensional embedding

import esm

model = esm.pretrained.esmfold_structure_module_only()  # or esm2 variant
# Inference: protein sequence → 1024-dim vector per amino acid

# For target: Mean pool over sequence to get single vector
```

### C. Binding Affinity Prediction

**Option 1: GraphDTA** (Graph-based)
```python
# Pre-trained model from paper
# Paper: "Graph Convolutional Networks for Drug-Target Binding Affinity Prediction"
# Weights available: Yes (research repos)
# Size: ~100MB
# Input: Molecular graph + Protein embedding
# Output: IC50 / Kd / binding score

from graphdta import GraphDTA
model = GraphDTA()
model.load_weights("models/graphdta_pretrained.pt")
```

**Option 2: TransDTA** (Transformer-based)
```python
# Pre-trained transformer model
# Paper: "Transformer: A Unified Architecture for DTA Prediction"
# Weights available: Yes
# Size: ~150MB
# Better for: Handling longer proteins

from transdta import TransDTA
model = TransDTA()
model.load_weights("models/transdta_pretrained.pt")
```

**Option 3: DeepDTA** (Reference implementation)
```python
# Older but well-documented
# Source: Original authors' repository
# Size: ~200MB
# Good for: Baseline comparison
```

**Choice for v1**: **GraphDTA** (good balance of speed/accuracy, well-documented)

### D. Toxicity Assessment

**Option 1: Tox21 Pre-trained**
```python
# If available pre-trained weights for Tox21 benchmark
# Classes: 12 toxicity endpoints
# Input: Molecular features
# Output: Toxicity probability per class
```

**Option 2: MedGemma Reasoning** (Fallback)
```python
# Use MedGemma for toxicity explanation
# Input: Molecule name + mechanism
# Output: Toxicity assessment + explanation
```

**Choice for v1**: **MedGemma** (always works, provides reasoning)

---

## 7. Implementation Roadmap

### Phase 1: Feature Extraction (Week 1)
- ✅ RDKit descriptor extraction (ready)
- ✅ Morgan fingerprints (ready)
- ⏳ ChemBERTA integration (fetch model)
- ⏳ ESM-2 optimization for backend

### Phase 2: Binding Affinity (Week 1-2)
- ⏳ Download GraphDTA pre-trained weights
- ⏳ Create inference wrapper
- ⏳ API endpoint for binding prediction
- ⏳ Android integration

### Phase 3: Android Optimization (Week 2)
- ⏳ Quantize models to TFLite
- ⏳ Local feature extraction (RDKit on Android)
- ⏳ Caching layer
- ⏳ Offline mode support

### Phase 4: Integration (Week 2-3)
- ⏳ Update API to use new models
- ⏳ Update frontend UIs
- ⏳ End-to-end testing
- ⏳ Performance benchmarking

---

## 8. Model Conversion for Android

### Strategy

Since MedGemma-7B is too large for Android, architecture uses:
1. **Backend for heavy compute**: MedGemma, GraphDTA, ESM-2
2. **Android for lightweight compute**: RDKit, feature caching
3. **REST API connection**: Request/response flow

### Models on Android

```
✅ Feasible on Android:
├── RDKit (native Python/Java libraries available)
├── Morgan fingerprints (lightweight)
├── ChemBERTA (quantized TFLite version, ~50MB)
└── Local SQLite cache

❌ Not on Android:
├── ESM-2 (350MB model + 1GB+ RAM)
├── MedGemma-7B (14GB)
└── GraphDTA (requires GPU for speed)
```

### Optimization Path

1. **Convert ChemBERTA to TFLite**:
   ```bash
   python -m tf2onnx.convert --saved-model <model> --output_file model.onnx
   # Then ONNX → TFLite via TensorFlow Lite Converter
   ```

2. **Use RDKit Java bindings** (if possible) or stay with backend

3. **Quantize weights** (int8 or float16):
   ```bash
   # Reduces size by 4x
   # Example: 300MB ChemBERTA → ~75MB
   ```

---

## 9. API Endpoints (New)

### Before Training Path (What We Had)
- `POST /api/v1/molecules/predict-binding/` → Custom model (needs training)
- `POST /api/v1/molecules/predict-toxicity/` → Custom model (needs training)

### New Pretrained Path (What We're Building)  
- `POST /api/v1/molecules/extract-features/` → RDKit + ChemBERTA
- `POST /api/v1/proteins/embed/` → ESM-2
- `POST /api/v1/interactions/binding-affinity/` → GraphDTA
- `POST /api/v1/molecules/toxicity-check/` → MedGemma
- `GET /api/v1/models/available/` → List available pre-trained models + info

---

## 10. Performance Expectations

### Feature Extraction (Local/Android)
```
Operation          | Time   | Size   | Notes
RDKit descriptors  | <1ms   | 80B    | 10 numbers
Morgan fingerprints| <5ms   | 256B   | 2048 bits
ChemBERTA embed    | 100ms  | 1.5KB  | Android: requires download
```

### Backend Inference
```
Operation          | Time      | GPU needed | Notes
ESM-2 (single seq) | 200-500ms | Yes        | Cached in Redis
GraphDTA inference | 50-100ms  | Optional   | CPU still ~200ms
MedGemma call      | 1-3s      | No         | API call
```

### Android
```
Component        | Size      | RAM needed | Performance
App core         | 50MB      | 100MB      | Very fast
SQLite cache     | 10-20MB   | -          | Local queries
ChemBERTA (TF L) | 50-80MB   | 500MB      | 100-200ms per mol
RDKit (if native)| 20-40MB   | 200MB      | <10ms
```

---

## 11. Removing Custom Training Code

### Files to Simplify/Remove

1. **backend/core/ml/training.py** → Remove entirely
2. **backend/core/ml/datasets.py** → Remove (use downloaded pretrained only)
3. **backend/core/ml/molecular_representations.py** → Replace with feature_extraction.py
4. **backend/core/ml/target_engagement.py** → Simplify to inference only
5. **backend/core/ml/disease_models.py** → Remove (v1 doesn't need it)
6. **backend/core/management/commands/ingest_drugbank.py** → Keep (useful for features)

### Files to Create

1. **backend/core/ml/pretrained_models.py** → Model loading + caching
2. **backend/core/ml/feature_extraction.py** → RDKit + ChemBERTA
3. **backend/core/ml/binding_affinity.py** → GraphDTA inference
4. **backend/core/ml/inference.py** → Unified prediction pipeline

---

## 12. Decision Summary

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| **Binding Affinity** | Use GraphDTA checkpoint | Pre-trained, published, good performance |
| **Molecular Features** | RDKit + Morgan + ChemBERTA | Fast, lightweight, mature |
| **Protein Embedding** | ESM-2-33M | Pre-trained, accurate, available |
| **Toxicity** | MedGemma reasoning | Always works, provides explanation |
| **Android** | Backend-heavy, frontend-light | MedGemma/ESM-2 too large for mobile |
| **No Training** | Focus on inference | Time constraint |
| **Model Size** | Prioritize <500MB per model | Feasible download + deployment |

---

## 13. Next Steps

1. ✅ This plan created
2. ⏳ Download GraphDTA pre-trained weights
3. ⏳ Create `pretrained_models.py`
4. ⏳ Create `feature_extraction.py` (RDKit + ChemBERTA)
5. ⏳ Create `inference.py` (unified pipeline)
6. ⏳ Update Django API views
7. ⏳ Update Android integration
8. ⏳ Performance testing
9. ⏳ Documentation update

---

**Author**: GitHub Copilot  
**Status**: Ready for implementation

