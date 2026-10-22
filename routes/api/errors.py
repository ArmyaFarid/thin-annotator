from flask import Blueprint, jsonify
from marshmallow import ValidationError


def error_response(message, status, details=None):
    body = {"success": False, "error": message}
    if details is not None:
        body["details"] = details
    return jsonify(body), status


def register_validation_handler(blueprint: Blueprint):
    @blueprint.errorhandler(ValidationError)
    def handle_validation_error(err: ValidationError):
        return error_response("Invalid request", 400, err.messages)
