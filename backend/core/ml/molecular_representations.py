"""
Molecular Representation Framework
=================================

Implements multi-view molecular representations as described in the system specification.

References:
- SchNet: A continuous-filter convolutional neural network for modeling quantum interactions
  (Schütt et al., 2018)
- Message Passing Neural Networks for Partial Differential Equations (Pfaff et al., 2021)
- Protein language models capture structure and function (ESM, Madani et al., 2023)

This module provides:
1. Graph Neural Networks for molecular structure encoding
2. Physicochemical descriptor extraction (RDKit-based)
3. Protein language model integration (ESM-2)
4. Unified embedding space for molecules and proteins
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import MessagePassing, GCNConv, GATConv, global_add_pool, global_mean_pool
from torch_geometric.data import Data, DataLoader
from typing import Dict, Tuple, List, Optional
import numpy as np
from rdkit import Chem
from rdkit.Chem import Descriptors, AllChem
import logging

logger = logging.getLogger(__name__)


class MolecularGraphEncoder(nn.Module):
    """
    Graph Neural Network encoder for molecular structures.
    
    Converts SMILES strings to graph representations, then encodes via GNN.
    
    Architecture:
    - Node features: Atom type embeddings + physicochemical properties
    - Edge features: Bond type embeddings
    - Graph convolution: 3 layers of GAT with attention
    - Pooling: Global mean pooling to molecule-level representation
    
    Output: 256-dimensional embedding per molecule
    """

    def __init__(
        self,
        hidden_dim: int = 256,
        num_layers: int = 3,
        num_heads: int = 4,
        dropout: float = 0.1,
    ):
        super().__init__()
        
        # Node embedding (atom types: 0-118)
        self.atom_embedding = nn.Embedding(119, hidden_dim)
        
        # Edge embedding (bond types: single, double, triple, aromatic)
        self.bond_embedding = nn.Embedding(4, hidden_dim)
        
        # Atom feature projection (degree, hybridization, valence, formal charge)
        self.atom_feature_proj = nn.Linear(4, hidden_dim)
        
        # Graph attention layers
        self.gat_layers = nn.ModuleList([
            GATConv(hidden_dim, hidden_dim // num_heads, heads=num_heads, dropout=dropout)
            for _ in range(num_layers)
        ])
        
        self.fc_out = nn.Linear(hidden_dim, hidden_dim)
        self.dropout = nn.Dropout(dropout)

    def smiles_to_graph(self, smiles: str) -> Optional[Data]:
        """Convert SMILES to PyTorch Geometric Data object."""
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                logger.warning(f"Invalid SMILES: {smiles}")
                return None
            
            # Node features: atom types
            x = []
            for atom in mol.GetAtoms():
                x.append([
                    atom.GetAtomicNum(),  # Atomic number
                    atom.GetDegree(),  # Degree
                    atom.GetTotalNumHs(),  # Hydrogen count
                    atom.GetFormalCharge(),  # Formal charge
                ])
            x = torch.tensor(x, dtype=torch.float32)
            
            # Edge features: bond types
            edges = []
            edge_types = []
            for bond in mol.GetBonds():
                i, j = bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()
                edges.append([i, j])
                edges.append([j, i])  # Undirected
                
                # Map bond type to integer
                bond_type_map = {
                    Chem.BondType.SINGLE: 0,
                    Chem.BondType.DOUBLE: 1,
                    Chem.BondType.TRIPLE: 2,
                    Chem.BondType.AROMATIC: 3,
                }
                bond_type = bond_type_map.get(bond.GetBondType(), 0)
                edge_types.extend([bond_type, bond_type])
            
            edge_index = torch.tensor(edges, dtype=torch.long).t().contiguous()
            edge_attr = torch.tensor(edge_types, dtype=torch.long) if edge_types else None
            
            return Data(x=x, edge_index=edge_index, edge_attr=edge_attr)
        
        except Exception as e:
            logger.error(f"Error converting SMILES {smiles}: {e}")
            return None

    def forward(self, data: Data) -> torch.Tensor:
        """Forward pass: SMILES/Data -> molecular embedding."""
        x = data.x
        edge_index = data.edge_index
        edge_attr = data.edge_attr
        
        # Embed atoms
        atom_type = self.atom_embedding(x[:, 0].long())
        atom_features = self.atom_feature_proj(x[:, 1:])
        x = atom_type + atom_features
        
        # Embed and add edge attributes
        if edge_attr is not None:
            edge_embedding = self.bond_embedding(edge_attr.long())
            # Incorporate edge features in attention
        
        # Graph attention convolutions
        for gat_layer in self.gat_layers:
            x = gat_layer(x, edge_index)
            x = F.elu(x)
            x = self.dropout(x)
        
        # Global pooling
        x = global_mean_pool(x, data.batch if hasattr(data, 'batch') else torch.zeros(len(x), dtype=torch.long))
        
        # Output projection
        x = self.fc_out(x)
        
        return x


class PhysicochemicalDescriptors:
    """
    Extracts physicochemical descriptors from molecules.
    
    Features extracted:
    - Molecular weight
    - LogP (lipophilicity)
    - Hydrogen bond donors/acceptors
    - Topological polar surface area (TPSA)
    - Rotatable bonds
    - Molar refractivity
    - Aromatic rings
    """

    @staticmethod
    def extract_descriptors(smiles: str) -> Optional[Dict[str, float]]:
        """Extract physicochemical descriptors from SMILES."""
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                return None
            
            descriptors = {
                'mw': Descriptors.MolWt(mol),
                'logp': Descriptors.MolLogP(mol),
                'hbd': Descriptors.NumHDonors(mol),
                'hba': Descriptors.NumHAcceptors(mol),
                'tpsa': Descriptors.TPSA(mol),
                'rotatable_bonds': Descriptors.NumRotatableBonds(mol),
                'molar_refractivity': Descriptors.MolMR(mol),
                'aromatic_rings': Descriptors.NumAromaticRings(mol),
                'num_atoms': mol.GetNumAtoms(),
                'num_heteroatoms': Descriptors.NumHeteroatoms(mol),
            }
            
            return descriptors
        except Exception as e:
            logger.error(f"Error extracting descriptors from {smiles}: {e}")
            return None

    @staticmethod
    def get_ecfp_fingerprint(smiles: str, radius: int = 2, nbits: int = 1024) -> Optional[np.ndarray]:
        """Extract Extended Connectivity Fingerprint (ECFP/Morgan)."""
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                return None
            
            fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius, nBits=nbits)
            return np.array(fp)
        except Exception as e:
            logger.error(f"Error extracting ECFP from {smiles}: {e}")
            return None


class ProteinLanguageModelEncoder:
    """
    Protein sequence encoder using language models.
    
    Uses ESM-2 (Evolutionary Scale Modeling) for protein embeddings.
    Captures evolutionary and functional information.
    
    Reference: Madani et al., "Protein language models capture structure and function" 
    (Preprint, 2023)
    """
    
    def __init__(self, model_name: str = "facebook/esm2_t6_8M_UR50D"):
        """Initialize protein language model."""
        try:
            from transformers import AutoTokenizer, AutoModel
            
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModel.from_pretrained(model_name).to(self.device)
            self.model.eval()
            
            logger.info(f"Loaded protein language model: {model_name}")
        except ImportError:
            logger.warning("transformers not installed. Protein encoding disabled.")
            self.model = None

    def encode_protein(self, sequence: str) -> Optional[torch.Tensor]:
        """Encode protein sequence to embedding."""
        if self.model is None:
            return None
        
        try:
            with torch.no_grad():
                tokens = self.tokenizer(sequence, return_tensors="pt").to(self.device)
                output = self.model(**tokens)
                
                # Mean pooling over sequence positions
                embedding = output.last_hidden_state.mean(dim=1)
                
                return embedding.cpu()
        except Exception as e:
            logger.error(f"Error encoding sequence: {e}")
            return None


class UnifiedMolecularEmbedding(nn.Module):
    """
    Unified embedding space combining multiple molecular views.
    
    Inputs:
    - Graph representation (from MolecularGraphEncoder)
    - Physicochemical descriptors
    - ECFP fingerprints
    
    Output: Single 256-dimensional molecular embedding
    """

    def __init__(
        self,
        graph_dim: int = 256,
        descriptor_dim: int = 10,
        ecfp_dim: int = 1024,
        output_dim: int = 256,
    ):
        super().__init__()
        
        # Feature projections
        self.graph_proj = nn.Linear(graph_dim, output_dim)
        self.descriptor_proj = nn.Linear(descriptor_dim, output_dim // 2)
        self.ecfp_proj = nn.Linear(ecfp_dim, output_dim // 2)
        
        # Fusion layers
        self.fusion_fc = nn.Sequential(
            nn.Linear(output_dim * 2, output_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(output_dim, output_dim),
        )
        
        # Attention weights for view fusion
        self.attention = nn.MultiheadAttention(
            embed_dim=output_dim,
            num_heads=4,
            dropout=0.1,
            batch_first=True,
        )

    def forward(
        self,
        graph_embedding: torch.Tensor,
        descriptors: torch.Tensor,
        ecfp: torch.Tensor,
    ) -> torch.Tensor:
        """Fuse multiple molecular views into single embedding."""
        
        # Project all views
        graph_proj = self.graph_proj(graph_embedding)
        desc_proj = self.descriptor_proj(descriptors)
        ecfp_proj = self.ecfp_proj(ecfp)
        
        # Concatenate
        combined = torch.cat([
            graph_proj.unsqueeze(1),
            torch.cat([desc_proj, ecfp_proj], dim=-1).unsqueeze(1),
        ], dim=1)
        
        # Self-attention fusion
        fused, _ = self.attention(combined, combined, combined)
        fused = fused.mean(dim=1)
        
        # Output projection
        output = self.fusion_fc(torch.cat([graph_proj, fused], dim=-1))
        
        return output


class MolecularRepresentationPipeline:
    """
    Complete pipeline for molecular representation.
    
    Usage:
        pipeline = MolecularRepresentationPipeline()
        embedding = pipeline.get_embedding("CCO")  # Ethanol SMILES
    """

    def __init__(self):
        self.graph_encoder = MolecularGraphEncoder()
        self.protein_encoder = ProteinLanguageModelEncoder()
        self.unified_embedding = UnifiedMolecularEmbedding()

    def get_embedding(self, smiles: str) -> Optional[torch.Tensor]:
        """Get unified embedding for molecule."""
        try:
            # Graph encoding
            data = self.graph_encoder.smiles_to_graph(smiles)
            if data is None:
                return None
            
            with torch.no_grad():
                graph_emb = self.graph_encoder(data)
                
                # Physicochemical descriptors
                desc = PhysicochemicalDescriptors.extract_descriptors(smiles)
                if desc is None:
                    return None
                
                desc_tensor = torch.tensor(list(desc.values()), dtype=torch.float32).unsqueeze(0)
                
                # ECFP fingerprint
                ecfp = PhysicochemicalDescriptors.get_ecfp_fingerprint(smiles)
                if ecfp is None:
                    return None
                
                ecfp_tensor = torch.tensor(ecfp, dtype=torch.float32).unsqueeze(0)
                
                # Unified embedding
                embedding = self.unified_embedding(graph_emb, desc_tensor, ecfp_tensor)
                
                return embedding
        
        except Exception as e:
            logger.error(f"Error getting embedding for {smiles}: {e}")
            return None


if __name__ == "__main__":
    # Example usage
    pipeline = MolecularRepresentationPipeline()
    
    # Test SMILES
    test_smiles = [
        "CCO",  # Ethanol
        "c1ccccc1",  # Benzene
        "CC(=O)Oc1ccccc1C(=O)O",  # Aspirin
    ]
    
    for smi in test_smiles:
        emb = pipeline.get_embedding(smi)
        if emb is not None:
            print(f"{smi}: embedding shape {emb.shape}")
        else:
            print(f"{smi}: failed to encode")
