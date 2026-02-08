import torch
from data_ingestion.smiles_loader import load_smiles
from graph.mol_to_graph import mol_to_graph
from graph.similarity_graph import build_similarity_edges
from models.gsl_mpp import GSLMPP

# Dataset (toy for now)
smiles = ["CCO", "CCCO", "c1ccccc1"]
labels = torch.tensor([1., 1., 0.])

# Load molecules
mols = [load_smiles(s) for s in smiles]
graphs = []

for mol in mols:
    g = mol_to_graph(mol)
    g.batch = torch.zeros(g.x.size(0), dtype=torch.long)
    graphs.append(g)

# Initial adjacency
edges = build_similarity_edges(mols, threshold=0.3)
A0 = torch.zeros(len(mols), len(mols))
for i, j in edges:
    A0[i, j] = 1

# Model
model = GSLMPP(atom_feat_dim=3, hidden_dim=64)
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
criterion = torch.nn.BCEWithLogitsLoss()

# Training loop
for epoch in range(30):
    logits, A = model(graphs, A0)
    loss = criterion(logits, labels)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    print(f"Epoch {epoch}, Loss {loss.item():.4f}")
