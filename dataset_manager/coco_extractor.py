import os
import json
import zipfile
import traceback
import shutil
from pathlib import Path
from datetime import datetime

# ─── CONFIG ───────────────────────────────────────────────────────────────────
COMPUTE_BBOX = True  # Set True to compute bbox/area via pycocotools
# ──────────────────────────────────────────────────────────────────────────────

MINERALS = [
    {"id": 1, "value": "qtz", "label": {"fr": "Quartz", "en": "Quartz"}, "group": "tectosilicates"},
    {"id": 2, "value": "kfs", "label": {"fr": "Feldspath K", "en": "K-feldspar"}, "group": "tectosilicates"},
    {"id": 3, "value": "plag", "label": {"fr": "Plagioclase", "en": "Plagioclase"}, "group": "tectosilicates"},
    {"id": 4, "value": "ms", "label": {"fr": "Muscovite", "en": "Muscovite"}, "group": "phyllosilicates"},
    {"id": 5, "value": "bt", "label": {"fr": "Biotite", "en": "Biotite"}, "group": "phyllosilicates"},
    {"id": 6, "value": "chl", "label": {"fr": "Chlorite", "en": "Chlorite"}, "group": "phyllosilicates"},
    {"id": 7, "value": "srp", "label": {"fr": "Serpentine", "en": "Serpentine"}, "group": "phyllosilicates"},
    {"id": 8, "value": "hbl", "label": {"fr": "Hornblende", "en": "Hornblende"}, "group": "inosilicates"},
    {"id": 9, "value": "aug", "label": {"fr": "Augite", "en": "Augite"}, "group": "inosilicates"},
    {"id": 10, "value": "hyp", "label": {"fr": "Hypersthène", "en": "Hypersthene"}, "group": "inosilicates"},
    {"id": 11, "value": "ol", "label": {"fr": "Olivine", "en": "Olivine"}, "group": "nesosilicates"},
    {"id": 12, "value": "grt", "label": {"fr": "Grenat", "en": "Garnet"}, "group": "nesosilicates"},
    {"id": 13, "value": "zrn", "label": {"fr": "Zircon", "en": "Zircon"}, "group": "nesosilicates"},
    {"id": 14, "value": "tur", "label": {"fr": "Tourmaline", "en": "Tourmaline"}, "group": "cyclosilicates"},
    {"id": 15, "value": "ep", "label": {"fr": "Épidote", "en": "Epidote"}, "group": "sorosilicates"},
    {"id": 16, "value": "ttn", "label": {"fr": "Titanite", "en": "Titanite"}, "group": "sorosilicates"},
    {"id": 17, "value": "cal", "label": {"fr": "Calcite", "en": "Calcite"}, "group": "carbonates"},
    {"id": 18, "value": "dol", "label": {"fr": "Dolomite", "en": "Dolomite"}, "group": "carbonates"},
    {"id": 19, "value": "mag", "label": {"fr": "Magnétite", "en": "Magnetite"}, "group": "oxides"},
    {"id": 20, "value": "ilm", "label": {"fr": "Ilménite", "en": "Ilmenite"}, "group": "oxides"},
    {"id": 21, "value": "hem", "label": {"fr": "Hématite", "en": "Hematite"}, "group": "oxides"},
    {"id": 22, "value": "ap", "label": {"fr": "Apatite", "en": "Apatite"}, "group": "phosphates"},
]

MINERAL_VALUE_TO_ID = {m["value"]: m["id"] for m in MINERALS}

MINERAL_GROUPS = [
    {"value": "tectosilicates", "label": {"fr": "Tectosilicates", "en": "Tectosilicates"}},
    {"value": "phyllosilicates", "label": {"fr": "Phyllosilicates", "en": "Phyllosilicates"}},
    {"value": "inosilicates", "label": {"fr": "Inosilicates", "en": "Inosilicates"}},
    {"value": "nesosilicates", "label": {"fr": "Nésosilicates", "en": "Nesosilicates"}},
    {"value": "cyclosilicates", "label": {"fr": "Cyclosilicates", "en": "Cyclosilicates"}},
    {"value": "sorosilicates", "label": {"fr": "Sorosilicates", "en": "Sorosilicates"}},
    {"value": "carbonates", "label": {"fr": "Carbonates", "en": "Carbonates"}},
    {"value": "oxides", "label": {"fr": "Oxydes", "en": "Oxides"}},
    {"value": "phosphates", "label": {"fr": "Phosphates", "en": "Phosphates"}},
]


