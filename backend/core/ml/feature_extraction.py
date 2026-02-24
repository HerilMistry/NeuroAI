"""
Feature Extraction Pipeline
============================

Extracts molecular and protein features using pre-trained models.

Features extracted:
1. RDKit Descriptors: 10 physicochemical properties
2. Morgan Fingerprints: 2048-bit molecular encoding
3. ChemBERTA: Pre-trained molecule encoder (384-dim)
4. ESM-2: Pre-trained protein encoder (1024-dim)
5. MACCS Keys: Standard molecular pattern keys

Total molecular representation: 2,000+ dimensions
"""

import numpy as np
import torch
import logging
from typing import Dict, List, Tuple, Optional
from rdkit import Chem
from rdkit.Chem import Descriptors, AllChem, MACCSkeys
import hashlib
from functools import lru_cache

logger = logging.getLogger(__name__)


class RDKitDescriptors:
    """Extract physicochemical descriptors using RDKit."""

    @staticmethod
    def extract(smiles: str) -> Optional[Dict[str, float]]:
        """
        Extract RDKit descriptors from SMILES.

        Args:
            smiles: SMILES string

        Returns:
            Dictionary of 10 descriptors or None if invalid
        """
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                return None

            return {
                "mw": Descriptors.MolWt(mol),  # Molecular weight
                "logp": Descriptors.MolLogP(mol),  # Lipophilicity
                "hba": Descriptors.NumHAcceptors(mol),  # H-bond acceptors
                "hbd": Descriptors.NumHDonors(mol),  # H-bond donors
                "rotatable_bonds": Descriptors.NumRotatableBonds(mol),  # Rotation freedom
                "aromatic_rings": Descriptors.NumAromaticRings(mol),  # Aromaticity
                "tpsa": Descriptors.TPSA(mol),  # Topological PSA
                "psa": Descriptors.PSA(mol),  # Polar surface area
                "labuteasa": Descriptors.PEOE_VSA1(mol),  # Electrostatic features
                "bertzct": Descriptors.BertzCT(mol),  # Complexity
            }
        except Exception as e:
            logger.error(f"Error extracting RDKit descriptors: {e}")
            return None

    @staticmethod
    def to_vector(descriptors: Dict[str, float]) -> np.ndarray:
        """Convert descriptor dict to vector."""
        if descriptors is None:
            return np.zeros(10)
        keys = [
            "mw",
            "logp",
            "hba",
            "hbd",
            "rotatable_bonds",
            "aromatic_rings",
            "tpsa",
            "psa",
            "labuteasa",
            "bertzct",
        ]
        return np.array([descriptors.get(k, 0.0) for k in keys])


class MorganFingerprints:
    """Extract Morgan fingerprints (circular descriptors)."""

    @staticmethod
    def extract(smiles: str, radius: int = 2, nbits: int = 2048) -> Optional[np.ndarray]:
        """
        Extract Morgan fingerprints from SMILES.

        Args:
            smiles: SMILES string
            radius: Radius for circular descriptors (default 2)
            nbits: Number of bits in fingerprint (default 2048)

        Returns:
            Binary fingerprint vector or None if invalid
        """
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                return None

            fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius, nBits=nbits)
            return np.array(fp)

        except Exception as e:
            logger.error(f"Error extracting Morgan fingerprints: {e}")
            return None


class MACCSKeysFeatures:
    """Extract MACCS structural keys."""

    @staticmethod
    def extract(smiles: str) -> Optional[np.ndarray]:
        """
        Extract MACCS Keys from SMILES.

        Args:
            smiles: SMILES string

        Returns:
            167-bit structural key vector or None if invalid
        """
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                return None

            keys = MACCSkeys.GenMACCSKeys(mol)
            return np.array(keys)

        except Exception as e:
            logger.error(f"Error extracting MACCS Keys: {e}")
            return None


class ChemBERTAEncoder:
    """Encode molecules using ChemBERTA pre-trained model."""

    def __init__(self, model_dict: Optional[Dict] = None):
        """
        Initialize ChemBERTA encoder.

        Args:
            model_dict: Dict with 'tokenizer' and 'model' keys
        """
        self.model_dict = model_dict
        self.tokenizer = model_dict.get("tokenizer") if model_dict else None
        self.model = model_dict.get("model") if model_dict else None

    def encode(self, smiles: str) -> Optional[np.ndarray]:
        """
        Encode SMILES using ChemBERTA.

        Args:
            smiles: SMILES string

        Returns:
            384-dimensional embedding or None if failed
        """
        if self.model is None or self.tokenizer is None:
            logger.warning("ChemBERTA model not loaded")
            return None

        try:
            inputs = self.tokenizer(
                smiles, return_tensors="pt", truncation=True, max_length=256
            )

            with torch.no_grad():
                outputs = self.model(**inputs)
                # Mean pooling over tokens
                embedding = outputs.last_hidden_state.mean(dim=1)

            return embedding[0].cpu().numpy()

        except Exception as e:
            logger.error(f"Error encoding with ChemBERTA: {e}")
            return None


