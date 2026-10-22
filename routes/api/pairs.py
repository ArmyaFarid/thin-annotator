from flask import Blueprint, jsonify, request

from core.pairs import get_pairs
from routes.api.errors import register_validation_handler
from schema.pairs import pairs_query_schema, pairs_schema

pairs_blueprint = Blueprint('pairs', __name__)
register_validation_handler(pairs_blueprint)


@pairs_blueprint.route("/api/pairs", methods=["GET"])
def get_pairs_route():
    query = pairs_query_schema.load(request.args)
    pairs = get_pairs(query["pairs_code"], query["sample_id"])
    return jsonify(pairs_schema.dump(pairs))
