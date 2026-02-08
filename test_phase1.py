import torch
from data_ingestion.smiles_loader import load_smiles
from graph.mol_to_graph import mol_to_graph
from models.gin_encoder import GINEncoder

# Load molecule
mol = load_smiles("CCO")

# Convert to graph
data = mol_to_graph(mol)
data.batch = torch.zeros(data.x.size(0), dtype=torch.long)

# Model
model = GINEncoder(input_dim=data.x.size(1), hidden_dim=64)

# Forward pass
embedding = model(data)
print("Molecule embedding shape:", embedding.shape)
