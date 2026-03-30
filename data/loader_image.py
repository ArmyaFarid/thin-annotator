# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.


#modified add preload image

import os
import shutil
import subprocess
from glob import glob
from pathlib import Path
from typing import Dict, Optional

import imagesize
from app_conf import GALLERY_PATH, POSTERS_PATH, POSTERS_PREFIX, THUMBNAILS_PATH, THUMBNAILS_PREFIX
from data.data_types import Image, Video
from tqdm import tqdm


def preload_data_img() -> Dict[str, Image]:
    """
    Preload images from the gallery and optionally generate thumbnails.
    """
    all_images = {}

    # Find all image files (jpg, png, etc.) recursively
    image_path_pattern = os.path.join(GALLERY_PATH, "**/*.[jp][pn]g")
    image_paths = glob(image_path_pattern, recursive=True)

    image_paths += glob(os.path.join(GALLERY_PATH, "**/*.bmp"), recursive=True)

    for p in tqdm(image_paths):
        image = get_image(p, GALLERY_PATH)
        all_images[image.code] = image

    return all_images


def get_image(
    filepath: os.PathLike,
    absolute_path: Path,
    file_key: Optional[str] = None,
    generate_thumbnail: bool = True,
    verbose: Optional[bool] = False,
) -> Image:
    """
    Create an Image object from a file path.
    """
    # Relative path to gallery root
    image_path = os.path.relpath(filepath, absolute_path.parent)

    thumbnail_path = None
    if generate_thumbnail:
        # Example: generate a simple copy or resize for thumbnail
        thumbnail_filename = os.path.splitext(os.path.basename(filepath))[0] + ".jpg"
        thumbnail_path = f"{THUMBNAILS_PREFIX}/{thumbnail_filename}"
        thumbnail_output_path = os.path.join(THUMBNAILS_PATH, thumbnail_filename)

        # For simplicity, just copy or use PIL to resize
        try:
            from PIL import Image as PILImage

            img = PILImage.open(filepath)
            img.thumbnail((200, 200))  # small thumbnail
            img.save(thumbnail_output_path)
        except Exception as e:
            if verbose:
                print(f"Failed to generate thumbnail for {filepath}: {e}")
            thumbnail_path = None

    # Get image dimensions
    width, height = imagesize.get(filepath)

    return Image(
        code=image_path if file_key is None else file_key,
        path=image_path,
        thumbnail_path=thumbnail_path,
        width=width,
        height=height,
    )