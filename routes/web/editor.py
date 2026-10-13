import os

from flask import Blueprint, current_app, send_from_directory

editor_blueprint = Blueprint("editor", __name__)


@editor_blueprint.route("/")
def serve_index():
    return send_from_directory(current_app.static_folder, "index.html")


@editor_blueprint.route("/<path:path>")
def serve_static(path):
    if os.path.exists(os.path.join(current_app.static_folder, path)):
        return send_from_directory(current_app.static_folder, path)
    return send_from_directory(current_app.static_folder, "index.html")
