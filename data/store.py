# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#
# Modifications Copyright (c) 2025 Armya BAKOUAN -- see NOTICE for details.

#Modified : Add images 

from typing import Dict

from data.data_types import Image, Video

ALL_VIDEOS: Dict[str, Video] = []
 
ALL_IMAGES: Dict[str, Image] = []

def set_videos(videos: Dict[str, Video]) -> None:
    """
    Set the videos available in the backend. The data is kept in-memory, but a future change could replace the
    in-memory storage with a database backend. This would also be more efficient when querying videos given a
    dataset name etc.
    """
    global ALL_VIDEOS
    ALL_VIDEOS = videos


def get_videos() -> Dict[str, Video]:
    """
    Return the videos available in the backend.
    """
    global ALL_VIDEOS
    return ALL_VIDEOS


def set_images(images : Dict[str , Image]) -> None:
    global ALL_IMAGES
    ALL_IMAGES = images

def get_images() -> Dict[str , Image]:
    global ALL_IMAGES
    return ALL_IMAGES