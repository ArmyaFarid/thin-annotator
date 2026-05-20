# Copyright (c) 2025 Armya BAKOUAN.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file in the root directory of this source tree.

import torch
print(f"MPS built? {torch.backends.mps.is_built()}")
print(f"MPS available? {torch.backends.mps.is_available()}")