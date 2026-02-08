import torch
import torch.nn as nn
from torch_geometric.nn import GCNConv

class MoleculeGNN(nn.Module):
    def __init__(self, input_dim, hidden_dim):
        super().__init__()
        self.conv = GCNConv(input_dim, hidden_dim)

    def forward(self, x, edge_index):
        return self.conv(x, edge_index)
