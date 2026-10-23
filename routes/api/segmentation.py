from flask import Blueprint, current_app, jsonify, request

from extensions import db
from models import FOVAsset
from routes.api.errors import error_response, register_validation_handler
from segmentation.schema import dump_output

segmentation_blueprint = Blueprint('segmentation', __name__)
register_validation_handler(segmentation_blueprint)


@segmentation_blueprint.route("/api/segmentation/<method>", methods=["POST"])
def segment(method):
    segmenter = current_app.extensions["segmenters"].get(method)
    if segmenter is None:
        return error_response(f"Unknown segmentation method {method}.", 404)

    req = segmenter.request_schema.load(request.get_json(silent=True))
    asset = db.session.get(FOVAsset, req.image_id)
    if asset is None:
        return error_response(f"Asset with ID {req.image_id} not found.", 404)

    try:
        output = segmenter.segment(asset, req)
    except Exception as e:
        print(f"Error running {method} segmentation: {str(e)}")
        return error_response(str(e), 500)

    return jsonify(dump_output(output))
