import csv
from collections import defaultdict

_PAIRS_CACHE = None

def load_pairs_csv():
    csv_path = "/Users/armyabakouan/UQAC/RESEARCH/experiments/web/sam2/backend/server/data/gallery/image_pairs.csv"
    global _PAIRS_CACHE

    if _PAIRS_CACHE is not None:
        return _PAIRS_CACHE

    grouped = defaultdict(list)

    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            grouped[row["pair_code"]].append(row)

    _PAIRS_CACHE = grouped
    return grouped