class ESM2Encoder:
    """Encode proteins using ESM-2 pre-trained model."""

    def __init__(self, model_dict: Optional[Dict] = None):
        """
        Initialize ESM-2 encoder.

        Args:
            model_dict: Dict with 'tokenizer' and 'model' keys
        """
        self.model_dict = model_dict
        self.tokenizer = model_dict.get("tokenizer") if model_dict else None
        self.model = model_dict.get("model") if model_dict else None

    def encode(self, sequence: str) -> Optional[np.ndarray]:
        """
        Encode protein sequence using ESM-2.

        Args:
            sequence: Protein sequence (single letter amino acids)

        Returns:
            1024-dimensional embedding (mean-pooled) or None if failed
        """
        if self.model is None or self.tokenizer is None:
            logger.warning("ESM-2 model not loaded")
            return None

        try:
            # Tokenize sequence
            inputs = self.tokenizer(sequence, return_tensors="pt", truncation=True)

            with torch.no_grad():
                outputs = self.model(**inputs, output_hidden_states=True)
                # Use last hidden state, mean pool over sequence
                embeddings = outputs.last_hidden_state
                embedding = embeddings.mean(dim=1)

            return embedding[0].cpu().numpy()

        except Exception as e:
            logger.error(f"Error encoding with ESM-2: {e}")
            return None


class MolecularFeatureExtractor:
    """Unified molecular feature extraction pipeline."""

    def __init__(
        self,
        chemberta_model: Optional[Dict] = None,
        use_esm2: bool = True,
        esm2_model: Optional[Dict] = None,
    ):
        """
        Initialize feature extractor.

        Args:
            chemberta_model: Optional pre-loaded ChemBERTA
            use_esm2: Whether to use ESM-2 for proteins
            esm2_model: Optional pre-loaded ESM-2
        """
        self.rdkit = RDKitDescriptors()
        self.morgan = MorganFingerprints()
        self.maccs = MACCSKeysFeatures()
        self.chemberta = ChemBERTAEncoder(chemberta_model)
        self.esm2 = ESM2Encoder(esm2_model) if use_esm2 else None

    def extract_molecule_features(self, smiles: str) -> Optional[Dict[str, np.ndarray]]:
        """
        Extract all molecular features from SMILES.

        Args:
            smiles: SMILES string

        Returns:
            Dict with keys: 'descriptors', 'morgan', 'maccs', 'chemberta'
        """
        # Validate SMILES
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            logger.error(f"Invalid SMILES: {smiles}")
            return None

        features = {}

        # RDKit descriptors (10-dim)
        rdkit_desc = self.rdkit.extract(smiles)
        if rdkit_desc:
            features["descriptors"] = self.rdkit.to_vector(rdkit_desc)

        # Morgan fingerprints (2048-dim)
        morgan_fp = self.morgan.extract(smiles)
        if morgan_fp is not None:
            features["morgan"] = morgan_fp

        # MACCS Keys (167-dim)
        maccs_keys = self.maccs.extract(smiles)
        if maccs_keys is not None:
            features["maccs"] = maccs_keys

        # ChemBERTA embedding (384-dim) - optional, slower
        if self.chemberta.model is not None:
            chemberta_embed = self.chemberta.encode(smiles)
            if chemberta_embed is not None:
                features["chemberta"] = chemberta_embed

        return features if features else None

    def extract_protein_features(self, sequence: str) -> Optional[np.ndarray]:
        """
        Extract protein features using ESM-2.

        Args:
            sequence: Protein sequence

        Returns:
            1024-dimensional embedding or None
        """
        if self.esm2 is None:
            logger.warning("ESM-2 not available")
            return None

        return self.esm2.encode(sequence)

    def combine_molecule_features(
        self, features: Dict[str, np.ndarray], exclude_chemberta: bool = False
    ) -> np.ndarray:
        """
        Combine all molecular features into single vector.

        Args:
            features: Dict from extract_molecule_features
            exclude_chemberta: Skip ChemBERTA for faster processing

        Returns:
            Combined feature vector (2225+ dimensional)
        """
        vectors = []

        # Always include these fast features
        if "descriptors" in features:
            vectors.append(features["descriptors"])
        if "morgan" in features:
            vectors.append(features["morgan"])
        if "maccs" in features:
            vectors.append(features["maccs"])

        # Optional: Include ChemBERTA for richer representation
        if "chemberta" in features and not exclude_chemberta:
            vectors.append(features["chemberta"])

        if vectors:
            return np.concatenate(vectors)
        else:
            return np.array([])

    def extract_all(
        self, smiles: str, protein_sequence: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Extract all features for molecule and optionally protein.

        Args:
            smiles: Molecule SMILES
            protein_sequence: Optional protein sequence

        Returns:
            Dict with 'molecule_features', 'protein_features', 'combined'
        """
        result = {}

        # Molecule features
        mol_features = self.extract_molecule_features(smiles)
        if mol_features:
            result["molecule_features"] = mol_features
            result["molecule_vector"] = self.combine_molecule_features(mol_features)

        # Protein features
        if protein_sequence and self.esm2:
            prot_features = self.extract_protein_features(protein_sequence)
            if prot_features is not None:
                result["protein_features"] = prot_features

        return result


# Caching decorator for faster repeated queries
@lru_cache(maxsize=10000)
def get_molecule_hash(smiles: str) -> str:
    """Get hash of SMILES for caching."""
    return hashlib.md5(smiles.encode()).hexdigest()
