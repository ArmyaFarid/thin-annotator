import argparse
import sys
from pathlib import Path


sys.path.append(str(Path(__file__).resolve().parents[1]))
from dataset_manager.maks_utilities import extract_binary_masks

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convertir JSON COCO-RLE en masques binaires"
    )
    parser.add_argument("--json", type=str, help="Chemin vers le fichier JSON")
    parser.add_argument("--output", type=str, help="Dossier de sortie")

    args = parser.parse_args()

    json_file = args.json or input(
        "Chemin vers le fichier JSON [data.json] : "
    ).strip() or "data.json"

    output_dir = args.output or input(
        "Dossier de sortie [masques_extraits] : "
    ).strip() or "masques_extraits"

    extract_binary_masks(json_file, output_dir)