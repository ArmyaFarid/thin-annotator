import csv
import os
from collections import defaultdict

from app_conf import CSV_PATH

_PAIRS_CACHE = None


def load_pairs_csv():
    global _PAIRS_CACHE

    if _PAIRS_CACHE is not None:
        return _PAIRS_CACHE

    grouped = defaultdict(list)

    with open(CSV_PATH, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            grouped[row["pair_code"]].append(row)

    _PAIRS_CACHE = grouped
    return grouped

def save_sam_cache_path(image_path: str, sam_cache_path: str):
    global _PAIRS_CACHE

    rows = []
    updated = False
    image_name = os.path.basename(image_path)

    with open(CSV_PATH, newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            if os.path.basename(row["image"]) == image_name:
                row["sam_cache"] = sam_cache_path
                updated = True
            rows.append(row)

    if not updated:
        raise ValueError(f"No row found with image name: {image_name}")

    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    _PAIRS_CACHE = None


def get_row_by_image_path(image_path: str) -> dict | None:
    image_name = os.path.basename(image_path)
    pairs = load_pairs_csv()
    for rows in pairs.values():
        for row in rows:
            if os.path.basename(row["image"]) == image_name:
                return row
    return None