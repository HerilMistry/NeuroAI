import torch
from graph.gsl import cosine_similarity_matrix, build_learned_edges

X = torch.randn(4, 64)
S = cosine_similarity_matrix(X)
edges = build_learned_edges(S, threshold=0.3)

print("Learned edges:", edges)
