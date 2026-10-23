import contextlib
from threading import Lock

import numpy as np
import torch

from mask_utilities.holes import clean_mask
from models import FOVAsset
from segmentation.base import Segmenter
from segmentation.outputs import MaskList
from segmentation.sam2.embeddings import ensure_embeddings, load_embeddings
from segmentation.sam2.model import build_predictor, select_device
from segmentation.sam2.schema import Sam2Request, Sam2RequestSchema


class Sam2Segmenter(Segmenter):
    request_schema = Sam2RequestSchema()

    def __init__(self) -> None:
        self.device = select_device()
        self.predictor = build_predictor(self.device)
        self.lock = Lock()

    def autocast_context(self):
        return torch.autocast("cuda", dtype=torch.bfloat16) if self.device.type == "cuda" else contextlib.nullcontext()

    def segment(self, asset: FOVAsset, request: Sam2Request) -> MaskList:
        with self.autocast_context(), self.lock:
            cache_path = ensure_embeddings(self.predictor, self.device, asset)
            image_hw = load_embeddings(self.predictor, self.device, cache_path)

            points = np.array(request.points) if request.points else None
            labels = np.array(request.labels) if request.labels else None
            if points is not None and labels is not None:
                valid = labels != -1
                points, labels = points[valid], labels[valid]

            bboxes = np.array(request.bboxes, dtype=np.float32) if request.bboxes else None
            if bboxes is not None and bboxes.ndim == 2:
                bboxes = bboxes[0]

            if points is not None or bboxes is not None:
                masks, _, _ = self.predictor.predict(
                    point_coords=points,
                    point_labels=labels,
                    box=bboxes,
                    multimask_output=True,
                )
                mask = clean_mask(masks[1], max_hole_area=400, min_object_area=400)
            else:
                mask = np.zeros(image_hw, dtype=bool)

            return MaskList.from_binary_masks([mask], image_hw)
