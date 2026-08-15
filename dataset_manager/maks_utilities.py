import json
import os
import numpy as np
from PIL import Image
from pycocotools import mask as mask_util
import argparse


def extract_binary_masks(json_path, output_dir):
    # Charger le fichier JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Récupérer le nom de fichier original (sans l'extension)
    orig_filename = data['image']['file_name']
    base_name = os.path.splitext(orig_filename)[0]

    # Créer le dossier de sortie s'il n'existe pas
    os.makedirs(output_dir, exist_ok=True)

    print(f"Extraction des masques pour : {orig_filename}")

    # Parcourir chaque annotation pour extraire les masques
    for idx, ann in enumerate(data['annotations']):
        # Extraire le format RLE compressé
        rle = {
            'counts': ann['segmentation']['counts'],
            'size': ann['segmentation']['size']
        }

        # pycocotools nécessite souvent que la chaîne soit encodée en bytes
        if isinstance(rle['counts'], str):
            rle['counts'] = rle['counts'].encode('utf-8')

        # Décoder le masque binaire (donne un tableau numpy avec des 0 et des 1)
        binary_mask = mask_util.decode(rle)

        # Récupérer les noms des minéraux (on les assemble avec un tiret s'il y en a plusieurs)
        mineral_ids = ann.get('mineralIds', [])
        mineral_name = "-".join(mineral_ids) if mineral_ids else f"mineral_{idx}"

        # Créer le nom du fichier du masque binaire final
        # Format: nom_mineral_nom_fichier_original_index.png
        out_name = f"{mineral_name}_{base_name}_{idx}.png"
        out_path = os.path.join(output_dir, out_name)

        # Convertir le tableau en image (0 pour le fond, 255 pour le masque)
        img = Image.fromarray((binary_mask * 255).astype(np.uint8))
        img.save(out_path)
        print(f" -> Sauvegardé : {out_path}")




