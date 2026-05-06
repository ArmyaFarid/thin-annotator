# data/schema_image.py
import base64

import strawberry
from typing import Iterable, List
from data.data_types import (
    AddPointsImageInput, Image, StartSessionInput, StartSession,
    AddPointsInput, RLEMaskListOnFrame,
    RLEMaskForObject, RLEMask, ThinSectionImagePairs, SlicImageInput
)
from app_conf import DATA_PATH, THIN_SECTION_FOV_SAMPLE_PATH
from extensions import db
from inference.data_types import AddPointsImageRequest, StartSessionRequest, SlicImageRequest
from strawberry import relay
from data.store import get_images
from models import FOVAsset


@strawberry.type
class ImageQuery:

    @strawberry.field
    def default_image(self) -> Image:
        """
        Return the default image , the first
        """
        all_videos = get_images()

        return next(iter(all_videos.values()))


    @relay.connection(relay.ListConnection[Image])
    def images(self) -> Iterable[Image]:
        """
        Return all available images for the gallery.
        """
        all_images = get_images()
        return all_images.values()

@strawberry.type
class ThinSectionImagePairsQuery:



    @strawberry.field
    def default_pairs(self) -> ThinSectionImagePairs:
        asset = db.session.execute(db.select(FOVAsset).filter_by(sample_path=str(THIN_SECTION_FOV_SAMPLE_PATH))).scalar()
        return ThinSectionImagePairs(
            code=asset.thin_section_id,
            sample_id=asset.fov_id,
            label="Example pair",
        )


@strawberry.type
class ImageMutation:
    @strawberry.mutation
    def start_session_image(self, input: StartSessionInput, info: strawberry.Info) -> StartSession:
        # Uses the IMAGE API from context
        api = info.context["inference_image_api"]

        raw_pair_code = base64.b64decode(str(input.pairs_code)).decode("utf-8").split(":")[-1]

        print(raw_pair_code)
        
        # Reuse StartSessionRequest or make a specific one if fields differ
        request = StartSessionRequest(
            type="start_session_image",
            path=f"{DATA_PATH}/{input.path}",
            pairs_code=raw_pair_code,
            sample_id=input.sample_id,
        )
        
        # The image API saves the embeddings here
        response = api.start_session(request) 
        return StartSession(session_id=response.session_id)

    @strawberry.mutation
    def add_points_image(self, input: AddPointsImageInput, info: strawberry.Info) -> RLEMaskListOnFrame:
        api = info.context["inference_image_api"]

        # Image Way: Frame index is always 0
        request = AddPointsImageRequest(
            type="add_points",
            session_id=input.session_id,
            image_path=input.image_path,
            image_id=input.image_id.node_id,
            points=input.points,
            labels=input.labels,
            bboxes=input.bboxes,
        )
        
        # Call image predictor
        response = api.add_points_image(request)


        print("response ....")

        return RLEMaskListOnFrame(
            frame_index=0,
            rle_mask_list=[
                RLEMaskForObject(
                    object_id=r.object_id,
                    rle_mask=RLEMask(counts=r.mask.counts, size=r.mask.size, order="F"),
                )
                for r in response.results
            ],
        )

    @strawberry.mutation
    def compute_slic_image(self, input: SlicImageInput, info: strawberry.Info) -> RLEMaskListOnFrame:
        api = info.context["inference_image_api"]

        # Image Way: Frame index is always 0
        request = SlicImageRequest(
            type="add_points",
            session_id=input.session_id,
            image_path=input.image_path,
            image_id=input.image_id.node_id,
            bbox=input.bbox,
        )

        # Call image predictor
        response = api.compute_slic_image(request)

        print("response ....")

        return RLEMaskListOnFrame(
            frame_index=0,
            rle_mask_list=[
                RLEMaskForObject(
                    object_id=r.object_id,
                    rle_mask=RLEMask(counts=r.mask.counts, size=r.mask.size, order="F"),
                )
                for r in response.results
            ],
        )