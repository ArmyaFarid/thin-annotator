import base64
from typing import Tuple

import numpy as np


def encode_label_map(label_map: Tuple[np.ndarray, Tuple[int, int, int, int]]) -> dict:
    arr, (x0, y0, w, h) = label_map

    arr = np.ascontiguousarray(arr, dtype=np.uint16)

    return {
        "data": base64.b64encode(arr.tobytes()).decode("ascii"),
        "height": arr.shape[0],
        "width": arr.shape[1],
        "dtype": str(arr.dtype),
        "bbox": {"x": x0, "y": y0, "w": w, "h": h},
    }
