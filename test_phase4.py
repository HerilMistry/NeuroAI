import torch
from graph.gsl import cosine_similarity_matrix, mix_graphs

# Fake embeddings
X = torch.randn(3, 64)

# Initial adjacency (from Phase 2, simulated here)
A0 = torch.tensor([
    [0, 1, 0],
    [1, 0, 0],
    [0, 0, 0]
], dtype=torch.float)

# Learned adjacency
A_learned = cosine_similarity_matrix(X)

A_final = mix_graphs(A0, A_learned, lam=0.6)

print(A_final)
