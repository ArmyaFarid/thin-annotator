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
from data.transcoder import get_video_metadata, transcode, VideoMetadata
from strawberry.file_uploads import Upload

from data.image_schema import ImageMutation, ImageQuery
from data.video_schema import VideoMutation, VideoQuery


@strawberry.type
class Query(VideoQuery, ImageQuery):
    """
    Inherits 'videos' from VideoQuery and 'images' from ImageQuery.
    """
    pass

@strawberry.type
class Mutation(VideoMutation, ImageMutation):
    pass



def get_file_hash(video_path_or_file) -> str:
    if isinstance(video_path_or_file, str):
        with open(video_path_or_file, "rb") as in_f:
            result = hashlib.sha256(in_f.read()).hexdigest()
    else:
        video_path_or_file.seek(0)
        result = hashlib.sha256(video_path_or_file.read()).hexdigest()
    return result


def _get_start_sec_duration_sec(
    start_time_sec: Union[float, None],
    duration_time_sec: Union[float, None],
    max_time: float,
) -> Tuple[float, float]:
    default_seek_t = int(os.environ.get("VIDEO_ENCODE_SEEK_TIME", "0"))
    if start_time_sec is None:
        start_time_sec = default_seek_t

    if duration_time_sec is not None:
        duration_time_sec = min(duration_time_sec, max_time)
    else:
        duration_time_sec = max_time
    return start_time_sec, duration_time_sec


def process_video(
    file: Upload,
    max_time: float,
    start_time_sec: Optional[float] = None,
    duration_time_sec: Optional[float] = None,
) -> Tuple[Optional[str], str, str, VideoMetadata]:
    """
    Process file upload including video trimming and content moderation checks.

    Returns the filepath, s3_file_key, hash & video metaedata as a tuple.
    """
    with tempfile.TemporaryDirectory() as tempdir:
        in_path = f"{tempdir}/in.mp4"
        out_path = f"{tempdir}/out.mp4"
        with open(in_path, "wb") as in_f:
            in_f.write(file.read())

        try:
            video_metadata = get_video_metadata(in_path)
        except av.InvalidDataError:
            raise Exception("not valid video file")

        if video_metadata.num_video_streams == 0:
            raise Exception("video container does not contain a video stream")
        if video_metadata.width is None or video_metadata.height is None:
            raise Exception("video container does not contain width or height metadata")

        if video_metadata.duration_sec in (None, 0):
            raise Exception("video container does time duration metadata")

        start_time_sec, duration_time_sec = _get_start_sec_duration_sec(
            max_time=max_time,
            start_time_sec=start_time_sec,
            duration_time_sec=duration_time_sec,
        )

        # Transcode video to make sure videos returned to the app are all in
        # the same format, duration, resolution, fps.
        transcode(
            in_path,
            out_path,
            video_metadata,
            seek_t=start_time_sec,
            duration_time_sec=duration_time_sec,
        )

        os.remove(in_path)  # don't need original video now

        out_video_metadata = get_video_metadata(out_path)
        if out_video_metadata.num_video_frames == 0:
            raise Exception(
                "transcode produced empty video; check seek time or your input video"
            )

        filepath = None
        file_key = None
        with open(out_path, "rb") as file_data:
            file_hash = get_file_hash(file_data)
            file_data.seek(0)

            file_key = UPLOADS_PREFIX + "/" + f"{file_hash}.mp4"
            filepath = os.path.join(UPLOADS_PATH, f"{file_hash}.mp4")

        assert filepath is not None and file_key is not None
        shutil.move(out_path, filepath)

        return filepath, file_key, out_video_metadata


schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
)
