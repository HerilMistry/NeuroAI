import torch
from graph.gsl import cosine_similarity_matrix

X = torch.randn(3, 64)
S = cosine_similarity_matrix(X)

print(S)
