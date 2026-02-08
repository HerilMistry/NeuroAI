import torch.nn as nn
from torch_geometric.nn import GINConv, global_add_pool

class GINEncoder(nn.Module):
    def __init__(self, input_dim, hidden_dim):
        super().__init__()

        mlp = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim)
        )

        self.gin = GINConv(mlp)

    def forward(self, data):
        x = self.gin(data.x, data.edge_index)
        batch = data.batch
        return global_add_pool(x, batch)
