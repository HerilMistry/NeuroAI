"""
NeuroAI Machine Learning Module
================================

Core machine learning and deep learning components for:
- Molecular representation learning
- Target engagement prediction
- Disease state modeling
- Medical knowledge reasoning (MedGemma integration)
"""

from .molecular_representations import (
    MolecularGraphEncoder,
    PhysicochemicalDescriptors,
    ProteinLanguageModelEncoder,
    UnifiedMolecularEmbedding,
    MolecularRepresentationPipeline,
)

from .target_engagement import (
    TargetEmbedder,
    BindingAffinityPredictor,
    OffTargetPredictor,
    ToxicityPredictor,
    IntegratedTargetEngagementModel,
)

from .disease_models import (
    DiseaseStateVAE,
    NeuralODECell,
    DiseaseTrajectoryODE,
    DiseasePredictionHead,
    IntegratedDiseaseModel,
)

from .medgemma_service import (
    RAGVectorDatabase,
    MedGemmaService,
    get_medgemma_service,
)

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
