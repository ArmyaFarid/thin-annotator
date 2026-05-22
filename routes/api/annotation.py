import base64
import json
import os
from pathlib import Path

from flask import Blueprint, jsonify, request

from data.annotation_options import get_annotation_options
from models import FOVAsset

annotation_blueprint = Blueprint('annotation', __name__)


@annotation_blueprint.route("/api/annotations/save", methods=["POST"])
def save_annotations():
    body = request.get_json()
    if not body:
        return jsonify({"success": False, "error": "Invalid JSON"}), 400

    pairs_code = body.get("pairsCode")
    sample_id = body.get("sampleId")
    image_id = body.get("imageId")
    annotation_data = body.get("data")

    print(image_id)

    if not all([pairs_code, sample_id, annotation_data]):
        return jsonify({"success": False, "error": "Missing required fields"}), 400

    try:
        decoded = base64.b64decode(image_id).decode("utf-8")

        print(decoded)
        # Image:16fd1c9c-ba45-41f8-9e2f-18d70c4d6c73

        entity_type, real_id = decoded.split(":", 1)

        print(entity_type)  # Image
        print(real_id)

        asset = FOVAsset.query.filter_by(
            id=real_id,
            thin_section_id=pairs_code,
            fov_id=sample_id
        ).first()

        if not asset:
            return jsonify({"success": False, "error": "FOV folder not found in database"}), 404


        img_base_path, ext = os.path.splitext(asset.image_path)
        file_path = f"{img_base_path}-annotations.json"

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(annotation_data, f, indent=4)

        print(f"Annotations saved successfully for {pairs_code}/{sample_id} at {file_path}")

        return jsonify({"success": True})

    except Exception as e:
        print(f"Error saving annotations: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@annotation_blueprint.route("/api/annotations/load", methods=["GET"])
def load_annotations_endpoint():
    pairs_code = request.args.get("pairsCode")
    sample_id = request.args.get("sampleId")

    if not pairs_code or not sample_id:
        return jsonify({"success": False, "error": "Missing pairsCode or sampleId"}), 400

    try:
        asset = FOVAsset.query.filter_by(
            thin_section_id=pairs_code,
            fov_id=sample_id
        ).first()

        if not asset:
            return jsonify({"success": False, "error": "FOV folder not found in database"}), 404

        fov_folder = Path(asset.image_path).parent
        annotation_file = fov_folder / "annotations.json"

        annotations = None
        if annotation_file.exists():
            with open(annotation_file, 'r', encoding='utf-8') as f:
                annotations = json.load(f)

        return jsonify({"annotations": annotations})

    except Exception as e:
        print(f"Error loading annotations: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
