# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#
# Modifications Copyright (c) 2025 Armya BAKOUAN -- see NOTICE for details.

from dataclasses import dataclass
from typing import List, Tuple

import numpy as np
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Mask:
    size: List[int]
    counts: str


@dataclass_json
@dataclass
class BaseRequest:
    type: str


@dataclass_json
@dataclass
class AddPointsImageRequest(BaseRequest):
    type: str
    image_id : str
    labels: List[int]
    points: List[List[float]]
    bboxes: List[List[float]]


@dataclass_json
@dataclass
class SlicImageRequest(BaseRequest):
    type: str
    image_id: str
    bbox: List[float]


@dataclass_json
@dataclass
class PropagateDataValue:
    object_id: int
    mask: Mask


@dataclass_json
@dataclass
class PropagateDataResponse:
    frame_index: int
    results: List[PropagateDataValue]


@dataclass_json
@dataclass
class PropagateLabelMapDataResponse:
    data: Tuple[np.ndarray, Tuple[int, int, int, int]]
