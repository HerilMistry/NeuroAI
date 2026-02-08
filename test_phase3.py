import torch
from data_ingestion.smiles_loader import load_smiles
from graph.mol_to_graph import mol_to_graph
from graph.similarity_graph import build_similarity_edges
from models.gin_encoder import GINEncoder
from models.molecule_gnn import MoleculeGNN

# Input molecules
smiles_list = ["CCO", "CCCO", "c1ccccc1"]
mols = [load_smiles(s) for s in smiles_list]

# Encode molecules
gin = GINEncoder(input_dim=3, hidden_dim=64)
embeddings = []

for mol in mols:
    data = mol_to_graph(mol)
    data.batch = torch.zeros(data.x.size(0), dtype=torch.long)
    emb = gin(data)
    embeddings.append(emb)

X = torch.cat(embeddings, dim=0)  # [num_molecules, 64]

# Similarity graph
edges = build_similarity_edges(mols, threshold=0.3)
edge_index = torch.tensor(edges, dtype=torch.long).t()

# Molecule-level GNN
mol_gnn = MoleculeGNN(input_dim=64, hidden_dim=64)
updated_embeddings = mol_gnn(X, edge_index)

print("Updated embeddings shape:", updated_embeddings.shape)
