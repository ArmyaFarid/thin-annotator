# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

import hashlib
import os
import shutil
import tempfile
from pathlib import Path
from typing import Iterable, List, Optional, Tuple, Union
import av
import strawberry
from app_conf import (
    DATA_PATH,
    DEFAULT_VIDEO_PATH,
    MAX_UPLOAD_VIDEO_DURATION,
    UPLOADS_PATH,
    UPLOADS_PREFIX,
)
from strawberry.file_uploads import Upload

from data.image_schema import ImageMutation, ImageQuery, ThinSectionImagePairsQuery


@strawberry.type
class Query(ImageQuery,ThinSectionImagePairsQuery):
    """
    Inherits 'videos' from VideoQuery and 'images' from ImageQuery.
    """
    pass

@strawberry.type
class Mutation(ImageMutation):
    pass


schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
)
