from flask import g, request, abort
from werkzeug.local import LocalProxy

from schema.annotator import parse_annotator_header, MalformedAnnotatorHeader

EXEMPT_ENDPOINTS = {"static", "health.livez", "health.readyz"}


def load_annotator():
    if request.endpoint in EXEMPT_ENDPOINTS:
        g.annotator = None
        return
    try:
        g.annotator = parse_annotator_header(request.headers.get("X-Annotator"))
    except MalformedAnnotatorHeader as exc:
        abort(400, f"Malformed X-Annotator header: {exc}")


current_annotator = LocalProxy(lambda: getattr(g, "annotator", None))