def build_categories():
    return [
        {
            "id": m["id"],
            "name": m["value"],
            "name_en": m["label"]["en"],
            "name_fr": m["label"]["fr"],
            "supercategory": m["group"],
        }
        for m in MINERALS
    ]


def compute_bbox_area(rle, height, width):
    """Compute bbox and area from RLE segmentation using pycocotools."""
    try:
        from pycocotools import mask as mask_utils
        rle_obj = {"counts": rle["counts"], "size": rle["size"]}
        if isinstance(rle_obj["counts"], str):
            rle_obj["counts"] = rle_obj["counts"].encode("utf-8")
        decoded = mask_utils.decode(rle_obj)
        area = float(mask_utils.area(rle_obj))
        bbox = list(mask_utils.toBbox(rle_obj))  # [x, y, w, h]
        return bbox, area
    except Exception as e:
        raise RuntimeError(f"pycocotools failed: {e}")


def find_annotation_files(root_dir):
    """Recursively find all -annotations.json files."""
    root = Path(root_dir)
    return sorted(root.rglob("*-annotations.json"))


def resolve_image_path(json_path, json_data):
    """Resolve the image file path from JSON data or fallback to filename convention."""
    parent = json_path.parent
    if "image" in json_data and "file_name" in json_data["image"]:
        candidate = parent / json_data["image"]["file_name"]
        if candidate.exists():
            return candidate
        return candidate
    base = json_path.name.replace("-annotations.json", "")
    return parent / f"{base}.bmp"


