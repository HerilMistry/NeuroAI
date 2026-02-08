from data_ingestion.smiles_loader import load_smiles
from graph.similarity_graph import build_similarity_edges

smiles_list = [
    "CCO",      # ethanol
    "CCCO",     # propanol
    "c1ccccc1", # benzene
]

mols = [load_smiles(s) for s in smiles_list]
edges = build_similarity_edges(mols, threshold=0.3)

print("Molecule similarity edges:")
print(edges)
