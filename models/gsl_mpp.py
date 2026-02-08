import torch
import torch.nn as nn

from models.gin_encoder import GINEncoder
from models.molecule_gnn import MoleculeGNN
from models.predictor import Predictor
from graph.gsl import cosine_similarity_matrix, mix_graphs

class GSLMPP(nn.Module):
    def __init__(self, atom_feat_dim, hidden_dim):
        super().__init__()
        self.encoder = GINEncoder(atom_feat_dim, hidden_dim)
        self.mol_gnn = MoleculeGNN(hidden_dim, hidden_dim)
        self.predictor = Predictor(hidden_dim)

    def forward(self, mol_graphs, A0):
        """
        mol_graphs: list of PyG molecular graphs
        A0: initial adjacency matrix
        """
        embeddings = []

        for g in mol_graphs:
            emb = self.encoder(g)
            embeddings.append(emb)

        H = torch.cat(embeddings, dim=0)

        # Learn graph
        A_learned = cosine_similarity_matrix(H)
        A = mix_graphs(A0, A_learned)

        edge_index = torch.nonzero(A > 0.3).t()
        H_updated = self.mol_gnn(H, edge_index)

        logits = self.predictor(H_updated).squeeze()
        return logits, A
