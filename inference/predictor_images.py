# Copyright (c) 2025 Armya BAKOUAN.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file in the root directory of this source tree.

import contextlib
import logging
import os
from pathlib import Path
from threading import Lock
from typing import Any, List
from PIL import Image

import numpy as np
import torch
from app_conf import APP_ROOT, MODEL_SIZE, SAM_PREPROCESSED_IMAGE_PATH
from extensions import db
from models import FOVAsset
from inference.data_types import (
    AddPointsImageRequest,
    Mask,
    PropagateDataResponse,
    PropagateDataValue,
    SlicImageRequest,
)
from pycocotools.mask import encode as encode_masks
from sam2.build_sam import build_sam2
from sam2.sam2_image_predictor import SAM2ImagePredictor
from skimage.segmentation import slic

logger = logging.getLogger(__name__)


class InferenceImageAPI:

    def __init__(self) -> None:
        super(InferenceImageAPI, self).__init__()

        # No session_states dictionary here

        checkpoints = {
            "tiny": ("configs/sam2.1/sam2.1_hiera_t.yaml", "checkpoints/sam2.1_hiera_tiny.pt"),
            "small": ("configs/sam2.1/sam2.1_hiera_s.yaml", "checkpoints/sam2.1_hiera_small.pt"),
            "large": ("configs/sam2.1/sam2.1_hiera_l.yaml", "checkpoints/sam2.1_hiera_large.pt"),
            "base_plus": ("configs/sam2.1/sam2.1_hiera_b+.yaml", "checkpoints/sam2.1_hiera_base_plus.pt")
        }

        cfg, ckpt = checkpoints.get(MODEL_SIZE, checkpoints["base_plus"])
        checkpoint_path = Path(APP_ROOT) / ckpt

        force_cpu = os.environ.get("SAM2_DEMO_FORCE_CPU_DEVICE", "0") == "1"
        if torch.cuda.is_available() and not force_cpu:
            self.device = torch.device("cuda")
        elif torch.backends.mps.is_available() and not force_cpu:
            self.device = torch.device("mps")
        else:
            self.device = torch.device("cpu")

        self.sam2_model = build_sam2(cfg, str(checkpoint_path), device=self.device)
        self.predictor = SAM2ImagePredictor(self.sam2_model)
        self.inference_lock = Lock()

    def autocast_context(self):
        return torch.autocast("cuda", dtype=torch.bfloat16) if self.device.type == "cuda" else contextlib.nullcontext()

    def _ensure_embeddings(self, asset: FOVAsset) -> str:
        """Helper to ensure embeddings exist and return the path."""
        if asset.sam_cache_path and os.path.exists(asset.sam_cache_path):
            return asset.sam_cache_path

        # If no cache, generate it now (Stateless JIT encoding)
        print(f"[SAM] JIT Encoding: {asset.image_path}")
        image = Image.open(asset.image_path)
        image_np = np.array(image.convert("RGB"))

        self.predictor.set_image(image_np)
        image_embedding = self.predictor.get_image_embedding()
        high_res_features = self.predictor.get_high_res_features()

        if self.device.type == "cpu":
            image_embedding = image_embedding.cpu()

        filename = os.path.splitext(os.path.basename(asset.image_path))[0]
        cache_path = os.path.join(SAM_PREPROCESSED_IMAGE_PATH, f"{filename}.pt")
        os.makedirs(SAM_PREPROCESSED_IMAGE_PATH, exist_ok=True)

        torch.save({
            "image_embedding": image_embedding,
            "high_res_features": high_res_features,
            "orig_hw": image_np.shape[:2],
        }, cache_path)

        asset.sam_cache_path = cache_path
        db.session.commit()
        return cache_path

    def add_points_image(self, request: AddPointsImageRequest) -> PropagateDataResponse:
        with self.autocast_context(), self.inference_lock:
            # 1. Query DB using the image_id passed from frontend
            asset = FOVAsset.query.get(request.image_id)
            if not asset:
                raise ValueError(f"Asset with ID {request.image_id} not found.")

            # 2. Get/Generate embeddings path
            cache_path = self._ensure_embeddings(asset)

            # 3. Load embeddings into predictor
            session_data = torch.load(cache_path, weights_only=True)
            self.predictor.reset_predictor()
            self.predictor.set_image_embedding(
                image_embedding=session_data["image_embedding"].to(self.device),
                img_hw=session_data["orig_hw"],
                high_res_features=session_data["high_res_features"]
            )

            # 4. Standard SAM Prediction logic
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
                    multimask_output=False,
                )
                masks_binary = masks[0]
            else:
                masks_binary = np.zeros(session_data["orig_hw"], dtype=bool)

            rle_list = self.__get_rle_mask_list([0], [masks_binary])
            return PropagateDataResponse(frame_index=0, results=rle_list)

    def compute_slic_image(self, request: SlicImageRequest) -> PropagateDataResponse:
        # Similar logic: query by ID, open path, run SLIC
        with self.autocast_context(), self.inference_lock:
            asset = FOVAsset.query.get(request.image_id)
            if not asset: raise ValueError("Asset not found")

            image = Image.open(asset.image_path)
            masks = self.__slicOnImage(np.array(image.convert("RGB")), request.bbox)
            rle_list = self.__get_rle_mask_list(list(range(len(masks))), masks)
            return PropagateDataResponse(frame_index=0, results=rle_list)

    def __slicOnImage(self, image: np.ndarray, bbox: List[int]) -> list[np.ndarray]:
        x0, y0, w, h = map(int, bbox)
        portion = image[y0:y0 + h, x0:x0 + w]
        n_segments = max(10, int((w * h) / 400))
        segments_slic = slic(portion, n_segments=n_segments, compactness=20, start_label=1)

        binary_mask_list = []
        for seg_id in np.unique(segments_slic):
            full_mask = np.zeros(image.shape[:2], dtype=bool)
            full_mask[y0:y0 + h, x0:x0 + w] = (segments_slic == seg_id)
            binary_mask_list.append(full_mask)
        return binary_mask_list

    def __get_rle_mask_list(self, object_ids: List[int], masks: List[np.ndarray]) -> List[PropagateDataValue]:
        return [self.__get_mask_for_object(oid, m) for oid, m in zip(object_ids, masks)]

    def __get_mask_for_object(self, object_id: int, mask: np.ndarray) -> PropagateDataValue:
        mask_rle = encode_masks(np.array(mask, dtype=np.uint8, order="F"))
        return PropagateDataValue(
            object_id=object_id,
            mask=Mask(size=mask_rle["size"], counts=mask_rle["counts"].decode())
        )