# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

import logging
import os
from pathlib import Path
import signal
import sys
from typing import Any, Generator

from flask_sqlalchemy import SQLAlchemy

from app_conf import (
    GALLERY_PATH,
    GALLERY_PREFIX,
    POSTERS_PATH,
    POSTERS_PREFIX,
    UPLOADS_PATH,
    UPLOADS_PREFIX,
    get_resource_path,
)
from data.schema import schema
from data.store import set_images
from flask import Flask, make_response, Request, request, Response, send_from_directory, abort, send_file
from flask_cors import CORS
from inference.data_types import PropagateDataResponse, PropagateInVideoRequest
from inference.multipart import MultipartResponseBuilder
from strawberry.flask.views import GraphQLView

from data.loader_image import preload_data_img, init_thin_section_fov_images
from inference.predictor_images import InferenceImageAPI

import webbrowser
from threading import Timer

from extensions import db
from models import FOVAsset


def open_browser():
    # Matches the port in your app.run()
    webbrowser.open_new("http://127.0.0.1:7263")



logger = logging.getLogger(__name__)

app = Flask(__name__,static_folder=get_resource_path("frontend_payload"),
            static_url_path="/")


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'test.db')
db.init_app(app)

cors = CORS(app, supports_credentials=True)
inference_api = None
inference_image_api = None

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


@app.route("/image/<image_id>", methods=["GET"])
def serve_fov_image(image_id: str):
    # 1. Look up the record by its UUID
    # We use .get() because 'id' is your primary key
    asset = FOVAsset.query.get(image_id)

    # 2. Check if the ID exists in the database
    if not asset:
        return abort(404, description="Image ID not found")

    # 3. Verify the physical file actually exists at that path
    if not os.path.exists(asset.image_path):
        return abort(404, description="Physical image file missing on server")

    # 4. Serve the file directly
    try:
        return send_file(asset.image_path)
    except Exception as e:
        return abort(500, description=f"Error accessing file: {str(e)}")

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


def start_backend_logic():
    # Ensure environment variables are set inside the new process
    os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
    os.environ['OMP_NUM_THREADS'] = '1'
    """Function to initialize data and APIs inside the child process."""
    global inference_api, inference_image_api

    images = preload_data_img()
    set_images(images)

    print("Initializing SAM 2 Models...")
    inference_image_api = InferenceImageAPI()

    with app.app_context():
        db.create_all()
        init_thin_section_fov_images()

    # Run the app (this will block the process)
    app.run(host="0.0.0.0", port=7263, debug=False, use_reloader=False)