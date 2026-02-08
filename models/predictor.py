import torch.nn as nn

class Predictor(nn.Module):
    def __init__(self, input_dim):
        super().__init__()
        self.fc = nn.Linear(input_dim, 1)

    def forward(self, x):
        return self.fc(x)

def gsl_loss(adj_pred, labels):
    """
    Encourage similar labels to have strong connections.
    """
    loss = 0.0
    for i in range(len(labels)):
        for j in range(len(labels)):
            if labels[i] == labels[j]:
                loss += (1 - adj_pred[i, j])**2
    return loss
