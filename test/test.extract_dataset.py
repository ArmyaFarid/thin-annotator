
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))


from dataset_manager.coco_extractor import build_dataset

# if len(sys.argv) != 3:
#     print("Usage: python build_dataset.py <root_dir> <output.zip>")
#     sys.exit(1)

def update_progress(action,current, total, filename):
    percent = (current / total) * 100
    print(f"{action} {filename} ({percent:.1f}%)")

build_dataset(
    root_dir="/Users/armyabakouan/Documents/ThinAnnotatorData/DOSSIER_LAMES",
    zip_output=True,
    output_dir="/Users/armyabakouan/Documents/ThinAnnotatorData/dataset.zip",
    progress_callback=update_progress
)