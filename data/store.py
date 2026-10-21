# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#
# Modifications Copyright (c) 2025 Armya BAKOUAN -- see NOTICE for details.

#Modified : Add images 

from typing import Dict

from data.data_types import Image

ALL_IMAGES: Dict[str, Image] = []

def set_images(images : Dict[str , Image]) -> None:
    global ALL_IMAGES
    ALL_IMAGES = images

def get_images() -> Dict[str , Image]:
    global ALL_IMAGES
    return ALL_IMAGES