# data/schema_video.py
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
from data.data_types import (
    AddPointsInput,
    CancelPropagateInVideo,
    CancelPropagateInVideoInput,
    ClearPointsInFrameInput,
    ClearPointsInVideo,
    ClearPointsInVideoInput,
    CloseSession,
    CloseSessionInput,
    RemoveObjectInput,
    RLEMask,
    RLEMaskForObject,
    RLEMaskListOnFrame,
    StartSession,
    StartSessionInput,
    Video,
)
from data.loader import get_video
from data.store import get_videos
from data.transcoder import get_video_metadata, transcode, VideoMetadata
from inference.data_types import (
    AddPointsRequest,
    CancelPropagateInVideoRequest,
    CancelPropagateInVideoRequest,
    ClearPointsInFrameRequest,
    ClearPointsInVideoRequest,
    CloseSessionRequest,
    RemoveObjectRequest,
    StartSessionRequest,
)
from inference.predictor import InferenceAPI
from strawberry import relay
from strawberry.file_uploads import Upload



@strawberry.type
class VideoQuery:

    @strawberry.field
    def default_video(self) -> Video:
        """
        Return the default video.

        The default video can be set with the DEFAULT_VIDEO_PATH environment
        variable. It will return the video that matches this path. If no video
        is found, it will return the first video.
        """
        all_videos = get_videos()

        # Find the video that matches the default path and return that as
        # default video.
        for _, v in all_videos.items():
            if v.path == DEFAULT_VIDEO_PATH:
                return v

        # Fallback is returning the first video
        return next(iter(all_videos.values()))

    @relay.connection(relay.ListConnection[Video])
    def videos(
        self,
    ) -> Iterable[Video]:
        """
        Return all available videos.
        """
        all_videos = get_videos()
        return all_videos.values()

@strawberry.type
class VideoMutation:
    @strawberry.mutation
    def upload_video(
        self,
        file: Upload,
        start_time_sec: Optional[float] = None,
        duration_time_sec: Optional[float] = None,
    ) -> Video:
        # NOTE: You will need to move 'process_video' to a shared utils.py 
        # or import it from the main schema if circular imports allow.
        # For now, assuming it's available or you move it here.
        from .schema import process_video 
        
        max_time = MAX_UPLOAD_VIDEO_DURATION
        filepath, file_key, vm = process_video(
            file,
            max_time=max_time,
            start_time_sec=start_time_sec,
            duration_time_sec=duration_time_sec,
        )

        video = get_video(
            filepath,
            UPLOADS_PATH,
            file_key=file_key,
            width=vm.width,
            height=vm.height,
            generate_poster=False,
        )
        return video

    @strawberry.mutation
    def start_session(self, input: StartSessionInput, info: strawberry.Info) -> StartSession:
        api = info.context["inference_api"]
        request = StartSessionRequest(
            type="start_session",
            path=f"{DATA_PATH}/{input.path}",
        )
        response = api.start_session(request=request)
        return StartSession(session_id=response.session_id)

    @strawberry.mutation
    def close_session(self, input: CloseSessionInput, info: strawberry.Info) -> CloseSession:
        api = info.context["inference_api"]
        request = CloseSessionRequest(type="close_session", session_id=input.session_id)
        response = api.close_session(request)
        return CloseSession(success=response.success)

    @strawberry.mutation
    def add_points(self, input: AddPointsInput, info: strawberry.Info) -> RLEMaskListOnFrame:
        api = info.context["inference_api"]
        # ... (Original Video Logic) ...
        # For brevity, use the logic you already had:
        from inference.data_types import AddPointsRequest
        request = AddPointsRequest(
            type="add_points",
            session_id=input.session_id,
            frame_index=input.frame_index,
            object_id=input.object_id,
            points=input.points,
            labels=input.labels,
            clear_old_points=input.clear_old_points,
        )
        response = api.add_points(request)
        
        # Helper to convert response to RLEMaskListOnFrame
        from .data_types import RLEMaskForObject, RLEMask
        return RLEMaskListOnFrame(
            frame_index=response.frame_index,
            rle_mask_list=[
                RLEMaskForObject(
                    object_id=r.object_id,
                    rle_mask=RLEMask(counts=r.mask.counts, size=r.mask.size, order="F"),
                )
                for r in response.results
            ],
        )

    # ... Include remove_object, clear_points, etc. here ...
    @strawberry.mutation
    def remove_object(
        self, input: RemoveObjectInput, info: strawberry.Info
    ) -> List[RLEMaskListOnFrame]:
        inference_api: InferenceAPI = info.context["inference_api"]

        request = RemoveObjectRequest(
            type="remove_object", session_id=input.session_id, object_id=input.object_id
        )

        response = inference_api.remove_object(request)

        return [
            RLEMaskListOnFrame(
                frame_index=res.frame_index,
                rle_mask_list=[
                    RLEMaskForObject(
                        object_id=r.object_id,
                        rle_mask=RLEMask(
                            counts=r.mask.counts, size=r.mask.size, order="F"
                        ),
                    )
                    for r in res.results
                ],
            )
            for res in response.results
        ]

    @strawberry.mutation
    def clear_points_in_frame(
        self, input: ClearPointsInFrameInput, info: strawberry.Info
    ) -> RLEMaskListOnFrame:
        inference_api: InferenceAPI = info.context["inference_api"]

        request = ClearPointsInFrameRequest(
            type="clear_points_in_frame",
            session_id=input.session_id,
            frame_index=input.frame_index,
            object_id=input.object_id,
        )

        response = inference_api.clear_points_in_frame(request)

        return RLEMaskListOnFrame(
            frame_index=response.frame_index,
            rle_mask_list=[
                RLEMaskForObject(
                    object_id=r.object_id,
                    rle_mask=RLEMask(counts=r.mask.counts, size=r.mask.size, order="F"),
                )
                for r in response.results
            ],
        )

    @strawberry.mutation
    def clear_points_in_video(
        self, input: ClearPointsInVideoInput, info: strawberry.Info
    ) -> ClearPointsInVideo:
        inference_api: InferenceAPI = info.context["inference_api"]

        request = ClearPointsInVideoRequest(
            type="clear_points_in_video",
            session_id=input.session_id,
        )
        response = inference_api.clear_points_in_video(request)
        return ClearPointsInVideo(success=response.success)

    @strawberry.mutation
    def cancel_propagate_in_video(
        self, input: CancelPropagateInVideoInput, info: strawberry.Info
    ) -> CancelPropagateInVideo:
        inference_api: InferenceAPI = info.context["inference_api"]

        request = CancelPropagateInVideoRequest(
            type="cancel_propagate_in_video",
            session_id=input.session_id,
        )
        response = inference_api.cancel_propagate_in_video(request)
        return CancelPropagateInVideo(success=response.success)






