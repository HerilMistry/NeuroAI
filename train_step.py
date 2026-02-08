import torch
from models.predictor import Predictor

# Fake labels (binary)
labels = torch.tensor([1., 1., 0.])

# Assume embeddings from Phase 3
X = torch.randn(3, 64)

predictor = Predictor(64)
optimizer = torch.optim.Adam(predictor.parameters(), lr=1e-3)

for epoch in range(100):
    logits = predictor(X).squeeze()
    loss = torch.nn.functional.binary_cross_entropy_with_logits(logits, labels)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    print(f"Epoch {epoch}, Loss {loss.item():.4f}")
