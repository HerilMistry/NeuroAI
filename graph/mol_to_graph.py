import torch
from torch_geometric.data import Data
from .atom_features import atom_features
from .bond_features import bond_edges

def mol_to_graph(mol):
    """
    Convert RDKit molecule to PyTorch Geometric graph.
    """
    x = torch.tensor(
        [atom_features(atom) for atom in mol.GetAtoms()],
        dtype=torch.float
    )

    edges = bond_edges(mol)
    edge_index = torch.tensor(edges, dtype=torch.long).t()

    return Data(x=x, edge_index=edge_index)
