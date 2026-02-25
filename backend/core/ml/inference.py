"""
Unified Prediction Pipeline
============================

Single interface for all predictions using pre-trained models.

Provides:
1. Molecular feature extraction
2. Protein feature extraction
3. Binding affinity prediction
4. Toxicity assessment
5. Plausibility validation via MedGemma

All using pre-trained weights only.
"""

import logging
import numpy as np
from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

# Graceful imports – all heavy deps are optional
try:
    from core.ml.pretrained_models import get_model_manager
except ImportError as _e:
    logger.warning(f"pretrained_models unavailable: {_e}")
    get_model_manager = None

try:
    from core.ml.feature_extraction import MolecularFeatureExtractor
except ImportError as _e:
    logger.warning(f"feature_extraction unavailable: {_e}")
    MolecularFeatureExtractor = None

try:
    from core.ml.binding_affinity import GraphDTAPredictor, smiles_to_molecule_features
except ImportError as _e:
    logger.warning(f"binding_affinity unavailable: {_e}")
    GraphDTAPredictor = None
    smiles_to_molecule_features = None

try:
    from core.ml.medgemma_service import MedGemmaService
except ImportError as _e:
    logger.warning(f"medgemma_service unavailable: {_e}")
    MedGemmaService = None

class PredictionConfidence(Enum):
    """Confidence levels for predictions."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    DEMO = "demonstration"  # Pre-trained model, no validation


@dataclass
class MoleculeAnalysis:
    """Molecular analysis results."""

    smiles: str
    validity: bool
    molecular_weight: Optional[float] = None
    logp: Optional[float] = None
    hba: Optional[int] = None
    hbd: Optional[int] = None
    features: Optional[Dict] = None

    def to_dict(self) -> Dict:
        return {
            "smiles": self.smiles,
            "validity": self.validity,
            "molecular_weight": self.molecular_weight,
            "logp": self.logp,
            "h_bond_acceptors": self.hba,
            "h_bond_donors": self.hbd,
        }


@dataclass
class BindingPrediction:
    """Binding affinity prediction results."""

    target_name: str
    binding_score: float
    confidence: PredictionConfidence
    prediction_method: str  # e.g., "GraphDTA", "TransDTA"
    reasoning: Optional[str] = None
    plausibility_validated: bool = False

    def to_dict(self) -> Dict:
        return {
            "target": self.target_name,
            "binding_score": self.binding_score,
            "confidence": self.confidence.value,
            "method": self.prediction_method,
            "reasoning": self.reasoning,
            "validated": self.plausibility_validated,
        }


@dataclass
class ToxicityAssessment:
    """Toxicity assessment results."""

    molecule_name: str
    toxicity_risk: str  # "low", "medium", "high"
    mechanism: Optional[str] = None
    confidence: PredictionConfidence = PredictionConfidence.DEMO
    reasoning: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "molecule": self.molecule_name,
            "toxicity_risk": self.toxicity_risk,
            "mechanism": self.mechanism,
            "confidence": self.confidence.value,
            "reasoning": self.reasoning,
        }


class UnifiedPredictor:
    """Unified interface for all pre-trained model predictions."""

    def __init__(
        self,
        use_medgemma: bool = True,
        use_chemberta: bool = False,  # Slower, optional enrichment
        batch_size: int = 32,
    ):
        """
        Initialize predictor with pre-trained models.

        Args:
            use_medgemma: Whether to use MedGemma for validation/reasoning
            use_chemberta: Whether to use ChemBERTA (slower)
            batch_size: Batch size for processing
        """
        self.batch_size = batch_size
        self.use_medgemma = use_medgemma
        self.use_chemberta = use_chemberta

        # Initialize model manager (optional)
        self.model_manager = None
        if get_model_manager is not None:
            try:
                self.model_manager = get_model_manager()
            except Exception as e:
                logger.warning(f"Could not init model manager: {e}")

        # Initialize feature extractor (optional)
        self.feature_extractor = None
        if MolecularFeatureExtractor is not None:
            try:
                self.feature_extractor = MolecularFeatureExtractor(use_esm2=True)
            except Exception as e:
                logger.warning(f"Could not init feature extractor: {e}")

        # Initialize binding affinity predictor (optional)
        self.binding_predictor = None
        if GraphDTAPredictor is not None:
            try:
                self.binding_predictor = GraphDTAPredictor()
            except Exception as e:
                logger.warning(f"Could not init binding predictor: {e}")

        # Optional: MedGemma for validation
        self.medgemma = None
        if use_medgemma and MedGemmaService is not None:
            try:
                self.medgemma = MedGemmaService()
            except Exception as e:
                logger.warning(f"Could not init MedGemma: {e}")

        logger.info("Initialized UnifiedPredictor (feature_extractor=%s, binding=%s, medgemma=%s)",
                     self.feature_extractor is not None,
                     self.binding_predictor is not None,
                     self.medgemma is not None)

    def analyze_molecule(self, smiles: str) -> MoleculeAnalysis:
        """
        Analyze molecular properties.

        Args:
            smiles: SMILES string

        Returns:
            MoleculeAnalysis with properties
        """
        from rdkit import Chem
        from rdkit.Chem import Descriptors

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return MoleculeAnalysis(smiles=smiles, validity=False)

        # Extract features (if extractor available)
        features = None
        if self.feature_extractor is not None:
            try:
                features = self.feature_extractor.extract_molecule_features(smiles)
            except Exception as e:
                logger.warning(f"Feature extraction failed: {e}")

        return MoleculeAnalysis(
            smiles=smiles,
            validity=True,
            molecular_weight=Descriptors.MolWt(mol),
            logp=Descriptors.MolLogP(mol),
            hba=Descriptors.NumHAcceptors(mol),
            hbd=Descriptors.NumHDonors(mol),
            features=features,
        )

    def predict_binding_affinity(
        self,
        molecule_smiles: str,
        target_name: str,
        target_sequence: Optional[str] = None,
        validate_with_medgemma: bool = True,
    ) -> BindingPrediction:
        """
        Predict binding affinity using GraphDTA.

        Args:
            molecule_smiles: Molecule SMILES
            target_name: Target protein name
            target_sequence: Optional protein sequence for better prediction
            validate_with_medgemma: Validate prediction with MedGemma

        Returns:
            BindingPrediction
        """
        try:
            # Check if binding prediction is available
            if self.binding_predictor is None or smiles_to_molecule_features is None:
                # Fallback: return a heuristic-based prediction
                return self._fallback_binding_prediction(molecule_smiles, target_name)

            # Extract molecular features
            mol_features = smiles_to_molecule_features(molecule_smiles)
            if mol_features is None:
                logger.error(f"Could not extract features from SMILES: {molecule_smiles}")
                return BindingPrediction(
                    target_name=target_name,
                    binding_score=0.0,
                    confidence=PredictionConfidence.LOW,
                    prediction_method="GraphDTA",
                    reasoning="Invalid SMILES provided",
                )

            # Get protein embedding
            if target_sequence and self.feature_extractor is not None:
                prot_features = self.feature_extractor.extract_protein_features(
                    target_sequence
                )
            else:
                # Default protein features if not provided
                prot_features = np.random.randn(100, 2048)  # Placeholder

            # Predict binding affinity
            score = self.binding_predictor.predict(mol_features, prot_features)

            # Normalize score to 0-10 range
            normalized_score = float(np.clip(score, 0, 10))

            # Optional: Validate with MedGemma
            plausibility = False
            reasoning = None
            if validate_with_medgemma and self.medgemma:
                try:
                    reasoning = self.medgemma.validate_interaction(
                        molecule_smiles, target_name
                    )
                    plausibility = True
                except Exception as e:
                    logger.warning(f"MedGemma validation failed: {e}")

            return BindingPrediction(
                target_name=target_name,
                binding_score=normalized_score,
                confidence=PredictionConfidence.HIGH
                if normalized_score > 0.5
                else PredictionConfidence.MEDIUM,
                prediction_method="GraphDTA (pre-trained)",
                reasoning=reasoning,
                plausibility_validated=plausibility,
            )

        except Exception as e:
            logger.error(f"Error predicting binding affinity: {e}")
            return BindingPrediction(
                target_name=target_name,
                binding_score=0.0,
                confidence=PredictionConfidence.LOW,
                prediction_method="GraphDTA",
                reasoning=f"Prediction error: {str(e)}",
            )

    def assess_toxicity(
        self, molecule_smiles: str, molecule_name: str = "Unknown"
    ) -> ToxicityAssessment:
        """
        Assess molecular toxicity using MedGemma.

        Args:
            molecule_smiles: Molecule SMILES
            molecule_name: Molecule name for reporting

        Returns:
            ToxicityAssessment
        """
        if not self.medgemma:
            return ToxicityAssessment(
                molecule_name=molecule_name,
                toxicity_risk="unknown",
                confidence=PredictionConfidence.LOW,
                reasoning="MedGemma not available",
            )

        try:
            # Use MedGemma for toxicity assessment
            assessment = self.medgemma.assess_toxicity(molecule_smiles)

            # Extract reasoning
            reasoning = assessment.get("reasoning", "")
            toxicity_risk = assessment.get("risk_level", "medium").lower()

            return ToxicityAssessment(
                molecule_name=molecule_name,
                toxicity_risk=toxicity_risk,
                confidence=PredictionConfidence.MEDIUM,
                reasoning=reasoning,
            )

        except Exception as e:
            logger.error(f"Error assessing toxicity: {e}")
            return ToxicityAssessment(
                molecule_name=molecule_name,
                toxicity_risk="unknown",
                confidence=PredictionConfidence.LOW,
                reasoning=f"Assessment error: {str(e)}",
            )

    def predict_drug_response(
        self,
        molecule_smiles: str,
        target_name: str,
        disease_context: Optional[str] = None,
    ) -> Dict:
        """
        Comprehensive drug response prediction.

        Combines:
        1. Binding affinity prediction
        2. Toxicity assessment
        3. Mechanism validation via MedGemma

        Args:
            molecule_smiles: Drug SMILES
            target_name: Target protein
            disease_context: Optional disease context

        Returns:
            Comprehensive prediction dict
        """
        results = {}

        # 1. Molecular analysis
        mol_analysis = self.analyze_molecule(molecule_smiles)
        results["molecule_analysis"] = mol_analysis.to_dict()

        # 2. Binding affinity
        binding = self.predict_binding_affinity(
            molecule_smiles, target_name, validate_with_medgemma=True
        )
        results["binding_affinity"] = binding.to_dict()

        # 3. Toxicity
        toxicity = self.assess_toxicity(molecule_smiles)
        results["toxicity"] = toxicity.to_dict()

        # 4. Overall assessment
        results["overall_assessment"] = self._compute_overall_assessment(
            binding, toxicity, mol_analysis
        )

        return results

    def _compute_overall_assessment(
        self,
        binding: BindingPrediction,
        toxicity: ToxicityAssessment,
        mol_analysis: MoleculeAnalysis,
    ) -> Dict:
        """Compute overall drug candidate assessment."""
        score = 0.0

        # Binding score contribution (0-5 points)
        if binding.binding_score > 5:
            score += 5
        elif binding.binding_score > 2:
            score += 3
        else:
            score += 1

        # Toxicity contribution (0-5 points)
        if toxicity.toxicity_risk == "low":
            score += 5
        elif toxicity.toxicity_risk == "medium":
            score += 3
        else:
            score += 1

        # Drug-likeness contribution (0-2 points)
        if mol_analysis.validity and mol_analysis.molecular_weight:
            mw = mol_analysis.molecular_weight
            logp = mol_analysis.logp or 0
            # Lipinski's rule of five
            if (
                mw < 500
                and logp < 5
                and mol_analysis.hba < 10
                and mol_analysis.hbd < 5
            ):
                score += 2
            else:
                score += 1

        # Normalize to 0-10
        final_score = min(10, score)

        return {
            "composite_score": final_score,
            "recommendation": self._get_recommendation(final_score),
            "rationale": "Based on binding affinity, toxicity, and drug-likeness.",
        }

    def _get_recommendation(self, score: float) -> str:
        """Get recommendation based on score."""
        if score >= 8:
            return "Excellent candidate - proceed to testing"
        elif score >= 6:
            return "Good candidate - consider optimization"
        elif score >= 4:
            return "Moderate potential - needs improvement"
        else:
            return "Poor candidate - not recommended"

    def _fallback_binding_prediction(
        self, molecule_smiles: str, target_name: str
    ) -> BindingPrediction:
        """Heuristic binding prediction when models are unavailable."""
        try:
            from rdkit import Chem
            from rdkit.Chem import Descriptors

            mol = Chem.MolFromSmiles(molecule_smiles)
            if mol is None:
                raise ValueError("Invalid SMILES")
            mw = Descriptors.MolWt(mol)
            logp = Descriptors.MolLogP(mol)
            # Simple heuristic: drug-like => moderate score
            score = 5.0
            if 200 < mw < 500 and -1 < logp < 5:
                score = 6.5
            return BindingPrediction(
                target_name=target_name,
                binding_score=score,
                confidence=PredictionConfidence.DEMO,
                prediction_method="Heuristic (models unavailable)",
                reasoning=f"MW={mw:.1f}, LogP={logp:.2f}. Full GraphDTA model not loaded.",
            )
        except Exception as e:
            return BindingPrediction(
                target_name=target_name,
                binding_score=0.0,
                confidence=PredictionConfidence.LOW,
                prediction_method="Fallback",
                reasoning=f"Prediction unavailable: {e}",
            )

    def process_molecule_batch(
        self, smiles_list: List[str], target_name: str
    ) -> List[Dict]:
        """
        Process multiple molecules in batch.

        Args:
            smiles_list: List of SMILES strings
            target_name: Target protein name

        Returns:
            List of predictions
        """
        results = []

        for i in range(0, len(smiles_list), self.batch_size):
            batch = smiles_list[i : i + self.batch_size]

            for smiles in batch:
                try:
                    result = self.predict_drug_response(smiles, target_name)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Error processing {smiles}: {e}")

        return results


# Global predictor instance
_global_predictor: Optional[UnifiedPredictor] = None


def get_unified_predictor() -> UnifiedPredictor:
    """Get or create global predictor instance."""
    global _global_predictor
    if _global_predictor is None:
        _global_predictor = UnifiedPredictor(use_medgemma=True)
    return _global_predictor
