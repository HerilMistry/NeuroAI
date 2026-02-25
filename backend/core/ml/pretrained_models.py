"""
Pre-trained Model Management
============================

Loads and manages pre-trained models from HuggingFace, published papers, and local caches.

Models Available:
1. ESM-2-33M: Protein language model (Meta)
2. ChemBERTA-77M: Molecule tokenizer (DeepChem)
3. GraphDTA: Binding affinity (Published checkpoint)
4. MedGemma-7B: Medical reasoning (via API)
5. RDKit: Built-in chemical descriptors

All models use pre-trained weights - no custom training.
"""

import os
import logging
import torch
import hashlib
from typing import Dict, Optional, Any
from pathlib import Path
import json

logger = logging.getLogger(__name__)

# Model registry with checksums
MODEL_REGISTRY = {
    "esm2_33m": {
        "source": "facebook/esm2_t33_650M_UR50D",
        "type": "huggingface",
        "size_mb": 350,
        "description": "ESM-2 protein language model (33M params)",
        "download": True,
        "local_path": "models/esm2_33m",
    },
    "chemberta_77m": {
        "source": "deepchem/ChemBERTA-77M-MLM",
        "type": "huggingface",
        "size_mb": 300,
        "description": "ChemBERTA molecule encoder",
        "download": True,
        "local_path": "models/chemberta_77m",
    },
    "graphdta_pretrained": {
        "source": "https://huggingface.co/datasets/aalto-ai/graphdta-weights/resolve/main/model.pt",
        "type": "remote_checkpoint",
        "size_mb": 100,
        "description": "GraphDTA binding affinity model (pre-trained on KIBA/BindingDB)",
        "download": True,
        "local_path": "models/graphdta_pretrained.pt",
    },
    "rdkit": {
        "source": "builtin",
        "type": "builtin",
        "size_mb": 0,
        "description": "RDKit chemical descriptors (built-in, no download needed)",
        "download": False,
        "local_path": None,
    },
    "medgemma_7b": {
        "source": "google/medgemma-7b",
        "type": "api_only",
        "size_mb": 14000,
        "description": "MedGemma-7B (backend API only, not for mobile)",
        "download": False,
        "local_path": None,
    },
}


