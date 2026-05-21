import json
import os
import random
from glob import glob

import numpy as np
from PIL import Image
from pycocotools import mask as mask_utils

MINERAL_COLORS = {
    # tectosilicates — blues
    "qtz":  [0.55, 0.75, 1.00],
    "kfs":  [0.20, 0.40, 0.90],
    "plag": [0.45, 0.60, 0.95],
    # phyllosilicates — greens
    "ms":   [0.60, 0.90, 0.40],
    "bt":   [0.20, 0.60, 0.20],
    "chl":  [0.10, 0.80, 0.50],
    "srp":  [0.40, 0.75, 0.35],
    # inosilicates — purples
    "hbl":  [0.65, 0.25, 0.80],
    "aug":  [0.50, 0.15, 0.65],
    "hyp":  [0.80, 0.45, 0.90],
    # nesosilicates — reds/oranges
    "ol":   [0.10, 0.80, 0.20],
    "grt":  [1.00, 0.15, 0.15],
    "zrn":  [1.00, 0.55, 0.10],
    # cyclosilicates — cyan
    "tur":  [0.00, 0.85, 0.85],
    # sorosilicates — yellow-green
    "ep":   [0.75, 0.90, 0.10],
    "ttn":  [0.90, 0.80, 0.00],
    # carbonates — pinks
    "cal":  [1.00, 0.65, 0.80],
    "dol":  [0.90, 0.40, 0.70],
    # oxides — dark red/grey
    "mag":  [0.25, 0.25, 0.25],
    "ilm":  [0.45, 0.20, 0.10],
    "hem":  [0.75, 0.10, 0.00],
    # phosphates — gold
    "ap":   [0.95, 0.85, 0.20],
}
DEFAULT_COLOR = [0.5, 0.5, 0.5]

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TESTDATA_DIR = os.path.join(SCRIPT_DIR, "testdata")

annotation_files = glob(
    os.path.join(TESTDATA_DIR, "*-annotation.json")
)

random_file = random.choice(annotation_files)

with open(random_file, "r") as f:
    data = json.load(f)

image = data["image"]

image_path = os.path.join(TESTDATA_DIR, image["file_name"])

img = Image.open(image_path).convert("RGBA")
result = np.array(img, dtype=np.float32) / 255.0

ALPHA = 0.5

for ann in data["annotations"]:
    seg = ann["segmentation"]
    rle = {"counts": seg["counts"], "size": seg["size"]}
    binary_mask = mask_utils.decode(rle).astype(bool)

    mineral_ids = ann.get("mineralIds", [])
    mineral = mineral_ids[0].lower() if mineral_ids else ""
    color = np.array(MINERAL_COLORS.get(mineral, DEFAULT_COLOR))

    result[binary_mask, :3] = (1 - ALPHA) * result[binary_mask, :3] + ALPHA * color
    result[binary_mask, 3] = 1.0

out = Image.fromarray((result * 255).astype(np.uint8), "RGBA")

base, ext = os.path.splitext(image_path)
saved_overlay_file = f"{base}-overlay.png"

out.save(saved_overlay_file)
print(f"Saved {saved_overlay_file}")