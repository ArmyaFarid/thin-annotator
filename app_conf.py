# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#
# Modifications Copyright (c) 2025 Armya BAKOUAN -- see NOTICE for details.

import logging
import os
from pathlib import Path
import sys

from system import filesystem

logger = logging.getLogger(__name__)

def get_flask_stattic_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS) / relative_path
    return Path(".") / relative_path

def get_writable_dir():
    # Option A: A hidden folder in the User's Home (Professional way)
    # macOS: /Users/name/.geosam
    # Windows: C:\Users\name\.geosam

    return filesystem.get_writable_dir()

APP_ROOT = os.getenv("APP_ROOT", get_flask_stattic_resource_path(""))

API_URL = os.getenv("API_URL", "http://localhost:7263")

MODEL_SIZE = os.getenv("MODEL_SIZE", "base_plus")

logger.info(f"using model size {MODEL_SIZE}")

# Path for all data used in API
DATA_PATH = Path(os.getenv("DATA_PATH",get_writable_dir()))

# Prefix for gallery images
GALLERY_PREFIX = "gallery"

# Path where all gallery images are stored
GALLERY_PATH = DATA_PATH / GALLERY_PREFIX

THUMBNAILS_PREFIX = "thumbs"

THUMBNAILS_PATH = DATA_PATH / THUMBNAILS_PREFIX


# Prefix for SAM-preprocessed images
SAM_PREPROCESSED_IMAGE_PREFIX = "sam-preprocessed"

# Path where all SAM-preprocessed images are stored
SAM_PREPROCESSED_IMAGE_PATH = get_writable_dir() / SAM_PREPROCESSED_IMAGE_PREFIX

# Make sure any of those paths exist
os.makedirs(DATA_PATH, exist_ok=True)
os.makedirs(GALLERY_PATH, exist_ok=True)
os.makedirs(THUMBNAILS_PATH, exist_ok=True)
os.makedirs(SAM_PREPROCESSED_IMAGE_PATH, exist_ok=True)


THIN_SECTION_FOV_SAMPLE_PATH = Path(os.getenv("THIN_SECTION_FOV_SAMPLE_PATH", "./data"))