class ModelManager:
    """Manages downloading, caching, and loading pre-trained models."""

    def __init__(self, cache_dir: str = "models"):
        """
        Initialize model manager.

        Args:
            cache_dir: Directory to cache downloaded models
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.loaded_models = {}  # In-memory cache
        self._init_manifest()

    def _init_manifest(self):
        """Initialize or load manifest of what's been downloaded."""
        self.manifest_path = self.cache_dir / "manifest.json"
        if self.manifest_path.exists():
            with open(self.manifest_path) as f:
                self.manifest = json.load(f)
        else:
            self.manifest = {}

    def _save_manifest(self):
        """Save manifest of downloaded models."""
        with open(self.manifest_path, "w") as f:
            json.dump(self.manifest, f, indent=2)

    def download_model(self, model_name: str, force: bool = False) -> bool:
        """
        Download a pre-trained model.

        Args:
            model_name: Model identifier (e.g., 'esm2_33m')
            force: Force re-download even if exists

        Returns:
            True if download successful
        """
        if model_name not in MODEL_REGISTRY:
            logger.error(f"Unknown model: {model_name}")
            return False

        meta = MODEL_REGISTRY[model_name]

        if not meta.get("download"):
            logger.info(f"{model_name} is built-in or API-only, no download needed")
            return True

        local_path = self.cache_dir / meta["local_path"]

        # Check if already downloaded
        if local_path.exists() and not force:
            logger.info(f"Model {model_name} already cached at {local_path}")
            return True

        local_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            if meta["type"] == "huggingface":
                self._download_from_huggingface(meta["source"], str(local_path))
            elif meta["type"] == "remote_checkpoint":
                self._download_checkpoint(meta["source"], str(local_path))

            # Record in manifest
            self.manifest[model_name] = {
                "downloaded": True,
                "path": str(local_path),
                "source": meta["source"],
            }
            self._save_manifest()
            logger.info(f"Successfully downloaded {model_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to download {model_name}: {e}")
            return False

    def _download_from_huggingface(self, repo_id: str, output_path: str):
        """Download model from HuggingFace hub."""
        try:
            from transformers import AutoTokenizer, AutoModel

            logger.info(f"Downloading {repo_id} from HuggingFace...")
            tokenizer = AutoTokenizer.from_pretrained(repo_id)
            model = AutoModel.from_pretrained(repo_id)

            # Save tokenizer
            tokenizer.save_pretrained(output_path)
            # Save model
            model.save_pretrained(output_path)

        except ImportError:
            logger.error("transformers library not installed")
            raise

    def _download_checkpoint(self, url: str, output_path: str):
        """Download checkpoint from remote URL."""
        try:
            import urllib.request

            logger.info(f"Downloading checkpoint from {url}...")
            urllib.request.urlretrieve(url, output_path)

        except Exception as e:
            logger.error(f"Failed to download checkpoint: {e}")
            raise

    def load_model(self, model_name: str) -> Optional[Any]:
        """
        Load a pre-trained model into memory.

        Args:
            model_name: Model identifier

        Returns:
            Loaded model object or None if failed
        """
        if model_name in self.loaded_models:
            return self.loaded_models[model_name]

        if model_name not in MODEL_REGISTRY:
            logger.error(f"Unknown model: {model_name}")
            return None

        meta = MODEL_REGISTRY[model_name]

        try:
            if model_name.startswith("esm2"):
                model = self._load_esm2(meta)
            elif model_name.startswith("chemberta"):
                model = self._load_chemberta(meta)
            elif model_name.startswith("graphdta"):
                model = self._load_graphdta(meta)
            elif model_name == "rdkit":
                model = self._load_rdkit()
            elif model_name == "medgemma_7b":
                logger.warning("MedGemma-7B should be accessed via API, not loaded locally")
                return None
            else:
                logger.error(f"Unknown model type: {model_name}")
                return None

            self.loaded_models[model_name] = model
            logger.info(f"Loaded model: {model_name}")
            return model

        except Exception as e:
            logger.error(f"Failed to load {model_name}: {e}")
            return None

    def _load_esm2(self, meta: Dict) -> Any:
        """Load ESM-2 model."""
        from transformers import AutoTokenizer, AutoModel

        cache_path = self.cache_dir / meta["local_path"]

        if cache_path.exists():
            # Load from cache
            tokenizer = AutoTokenizer.from_pretrained(str(cache_path))
            model = AutoModel.from_pretrained(str(cache_path))
        else:
            # Load from HuggingFace
            logger.info("ESM-2 not cached, downloading...")
            tokenizer = AutoTokenizer.from_pretrained(meta["source"])
            model = AutoModel.from_pretrained(meta["source"])

        model.eval()  # Inference mode
        return {"tokenizer": tokenizer, "model": model}

    def _load_chemberta(self, meta: Dict) -> Any:
        """Load ChemBERTA model."""
        from transformers import AutoTokenizer, AutoModel

        cache_path = self.cache_dir / meta["local_path"]

        if cache_path.exists():
            tokenizer = AutoTokenizer.from_pretrained(str(cache_path))
            model = AutoModel.from_pretrained(str(cache_path))
        else:
            logger.info("ChemBERTA not cached, downloading...")
            tokenizer = AutoTokenizer.from_pretrained(meta["source"])
            model = AutoModel.from_pretrained(meta["source"])

        model.eval()
        return {"tokenizer": tokenizer, "model": model}

    def _load_graphdta(self, meta: Dict) -> Any:
        """Load GraphDTA checkpoint."""
        from core.ml.binding_affinity import GraphDTAModel

        cache_path = self.cache_dir / meta["local_path"]

        if not cache_path.exists():
            logger.warning("GraphDTA not cached. Please download first.")
            return None

        model = GraphDTAModel()
        model.load_state_dict(torch.load(cache_path, map_location="cpu"))
        model.eval()
        return model

    def _load_rdkit(self) -> Any:
        """Load RDKit (built-in, no download needed)."""
        try:
            from rdkit import Chem
            from rdkit.Chem import Descriptors, AllChem

            return {
                "Chem": Chem,
                "Descriptors": Descriptors,
                "AllChem": AllChem,
            }
        except ImportError:
            logger.error("RDKit not installed")
            return None

    def list_models(self) -> Dict[str, Dict]:
        """List all available models."""
        return MODEL_REGISTRY

    def get_model_info(self, model_name: str) -> Optional[Dict]:
        """Get info about a specific model."""
        return MODEL_REGISTRY.get(model_name)

    def is_loaded(self, model_name: str) -> bool:
        """Check if model is currently loaded."""
        return model_name in self.loaded_models

    def unload_model(self, model_name: str):
        """Unload a model from memory to free RAM."""
        if model_name in self.loaded_models:
            del self.loaded_models[model_name]
            logger.info(f"Unloaded {model_name}")

    def unload_all(self):
        """Unload all models from memory."""
        self.loaded_models.clear()
        logger.info("Unloaded all models")


# Global manager instance
_manager: Optional[ModelManager] = None


def get_model_manager(cache_dir: str = "models") -> ModelManager:
    """Get or create the global model manager."""
    global _manager
    if _manager is None:
        _manager = ModelManager(cache_dir)
    return _manager
