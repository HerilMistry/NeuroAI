"""
NeuroAI Machine Learning Module
================================

Core machine learning and deep learning components for:
- Molecular representation learning
- Target engagement prediction
- Disease state modeling
- Medical knowledge reasoning (MedGemma integration)

All imports are guarded so the application starts even when heavy
ML dependencies (torch-geometric, transformers, etc.) are missing.
"""

import logging as _logging

_logger = _logging.getLogger(__name__)

# -- Molecular representations (needs torch_geometric) --------
try:
    from .molecular_representations import (
        MolecularGraphEncoder,
        PhysicochemicalDescriptors,
        ProteinLanguageModelEncoder,
        UnifiedMolecularEmbedding,
        MolecularRepresentationPipeline,
    )
except Exception as _e:
    _logger.warning("molecular_representations unavailable: %s", _e)
    MolecularGraphEncoder = None
    PhysicochemicalDescriptors = None
    ProteinLanguageModelEncoder = None
    UnifiedMolecularEmbedding = None
    MolecularRepresentationPipeline = None

# -- Target engagement (needs torch) --------------------------
try:
    from .target_engagement import (
        TargetEmbedder,
        BindingAffinityPredictor,
        OffTargetPredictor,
        ToxicityPredictor,
        IntegratedTargetEngagementModel,
    )
except Exception as _e:
    _logger.warning("target_engagement unavailable: %s", _e)
    TargetEmbedder = None
    BindingAffinityPredictor = None
    OffTargetPredictor = None
    ToxicityPredictor = None
    IntegratedTargetEngagementModel = None

# -- Disease models (needs torch) -----------------------------
try:
    from .disease_models import (
        DiseaseStateVAE,
        NeuralODECell,
        DiseaseTrajectoryODE,
        DiseasePredictionHead,
        IntegratedDiseaseModel,
    )
except Exception as _e:
    _logger.warning("disease_models unavailable: %s", _e)
    DiseaseStateVAE = None
    NeuralODECell = None
    DiseaseTrajectoryODE = None
    DiseasePredictionHead = None
    IntegratedDiseaseModel = None

# -- Medical reasoning (MedGemma) -----------------------------
try:
    from .medgemma_service import (
        RAGVectorDatabase,
        MedGemmaService,
        get_medgemma_service,
    )
except Exception as _e:
    _logger.warning("medgemma_service unavailable: %s", _e)
    RAGVectorDatabase = None
    MedGemmaService = None
    get_medgemma_service = None

__version__ = "1.0.0"

__all__ = [
    # Molecular representation
    "MolecularGraphEncoder",
    "PhysicochemicalDescriptors",
    "ProteinLanguageModelEncoder",
    "UnifiedMolecularEmbedding",
    "MolecularRepresentationPipeline",
    # Target engagement
    "TargetEmbedder",
    "BindingAffinityPredictor",
    "OffTargetPredictor",
    "ToxicityPredictor",
    "IntegratedTargetEngagementModel",
    # Disease modeling
    "DiseaseStateVAE",
    "NeuralODECell",
    "DiseaseTrajectoryODE",
    "DiseasePredictionHead",
    "IntegratedDiseaseModel",
    # Medical reasoning
    "RAGVectorDatabase",
    "MedGemmaService",
    "get_medgemma_service",
]
