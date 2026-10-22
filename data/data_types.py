# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#
# Modifications Copyright (c) 2025 Armya BAKOUAN -- see NOTICE for details.

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


def unique_preserve_order(values):
    seen = set()
    result = []
    for v in values:
        if v not in seen:
            seen.add(v)
            result.append(v)
    return result


@dataclass
class Image:
    """Core type for image."""

    code: str                 # unique ID (FOVAsset id)
    path: str                 # image file path
    width: int
    height: int
    thumbnail_path: Optional[str] = None  # optional thumbnail


class PolarizedFilterType(Enum):
    PPL = "PPL"                  # Plane Polarized Light
    XPL = "XPL"                  # Cross Polarized Light (default angle)
    RL = "RL"                    # Reflected Light
    FL = "FL"                    # Fluorescence
    TR = "TR"                    # Transmitted light
    XPL_GAMMA = "XPL_GAMMA"
    OTHER = "OTHER"


@dataclass
class AcquiredImage:
    """
    Links an Image to its acquisition context (modality, angle, settings).
    This is the 'typed slot' in a Pairs set.
    """
    polarized_filter_type: PolarizedFilterType
    gamma: Optional[int]
    rotation: Optional[int]
    acquisition_label: Optional[str]
    image: Image


@dataclass
class Pairs:
    """
    A set of co-registered images for a single thin section sample.
    Each image is associated with a specific acquisition
    (XPL at angle, PPL, XPL with gamma, etc.).
    """
    pairs_code: str
    sample_id: str
    acquired_images: List[AcquiredImage]
    polarized_filter_types: List[PolarizedFilterType]
    rotations: List[Optional[int]]
    gammas: List[Optional[int]]
