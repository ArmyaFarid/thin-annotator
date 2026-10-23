from flask import Blueprint, current_app, jsonify, request

from extensions import db
from inference.encoding import encode_label_map
from models import FOVAsset
from routes.api.errors import error_response, register_validation_handler
from schema.inference import (
    add_points_request_schema,
    mask_list_schema,
    slic_label_map_schema,
    slic_request_schema,
)

inference_blueprint = Blueprint('inference', __name__)
register_validation_handler(inference_blueprint)


def _asset_missing(image_id):
    if db.session.get(FOVAsset, image_id) is None:
        return error_response(f"Asset with ID {image_id} not found.", 404)
    return None


@inference_blueprint.route("/api/inference/points", methods=["POST"])
def add_points():
    req = add_points_request_schema.load(request.get_json(silent=True))
    missing = _asset_missing(req.image_id)
    if missing:
        return missing

    try:
        response = current_app.extensions["inference_image_api"].add_points_image(req)
    except Exception as e:
        print(f"Error computing SAM mask: {str(e)}")
        return error_response(str(e), 500)

    return jsonify(mask_list_schema.dump(response))


@inference_blueprint.route("/api/inference/slic-label-map", methods=["POST"])
def slic_label_map():
    req = slic_request_schema.load(request.get_json(silent=True))
    missing = _asset_missing(req.image_id)
    if missing:
        return missing

    try:
        response = current_app.extensions["inference_image_api"].compute_slic_image_label_map(req)
    except Exception as e:
        print(f"Error computing SLIC label map: {str(e)}")
        return error_response(str(e), 500)

    return jsonify(slic_label_map_schema.dump(encode_label_map(response.data)))
