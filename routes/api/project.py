import json
import os
from datetime import datetime
from pathlib import Path

from flask import Blueprint, jsonify, request

from data.annotation_options import get_annotation_options
from data.project_manager import get_project_data
from models import FOVAsset

project_blueprint = Blueprint('project', __name__)


@project_blueprint.route("/api/project/save", methods=["POST"])
def save_project_annotations():
    body = request.get_json()
    if not body:
        return jsonify({"success": False, "error": "Invalid JSON"}), 400

    pairs_code = body.get("pairsCode")
    sample_id = body.get("sampleId")
    annotation_data = body.get("data")



    if not all([pairs_code, sample_id, annotation_data]):
        return jsonify({"success": False, "error": "Missing required fields"}), 400

    try:
        asset = FOVAsset.query.filter_by(
            thin_section_id=pairs_code,
            fov_id=sample_id
        ).first()

        if not asset:
            return jsonify({"success": False, "error": "FOV folder not found in database"}), 404

        fov_folder = Path(asset.image_path).parent

        file_path = fov_folder / "project.json"

        payload = {
            "data": annotation_data,  # your list stays untouched
            "_meta": {
                "version": "1.0.0",
                "saved_at": datetime.utcnow().isoformat(),
                "pairs_code": pairs_code,
                "sample_id": sample_id,
            }
        }

        # Write to a temp file first, then rename (atomic on most OS)
        tmp_path = file_path.with_suffix(".tmp")
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(payload, f, indent=4)
        os.replace(tmp_path, file_path)  # atomic rename
        print(f"Annotations saved successfully for {pairs_code}/{sample_id} at {file_path}")

        return jsonify({"success": True})

    except Exception as e:
        print(f"Error saving annotations: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@project_blueprint.route("/api/project/load", methods=["GET"])
def load_project_annotations_endpoint():
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

        annotations = get_project_data(fov_folder)

        return jsonify({"annotations": annotations})

    except Exception as e:
        print(f"Error loading annotations: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
