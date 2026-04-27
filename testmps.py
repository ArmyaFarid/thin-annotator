import torch
print(f"MPS built? {torch.backends.mps.is_built()}")
print(f"MPS available? {torch.backends.mps.is_available()}")