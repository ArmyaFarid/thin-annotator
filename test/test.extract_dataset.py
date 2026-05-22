from dataset_manager.coca_extractor import build_dataset

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python build_dataset.py <root_dir> <output.zip>")
        sys.exit(1)

    build_dataset(root_dir="/Users/armyabakouan/Documents/ThinAnnotatorData/DOSSIER_LAMES", output_zip_path="/Users/armyabakouan/Documents/ThinAnnotatorData/dataset.zip")