import numpy as np
from PIL import Image


def load_rgb(path: str) -> np.ndarray:
    return np.array(Image.open(path).convert("RGB"))
