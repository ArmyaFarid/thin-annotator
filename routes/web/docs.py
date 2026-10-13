import os

from flask import Blueprint, abort, redirect, request, send_from_directory
from werkzeug.security import safe_join

from app_conf import get_flask_stattic_resource_path

DOCS_PATH = get_flask_stattic_resource_path("docs")

docs_blueprint = Blueprint("docs", __name__, url_prefix="/docs")


@docs_blueprint.route("/", defaults={"path": ""})
@docs_blueprint.route("/<path:path>")
def serve_docs(path):
    full_path = safe_join(str(DOCS_PATH), path)
    if full_path is None:
        abort(404)
    if not os.path.isdir(full_path):
        return send_from_directory(DOCS_PATH, path)
    if not request.path.endswith("/"):
        return redirect(request.path + "/")
    if os.path.isfile(os.path.join(full_path, "index.html")):
        return send_from_directory(DOCS_PATH, os.path.join(path, "index.html"))
    if path == "":
        return redirect("/docs/user-guide/")
    abort(404)
