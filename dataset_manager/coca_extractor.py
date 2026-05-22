import os
import json
import zipfile
import traceback
from pathlib import Path

# ─── CONFIG ───────────────────────────────────────────────────────────────────
COMPUTE_BBOX = False  # Set True to compute bbox/area via pycocotools
# ──────────────────────────────────────────────────────────────────────────────

MINERALS = [
    {"id": 1,  "value": "qtz",  "label": {"fr": "Quartz",      "en": "Quartz"},      "group": "tectosilicates"},
    {"id": 2,  "value": "kfs",  "label": {"fr": "Feldspath K", "en": "K-feldspar"},  "group": "tectosilicates"},
    {"id": 3,  "value": "plag", "label": {"fr": "Plagioclase", "en": "Plagioclase"}, "group": "tectosilicates"},
    {"id": 4,  "value": "ms",   "label": {"fr": "Muscovite",   "en": "Muscovite"},   "group": "phyllosilicates"},
    {"id": 5,  "value": "bt",   "label": {"fr": "Biotite",     "en": "Biotite"},     "group": "phyllosilicates"},
    {"id": 6,  "value": "chl",  "label": {"fr": "Chlorite",    "en": "Chlorite"},    "group": "phyllosilicates"},
    {"id": 7,  "value": "srp",  "label": {"fr": "Serpentine",  "en": "Serpentine"},  "group": "phyllosilicates"},
    {"id": 8,  "value": "hbl",  "label": {"fr": "Hornblende",  "en": "Hornblende"},  "group": "inosilicates"},
    {"id": 9,  "value": "aug",  "label": {"fr": "Augite",      "en": "Augite"},      "group": "inosilicates"},
    {"id": 10, "value": "hyp",  "label": {"fr": "Hypersthène", "en": "Hypersthene"}, "group": "inosilicates"},
    {"id": 11, "value": "ol",   "label": {"fr": "Olivine",     "en": "Olivine"},     "group": "nesosilicates"},
    {"id": 12, "value": "grt",  "label": {"fr": "Grenat",      "en": "Garnet"},      "group": "nesosilicates"},
    {"id": 13, "value": "zrn",  "label": {"fr": "Zircon",      "en": "Zircon"},      "group": "nesosilicates"},
    {"id": 14, "value": "tur",  "label": {"fr": "Tourmaline",  "en": "Tourmaline"},  "group": "cyclosilicates"},
    {"id": 15, "value": "ep",   "label": {"fr": "Épidote",     "en": "Epidote"},     "group": "sorosilicates"},
    {"id": 16, "value": "ttn",  "label": {"fr": "Titanite",    "en": "Titanite"},    "group": "sorosilicates"},
    {"id": 17, "value": "cal",  "label": {"fr": "Calcite",     "en": "Calcite"},     "group": "carbonates"},
    {"id": 18, "value": "dol",  "label": {"fr": "Dolomite",    "en": "Dolomite"},    "group": "carbonates"},
    {"id": 19, "value": "mag",  "label": {"fr": "Magnétite",   "en": "Magnetite"},   "group": "oxides"},
    {"id": 20, "value": "ilm",  "label": {"fr": "Ilménite",    "en": "Ilmenite"},    "group": "oxides"},
    {"id": 21, "value": "hem",  "label": {"fr": "Hématite",    "en": "Hematite"},    "group": "oxides"},
    {"id": 22, "value": "ap",   "label": {"fr": "Apatite",     "en": "Apatite"},     "group": "phosphates"},
]

MINERAL_VALUE_TO_ID = {m["value"]: m["id"] for m in MINERALS}

