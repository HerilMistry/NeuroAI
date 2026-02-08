import torch
import torch.nn.functional as F

def cosine_similarity_matrix(X):
    """
    Compute cosine similarity matrix between rows of X.
    """
    X_norm = F.normalize(X, dim=1)
    return torch.mm(X_norm, X_norm.t())

def build_learned_edges(sim_matrix, threshold=0.5):
    """
    Convert similarity matrix to edge list.
    """
    edges = []
    num_nodes = sim_matrix.size(0)

    for i in range(num_nodes):
        for j in range(num_nodes):
            if i != j and sim_matrix[i, j] >= threshold:
                edges.append((i, j))

    return edges

def mix_graphs(initial_adj, learned_adj, lam=0.7):
    """
    Mix initial and learned adjacency matrices.
    """
    return lam * initial_adj + (1 - lam) * learned_adj