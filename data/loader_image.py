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
from app_conf import GALLERY_PATH, POSTERS_PATH, POSTERS_PREFIX, THUMBNAILS_PATH, THUMBNAILS_PREFIX,THIN_SECTION_FOV_SAMPLE_PATH
from data.data_types import Image, Video
from tqdm import tqdm

from data.parsers.fov_file_parser import parse_fov_filename
from extensions import db

from models import FOVAsset


def init_thin_section_fov_images():
    fov_images_path = THIN_SECTION_FOV_SAMPLE_PATH
    fov_id = fov_images_path.name
    thin_section_id = fov_images_path.parent.name

    print(f"Syncing folder: {thin_section_id} / {fov_id}")
    extensions = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp"}

    new_assets = []
    
    for file_path in fov_images_path.iterdir():
        if file_path.suffix.lower() in extensions:
            image_name = file_path.name
            image_path_str = str(file_path)
            fov_metadata = parse_fov_filename(image_name)

            # Look for the existing record by image_path
            existing_asset = db.session.query(FOVAsset).filter_by(
                image_path=image_path_str
            ).first()

            if existing_asset:
                # --- UPDATE LOGIC ---
                print(f"Updating existing asset: {image_name}")
                existing_asset.thin_section_id = thin_section_id
                existing_asset.fov_id = fov_id
                existing_asset.lighting_modality = fov_metadata["lighting_modality"]
                existing_asset.gamma = fov_metadata["gamma"]
                existing_asset.stage_angle = fov_metadata["stage_angle"]
                existing_asset.sample_path = str(fov_images_path.parent)
            else:
                # --- INSERT LOGIC ---
                print(f"Creating new asset: {image_name}")
                new_asset = FOVAsset(
                    image_path=image_path_str,
                    thin_section_id=thin_section_id,
                    fov_id=fov_id,
                    lighting_modality=fov_metadata["lighting_modality"],
                    gamma=fov_metadata["gamma"],
                    stage_angle=fov_metadata["stage_angle"],
                    sample_path=str(fov_images_path.parent)
                )
                new_assets.append(new_asset)

    if new_assets:
        db.session.add_all(new_assets)
    db.session.commit()
    print("Database sync complete.")
    return 0

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

    width, height = -1,-1

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
            width, height= img.width, img.height
            img.thumbnail((200, 200))  # small thumbnail
            img.save(thumbnail_output_path)
        except Exception as e:
            if verbose:
                print(f"Failed to generate thumbnail for {filepath}: {e}")
            thumbnail_path = None

    # Get image dimensions
    # width, height = imagesize.get(filepath)

    return Image(
        code=image_path if file_key is None else file_key,
        path=image_path,
        thumbnail_path=thumbnail_path,
        width=width,
        height=height,
    )