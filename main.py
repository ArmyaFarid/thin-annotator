# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#
# Modifications Copyright (c) 2025 Armya BAKOUAN -- see NOTICE for details.

import logging
import os
import signal
import time
from typing import Any

from app_conf import (
    GALLERY_PATH,
    GALLERY_PREFIX,
    POSTERS_PATH,
    POSTERS_PREFIX,
    UPLOADS_PATH,
    UPLOADS_PREFIX,
    get_resource_path, get_writable_dir,
)
from core.annotator import load_annotator
from data.annotation_options import get_annotation_options
from data.schema import schema
from flask import Flask, make_response, Request, Response, send_from_directory, abort, send_file, jsonify, request
from flask_cors import CORS
from strawberry.flask.views import GraphQLView

from inference.predictor_images import InferenceImageAPI

import webbrowser

from extensions import db
from models import FOVAsset
from preprocessing.pngconverter import to_png_bytes, LossyConversion, cached_png_path
from routes.api.annotation import annotation_blueprint
from routes.api.batch import batch_blueprint
from routes.api.task import task_blueprint
from system.disk_caching.host_caching import CACHE_DIR
from system.disk_caching.sweeper import start_sweeper, sweep


def open_browser():
    # Matches the port in your app.run()
    webbrowser.open_new("http://127.0.0.1:7263")



logger = logging.getLogger(__name__)

app = Flask(__name__,static_folder=get_resource_path("frontend_payload"))


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + str(get_writable_dir() / 'thinAnnotator.db')
db.init_app(app)

cors = CORS(app, supports_credentials=True)
inference_api = None
inference_image_api = None

app.before_request(load_annotator)
app.register_blueprint(task_blueprint)
app.register_blueprint(annotation_blueprint)
app.register_blueprint(batch_blueprint)

@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def serve_static(path):
    # Check if the requested file exists in the 'dist' folder
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    # Otherwise, fall back to index.html for React Router
    return send_from_directory(app.static_folder, "index.html")

@app.route("/healthy")
def healthy() -> Response:
    return make_response("OK", 200)

@app.route("/shutdown", methods=["GET"])
def shutdown():
    logger.info("Shutdown requested from UI...")
    # Give the response a moment to reach the browser before killing the engine
    try:
        # This is the cleanest way to kill a PyInstaller/multiprocessing app
        os.kill(os.getpid(), signal.SIGINT)
    except:
        os._exit(0)
    return make_response("Server shutting down...", 200)

@app.route(f"/{GALLERY_PREFIX}/<path:path>", methods=["GET"])
def send_gallery_video(path: str) -> Response:
    try:
        return send_from_directory(
            GALLERY_PATH,
            path,
        )
    except:
        raise ValueError("resource not found")


def convert_and_send_image_asset(asset_path):
    try:
        t = time.perf_counter()
        buf = to_png_bytes(asset_path)
        print((time.perf_counter() - t) * 1000, "ms",flush=True)
    except LossyConversion:
        abort(415)
    return send_file(buf, mimetype="image/png", download_name="asset.png")

@app.route("/image_non_cached/<image_id>", methods=["GET"])
def serve_fov_image_(image_id: str):
    asset = FOVAsset.query.get(image_id)

    if not asset:
        return abort(404, description="Image ID not found")

    if not os.path.exists(asset.image_path):
        return abort(404, description="Physical image file missing on server")

    try:
        return convert_and_send_image_asset(asset.image_path)
    except Exception as e:
        return abort(500, description=f"Error accessing file: {str(e)}")


@app.route("/image/<image_id>", methods=["GET"])
def serve_fov_image(image_id: str):
    asset = db.session.get(FOVAsset, image_id)
    if not asset:
        abort(404, description="Image ID not found")

    try:
        st = os.stat(asset.image_path)
    except OSError:
        abort(404, description="Physical image file missing on server")

    tag = f"{image_id}-{st.st_mtime_ns:x}-{st.st_size:x}"

    if request.if_none_match.contains(tag):
        resp = make_response("", 304)
        resp.set_etag(tag.strip('"'))
        resp.cache_control.private = True
        resp.cache_control.max_age = 1800
        return resp

    try:
        png = cached_png_path(asset.image_path, st.st_mtime_ns, st.st_size)
    except LossyConversion:
        abort(415)
    except Exception as e:
        abort(500, description=f"Error accessing file: {str(e)}")

    resp = send_file(
        png,
        mimetype="image/png",
        download_name="asset.png",
        last_modified=st.st_mtime,
        etag=tag,
        conditional=True,
    )
    resp.cache_control.private = True
    resp.cache_control.max_age = 1800
    return resp

@app.route(f"/{POSTERS_PREFIX}/<path:path>", methods=["GET"])
def send_poster_image(path: str) -> Response:
    try:
        return send_from_directory(
            POSTERS_PATH,
            path,
        )
    except:
        raise ValueError("resource not found")


@app.route(f"/{UPLOADS_PREFIX}/<path:path>", methods=["GET"])
def send_uploaded_video(path: str):
    try:
        return send_from_directory(
            UPLOADS_PATH,
            path,
        )
    except:
        raise ValueError("resource not found")

@app.route("/api/annotation-options", methods=["GET"])
def annotation_options():
  return jsonify(get_annotation_options())

class MyGraphQLView(GraphQLView):
    def get_context(self, request: Request, response: Response) -> Any:
        return {
            "inference_image_api": inference_image_api
            }


# Add GraphQL route to Flask app.
app.add_url_rule(
    "/graphql",
    view_func=MyGraphQLView.as_view(
        "graphql_view",
        schema=schema,
        # Disable GET queries
        # https://strawberry.rocks/docs/operations/deployment
        # https://strawberry.rocks/docs/integrations/flask
        allow_queries_via_get=False,
        # Strawberry recently changed multipart request handling, which now
        # requires enabling support explicitly for views.
        # https://github.com/strawberry-graphql/strawberry/issues/3655
        multipart_uploads_enabled=True,
    ),
)


def start_backend_logic(debug: bool = False , use_reloader: bool = False):
    # Ensure environment variables are set inside the new process
    os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
    os.environ['OMP_NUM_THREADS'] = '1'
    """Function to initialize data and APIs inside the child process."""
    global inference_api, inference_image_api

    # images = preload_data_img()
    # set_images(images)

    print("Initializing SAM 2 Models...")
    inference_image_api = InferenceImageAPI()

    with app.app_context():
        db.create_all()
        # init_thin_section_fov_images()

    # Run sweeper
    os.makedirs(CACHE_DIR, exist_ok=True)
    # sweep()
    start_sweeper()

    # Run the app (this will block the process)
    if debug:
        app.run(host="127.0.0.1", port=7263, debug=True, use_reloader=use_reloader)
    else:
        from waitress import serve
        serve(app, host="127.0.0.1", port=7263, threads=8)