def build_dataset(root_dir, output_dir, zip_output=False, progress_callback=None):
    """
    Builds the COCO dataset.
    :param root_dir: Source folder containing annotations and images.
    :param output_dir: Destination folder chosen by the user in the UI.
    :param zip_output: If True, exports as a .zip file. If False, exports as a normal folder.
    :param progress_callback: Function to report UI progress.
    """
    root_dir = Path(root_dir)
    output_dir = Path(output_dir)

    # Generate a unique identifier based on the current timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dataset_basename = f"dataset_{timestamp}"

    log_lines = []
    coco_images = []
    coco_annotations = []
    licenses_seen = {}

    image_seq_id = 0
    annotation_seq_id = 0

    annotation_files = find_annotation_files(root_dir)

    if not annotation_files:
        log_lines.append("ERROR: No annotation files found under the root directory.")

    all_image_files = set(root_dir.rglob("*.bmp"))
    matched_image_files = set()
    images_to_zip = []
    count = len(annotation_files)

    for json_path in annotation_files:
        try:
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                log_lines.append(f"ERROR [file issue] {json_path}: {e}")
                continue

            image_path = resolve_image_path(json_path, data)
            if not image_path.exists():
                log_lines.append(f"ERROR [image not found] Expected image: {image_path} (referenced by {json_path})")
                continue

            matched_image_files.add(image_path.resolve())

            image_seq_id += 1
            new_filename = f"{image_seq_id}_{image_path.name}"

            license_id = None
            if "license" in data:
                lic = data["license"]
                lic_url = lic.get("url", "")
                if lic_url not in licenses_seen:
                    lic_entry = {
                        "id": len(licenses_seen) + 1,
                        "name": lic.get("name", ""),
                        "url": lic_url,
                    }
                    licenses_seen[lic_url] = lic_entry
                license_id = licenses_seen[lic_url]["id"]

            img_info = data.get("image", {})
            coco_image = {
                "id": image_seq_id,
                "file_name": new_filename,
                "width": img_info.get("width"),
                "height": img_info.get("height"),
                "license": license_id,
                "metadata": data.get("metadata", {}),
            }
            coco_images.append(coco_image)
            images_to_zip.append((image_path, new_filename))

            for ann in data.get("annotations", []):
                annotation_seq_id += 1
                raw_mineral_ids = ann.get("mineralIds", [])
                resolved_mineral_ids = [MINERAL_VALUE_TO_ID[m] for m in raw_mineral_ids if m in MINERAL_VALUE_TO_ID]

                if not resolved_mineral_ids:
                    category_id = None
                else:
                    category_id = resolved_mineral_ids[0]

                bbox = []
                area = None
                segmentation = ann.get("segmentation", {})
                if COMPUTE_BBOX and segmentation:
                    try:
                        bbox, area = compute_bbox_area(segmentation, img_info.get("height"), img_info.get("width"))
                    except RuntimeError as e:
                        log_lines.append(f"WARNING [bbox calculation failed] {e}")

                coco_ann = {
                    "id": annotation_seq_id,
                    "image_id": image_seq_id,
                    "category_id": category_id,
                    "segmentation": segmentation,
                    "area": area,
                    "bbox": bbox,
                    "iscrowd": 1,
                    "mineralIds": resolved_mineral_ids,
                    "birefringence": ann.get("birefringence"),
                    "cleavage": ann.get("cleavage"),
                    "crystalSystem": ann.get("crystalSystem"),
                    "extinctionAngle": ann.get("extinctionAngle", ""),
                    "notes": ann.get("notes", ""),
                    "observedColor": ann.get("observedColor", ""),
                    "pleochroism": ann.get("pleochroism"),
                    "relief": ann.get("relief"),
                }
                coco_annotations.append(coco_ann)

        except Exception as e:
            log_lines.append(f"ERROR [unexpected] {json_path}:\n{traceback.format_exc()}")
            continue

        if progress_callback:
            progress_callback("JSON_FILES_COMPUTING", image_seq_id, count, json_path)

    for img_file in all_image_files:
        if img_file.resolve() not in matched_image_files:
            log_lines.append(f"WARNING [orphaned image] No annotation file found for: {img_file}")

    coco = {
        "info": {
            "description": "Petrographic thin section mineral dataset",
            "version": "1.0",
            "year": datetime.now().year,
            "contributor": "",
            "date_created": datetime.now().isoformat(),
        },
        "licenses": list(licenses_seen.values()),
        "categories": build_categories(),
        "images": coco_images,
        "annotations": coco_annotations,
    }

    # ── Exporting Dataset ──────────────────────────────────────────────────
    if zip_output:
        # ZIP EXPORT
        output_path = output_dir / f"{dataset_basename}.zip"
        try:
            with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
                zf.writestr("annotations.json", json.dumps(coco, indent=2, ensure_ascii=False))
                progress = 1
                for image_path, new_filename in images_to_zip:
                    try:
                        zf.write(image_path, arcname=f"images/{new_filename}")
                        if progress_callback:
                            progress_callback("ZIPPING", progress, len(images_to_zip), image_path)
                        progress += 1
                    except OSError as e:
                        log_lines.append(f"ERROR [zip write failed] Could not add image {image_path}: {e}")

                zf.writestr("build.log",
                            "\n".join(log_lines) if log_lines else "Build completed with no warnings or errors.\n")

        except Exception as e:
            fallback_log = output_dir / f"{dataset_basename}_error.log"
            with open(fallback_log, "w", encoding="utf-8") as f:
                f.write(f"FATAL [zip creation failed]: {e}\n{traceback.format_exc()}\n\n{chr(10).join(log_lines)}")
            raise RuntimeError(f"Failed to write ZIP. See {fallback_log}")

    else:
        # UNZIPPED FOLDER EXPORT
        output_path = output_dir / dataset_basename
        try:
            images_dir = output_path / "images"
            images_dir.mkdir(parents=True, exist_ok=True)

            with open(output_path / "annotations.json", "w", encoding="utf-8") as f:
                json.dump(coco, f, indent=2, ensure_ascii=False)

            progress = 1
            for image_path, new_filename in images_to_zip:
                try:
                    dest_path = images_dir / new_filename
                    shutil.copy2(image_path, dest_path)
                    if progress_callback:
                        progress_callback("COPYING", progress, len(images_to_zip), image_path)
                    progress += 1
                except OSError as e:
                    log_lines.append(f"ERROR [file copy failed] Could not copy image {image_path}: {e}")

            with open(output_path / "build.log", "w", encoding="utf-8") as f:
                f.write("\n".join(log_lines) if log_lines else "Build completed with no warnings or errors.\n")

        except Exception as e:
            fallback_log = output_dir / f"{dataset_basename}_error.log"
            with open(fallback_log, "w", encoding="utf-8") as f:
                f.write(f"FATAL [folder export failed]: {e}\n{traceback.format_exc()}\n\n{chr(10).join(log_lines)}")
            raise RuntimeError(f"Failed to write folder. See {fallback_log}")

    print(f"Done. {image_seq_id} images, {annotation_seq_id} annotations.")
    print(f"Output: {output_path}")

    return str(output_path)  # Return the path so the UI can display it