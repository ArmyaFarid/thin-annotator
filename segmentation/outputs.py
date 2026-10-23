from dataclasses import dataclass
from typing import List, Tuple, Union

import numpy as np
from pycocotools.mask import encode as encode_rle


@dataclass
class RleMask:
    counts: str
    size: List[int]

    @classmethod
    def from_binary_mask(cls, mask: np.ndarray) -> "RleMask":
        rle = encode_rle(np.array(mask, dtype=np.uint8, order="F"))
        return cls(counts=rle["counts"].decode(), size=rle["size"])


@dataclass
class MaskList:
    image_width: int
    image_height: int
    masks: List[RleMask]

    @classmethod
    def from_binary_masks(cls, masks: List[np.ndarray], image_hw: Tuple[int, int]) -> "MaskList":
        height, width = image_hw
        return cls(image_width=width, image_height=height, masks=[RleMask.from_binary_mask(m) for m in masks])


@dataclass
class LabelMap:
    image_width: int
    image_height: int
    x: int
    y: int
    labels: np.ndarray


SegmentationOutput = Union[MaskList, LabelMap]