MINERAL_GROUPS = [
    {"value": "tectosilicates",  "label": {"fr": "Tectosilicates", "en": "Tectosilicates"}},
    {"value": "phyllosilicates", "label": {"fr": "Phyllosilicates","en": "Phyllosilicates"}},
    {"value": "inosilicates",    "label": {"fr": "Inosilicates",   "en": "Inosilicates"}},
    {"value": "nesosilicates",   "label": {"fr": "Nésosilicates",  "en": "Nesosilicates"}},
    {"value": "cyclosilicates",  "label": {"fr": "Cyclosilicates", "en": "Cyclosilicates"}},
    {"value": "sorosilicates",   "label": {"fr": "Sorosilicates",  "en": "Sorosilicates"}},
    {"value": "carbonates",      "label": {"fr": "Carbonates",     "en": "Carbonates"}},
    {"value": "oxides",          "label": {"fr": "Oxydes",         "en": "Oxides"}},
    {"value": "phosphates",      "label": {"fr": "Phosphates",     "en": "Phosphates"}},
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
        # pycocotools expects counts as bytes if string
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

    # Primary: use file_name from JSON
    if "image" in json_data and "file_name" in json_data["image"]:
        candidate = parent / json_data["image"]["file_name"]
        if candidate.exists():
            return candidate
        # file_name present but file missing — fallback and log later
        return candidate  # return anyway so caller can detect missing

    # Fallback: strip -annotations.json -> .bmp
    base = json_path.name.replace("-annotations.json", "")
    return parent / f"{base}.bmp"


def build_dataset(root_dir, output_zip_path):
    root_dir = Path(root_dir)
    output_zip_path = Path(output_zip_path)

    log_lines = []
    coco_images = []
    coco_annotations = []
    licenses_seen = {}  # url -> license dict

    image_seq_id = 0
    annotation_seq_id = 0

    annotation_files = find_annotation_files(root_dir)

    if not annotation_files:
        log_lines.append("ERROR: No annotation files found under the root directory.")

    # Track images we've seen to detect orphaned images later
    all_image_files = set(root_dir.rglob("*.bmp"))
    matched_image_files = set()

    # Will collect (seq_id, original_image_path, new_filename) for zip writing
    images_to_zip = []

    for json_path in annotation_files:
        try:
            # ── Parse JSON ──────────────────────────────────────────────────
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except json.JSONDecodeError as e:
                log_lines.append(f"ERROR [bad JSON] {json_path}: {e}")
                continue
            except OSError as e:
                log_lines.append(f"ERROR [file not found/unreadable] {json_path}: {e}")
                continue

            # ── Resolve image path ───────────────────────────────────────────
            image_path = resolve_image_path(json_path, data)
            if not image_path.exists():
                log_lines.append(f"ERROR [image not found] Expected image: {image_path} (referenced by {json_path})")
                continue

            matched_image_files.add(image_path.resolve())

            # ── Sequential image ID & new filename ──────────────────────────
            image_seq_id += 1
            new_filename = f"{image_seq_id}_{image_path.name}"

            # ── License deduplication ────────────────────────────────────────
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

            # ── Image entry ──────────────────────────────────────────────────
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

            # ── Annotations ─────────────────────────────────────────────────
            for ann in data.get("annotations", []):
                annotation_seq_id += 1

                # Resolve mineralIds strings -> ints
                raw_mineral_ids = ann.get("mineralIds", [])
                resolved_mineral_ids = []
                for mid in raw_mineral_ids:
                    if mid in MINERAL_VALUE_TO_ID:
                        resolved_mineral_ids.append(MINERAL_VALUE_TO_ID[mid])
                    else:
                        log_lines.append(
                            f"WARNING [unknown mineral] '{mid}' in annotation {ann.get('id')} "
                            f"of {json_path} — skipped from mineralIds"
                        )

                # category_id = first resolved mineralId
                if not resolved_mineral_ids:
                    log_lines.append(
                        f"WARNING [no valid mineralId] annotation {ann.get('id')} in {json_path} "
                        f"— category_id set to null"
                    )
                    category_id = None
                else:
                    category_id = resolved_mineral_ids[0]

                # bbox & area
                bbox = []
                area = None
                segmentation = ann.get("segmentation", {})
                if COMPUTE_BBOX and segmentation:
                    try:
                        bbox, area = compute_bbox_area(
                            segmentation,
                            img_info.get("height"),
                            img_info.get("width"),
                        )
                    except RuntimeError as e:
                        log_lines.append(
                            f"WARNING [bbox computation failed] annotation {ann.get('id')} "
                            f"in {json_path}: {e}"
                        )

                coco_ann = {
                    "id": annotation_seq_id,
                    "image_id": image_seq_id,
                    "category_id": category_id,
                    "segmentation": segmentation,
                    "area": area,
                    "bbox": bbox,
                    "iscrowd": 1,
                    # custom fields
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
            log_lines.append(
                f"ERROR [unexpected] {json_path}:\n{traceback.format_exc()}"
            )
            continue

    # ── Orphaned images (images with no matching annotation file) ────────────
    for img_file in all_image_files:
        if img_file.resolve() not in matched_image_files:
            log_lines.append(f"WARNING [orphaned image] No annotation file found for: {img_file}")

    # ── Build final COCO dict ────────────────────────────────────────────────
    coco = {
        "info": {
            "description": "Petrographic thin section mineral dataset",
            "version": "1.0",
            "year": 2024,
            "contributor": "",
            "date_created": "",
        },
        "licenses": list(licenses_seen.values()),
        "categories": build_categories(),
        "images": coco_images,
        "annotations": coco_annotations,
    }

    # ── Write zip ────────────────────────────────────────────────────────────
    try:
        with zipfile.ZipFile(output_zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            # annotations.json
            zf.writestr(
                "annotations.json",
                json.dumps(coco, indent=2, ensure_ascii=False)
            )

            # images
            for image_path, new_filename in images_to_zip:
                try:
                    zf.write(image_path, arcname=f"images/{new_filename}")
                except OSError as e:
                    log_lines.append(f"ERROR [zip write failed] Could not add image {image_path}: {e}")

            # build.log
            if log_lines:
                zf.writestr("build.log", "\n".join(log_lines))
            else:
                zf.writestr("build.log", "Build completed with no warnings or errors.\n")

    except Exception as e:
        # If zip itself fails, write log beside the output path
        fallback_log = output_zip_path.with_suffix(".log")
        with open(fallback_log, "w") as f:
            f.write(f"FATAL [zip creation failed]: {e}\n")
            f.write(traceback.format_exc())
            f.write("\n\nPrevious log:\n" + "\n".join(log_lines))
        print(f"FATAL: Could not write zip. See {fallback_log}")
        return

    print(f"Done. {image_seq_id} images, {annotation_seq_id} annotations.")
    print(f"Output: {output_zip_path}")
    if log_lines:
        print(f"Warnings/errors logged inside zip as build.log ({len(log_lines)} entries).")