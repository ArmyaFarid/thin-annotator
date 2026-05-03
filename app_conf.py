# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

import logging
import os
from pathlib import Path
import sys

logger = logging.getLogger(__name__)

def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS) / relative_path
    return Path(".") / relative_path

def get_writable_dir():
    # Option A: A hidden folder in the User's Home (Professional way)
    # macOS: /Users/name/.geosam
    # Windows: C:\Users\name\.geosam
    path = Path.home() / ".geosam"
    path.mkdir(parents=True, exist_ok=True)
    return path

APP_ROOT = os.getenv("APP_ROOT", get_resource_path(""))

API_URL = os.getenv("API_URL", "http://localhost:7263")

MODEL_SIZE = os.getenv("MODEL_SIZE", "base_plus")

logger.info(f"using model size {MODEL_SIZE}")

FFMPEG_NUM_THREADS = int(os.getenv("FFMPEG_NUM_THREADS", "1"))

# Path for all data used in API
DATA_PATH = Path(os.getenv("DATA_PATH", "/Users/armyabakouan/UQAC/RESEARCH/experiments/web/sam2/data"))

# Max duration an uploaded video can have in seconds. The default is 10
# seconds.
MAX_UPLOAD_VIDEO_DURATION = float(os.environ.get("MAX_UPLOAD_VIDEO_DURATION", "10"))

# If set, it will define which video is returned by the default video query for
# desktop
DEFAULT_VIDEO_PATH = os.getenv("DEFAULT_VIDEO_PATH")

# Prefix for gallery videos
GALLERY_PREFIX = "gallery"

# Path where all gallery videos are stored
GALLERY_PATH = DATA_PATH / GALLERY_PREFIX

# Prefix for uploaded videos
UPLOADS_PREFIX = "uploads"

# Path where all uploaded videos are stored
UPLOADS_PATH = DATA_PATH / UPLOADS_PREFIX

# Prefix for video posters (1st frame of video)
POSTERS_PREFIX = "posters"

THUMBNAILS_PREFIX = "thumbs"

THUMBNAILS_PATH = DATA_PATH / THUMBNAILS_PREFIX

# Path where all posters are stored
POSTERS_PATH = DATA_PATH / POSTERS_PREFIX


# Prefix for uploaded videos
SAM_PREPROCESSED_IMAGE_PREFIX = "sam-preprocessed"

# Path where all uploaded videos are stored
SAM_PREPROCESSED_IMAGE_PATH = get_writable_dir() / SAM_PREPROCESSED_IMAGE_PREFIX

CSV_PATH = "/Users/armyabakouan/UQAC/RESEARCH/experiments/web/sam2/backend/server/data/gallery/image_pairs.csv"

# Make sure any of those paths exist
os.makedirs(DATA_PATH, exist_ok=True)
os.makedirs(GALLERY_PATH, exist_ok=True)
os.makedirs(UPLOADS_PATH, exist_ok=True)
os.makedirs(POSTERS_PATH, exist_ok=True)
os.makedirs(THUMBNAILS_PATH, exist_ok=True)
os.makedirs(SAM_PREPROCESSED_IMAGE_PATH, exist_ok=True)
