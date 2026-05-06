# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

import contextlib
import logging
import os
import uuid
import time
from pathlib import Path
from threading import Lock
from typing import Any, Dict, Generator, List
from PIL import Image

from skimage.segmentation import slic

import numpy as np
import torch
from app_conf import APP_ROOT, MODEL_SIZE, SAM_PREPROCESSED_IMAGE_PATH, DATA_PATH
from data.csv_queries import save_sam_cache_path, get_row_by_image_path, load_pairs_csv
from extensions import db
from inference.data_types import (
    AddPointsImageRequest,
    CloseSessionRequest,
    CloseSessionResponse,
    Mask,
    PropagateDataResponse,
    PropagateDataValue,
    StartSessionRequest,
    StartSessionResponse, SlicImageRequest,
)
from pycocotools.mask import decode as decode_masks, encode as encode_masks
from sam2.build_sam import build_sam2
from sam2.sam2_image_predictor import SAM2ImagePredictor

from models import FOVAsset

logger = logging.getLogger(__name__)


class InferenceImageAPI:

    def __init__(self) -> None:
        super(InferenceImageAPI, self).__init__()

        self.session_states: Dict[str, Any] = {}
        self.score_thresh = 0

        if MODEL_SIZE == "tiny":
            checkpoint = Path(APP_ROOT) / "checkpoints/sam2.1_hiera_tiny.pt"
            model_cfg = "configs/sam2.1/sam2.1_hiera_t.yaml"
        elif MODEL_SIZE == "small":
            checkpoint = Path(APP_ROOT) / "checkpoints/sam2.1_hiera_small.pt"
            model_cfg = "configs/sam2.1/sam2.1_hiera_s.yaml"
        elif MODEL_SIZE == "large":
            checkpoint = Path(APP_ROOT) / "checkpoints/sam2.1_hiera_large.pt"
            model_cfg = "configs/sam2.1/sam2.1_hiera_l.yaml"
        else:  # base_plus (default)
            checkpoint = Path(APP_ROOT) / "checkpoints/sam2.1_hiera_base_plus.pt"
            model_cfg = "configs/sam2.1/sam2.1_hiera_b+.yaml"

        # select the device for computation
        force_cpu_device = os.environ.get("SAM2_DEMO_FORCE_CPU_DEVICE", "0") == "1"
        if force_cpu_device:
            logger.info("forcing CPU device for SAM 2 demo")
        if torch.cuda.is_available() and not force_cpu_device:
            device = torch.device("cuda")
        elif torch.backends.mps.is_available() and not force_cpu_device:
            device = torch.device("mps")
        else:
            device = torch.device("cpu")
        logger.info(f"using device: {device}")

        print(f"using device: {device}")
        if device.type == "cuda":
            # turn on tfloat32 for Ampere GPUs (https://pytorch.org/docs/stable/notes/cuda.html#tensorfloat-32-tf32-on-ampere-devices)
            if torch.cuda.get_device_properties(0).major >= 8:
                torch.backends.cuda.matmul.allow_tf32 = True
                torch.backends.cudnn.allow_tf32 = True
        elif device.type == "mps":
            logging.warning(
                "\nSupport for MPS devices is preliminary. SAM 2 is trained with CUDA and might "
                "give numerically different outputs and sometimes degraded performance on MPS. "
                "See e.g. https://github.com/pytorch/pytorch/issues/84936 for a discussion."
            )



        self.device = device
        self.is_gpu = self.device.type in ["cuda", "mps"]
        torch.set_grad_enabled(False)
        if self.device.type == "cpu":
            torch.set_num_threads(os.cpu_count())
            torch.set_num_interop_threads(1)

        self.sam2_model = build_sam2(model_cfg, checkpoint, device=device)
        self.predictor = SAM2ImagePredictor(
            self.sam2_model
        )
        self.inference_lock = Lock()

    def autocast_context(self):
        if self.device.type == "cuda":
            return torch.autocast("cuda", dtype=torch.bfloat16)
        else:
            return contextlib.nullcontext()

    def start_session(self, request: StartSessionRequest) -> StartSessionResponse:
        with self.autocast_context(), self.inference_lock:
            session_id = str(uuid.uuid4())

            assets = FOVAsset.query.filter_by(
                thin_section_id=request.pairs_code,
                fov_id=request.sample_id
            ).all()

            if not assets:
                raise ValueError(f"No images found for pair_code: {request.pairs_code}")

            image_cache_map = {}
            for row in assets:
                cache_path = self._encode_and_save(row.image_path)
                image_cache_map[row.id] = cache_path
                row.cache_path = cache_path

            self.session_states[session_id] = {
                "pair_code": request.pairs_code,
                "image_cache_map": image_cache_map,
                "created_at": time.time(),
            }
            try:
                db.session.commit()
                print(f"Successfully updated cache paths for {len(assets)} assets.")
            except Exception as e:
                db.session.rollback()  # Undo changes if something goes wrong
                print(f"Failed to save to database: {e}")
                raise
            return StartSessionResponse(session_id=session_id)

    def _encode_and_save(self, image_path: str) -> str:

        asset = FOVAsset.query.filter_by(image_path=image_path).first()
        cached_path = asset.sam_cache_path if asset else None

        if cached_path and os.path.exists(cached_path):
            print(f"[SAM] Cache already exists for {image_path}, skipping encoding")
            return cached_path

        print(f"[SAM] Encoding image: {image_path}")
        image = Image.open(image_path)
        image_np = np.array(image.convert("RGB"))
        self.predictor.set_image(image_np)

        image_embedding = self.predictor.get_image_embedding()
        high_res_features = self.predictor.get_high_res_features()

        if not self.is_gpu:
            image_embedding = image_embedding.cpu()

        filename = os.path.splitext(os.path.basename(image_path))[0]
        cache_path = os.path.join(SAM_PREPROCESSED_IMAGE_PATH, f"{filename}.pt")
        os.makedirs(SAM_PREPROCESSED_IMAGE_PATH, exist_ok=True)
        torch.save({
            "image_embedding": image_embedding,
            "high_res_features": high_res_features,
            "orig_hw": image_np.shape[:2],
        }, cache_path)

        if asset:
            # 2. Update the attribute
            asset.sam_cache_path = cache_path

            # 3. Commit the change to the database
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Error saving cache path: {e}")
        else:
            # Optional: Handle the case where the image isn't in the DB yet
            print(f"Warning: No database record found for path {image_path}")

        print(f"[SAM] Saved cache: {cache_path}")
        return cache_path

    def close_session(self, request: CloseSessionRequest) -> CloseSessionResponse:
        is_successful = self.__clear_session_state(request.session_id)
        return CloseSessionResponse(success=is_successful)

    def add_points_image(self, request: AddPointsImageRequest) -> PropagateDataResponse:
        with self.autocast_context(), self.inference_lock:
            session = self.__get_session(request.session_id)
            
            # Restore the image features for this specific session
            self.predictor.reset_predictor() # Clear old internal state

            print(request.image_path)

            cache_path = session["image_cache_map"][request.image_id]

            print(request.image_id)
            print(cache_path)
            session_data = torch.load(cache_path,weights_only=True)

            self.predictor.set_image_embedding(
                image_embedding=session_data["image_embedding"].to(self.device),
                img_hw=session_data["orig_hw"],
                high_res_features=session_data["high_res_features"]
            )

            points = np.array(request.points)
            labels = np.array(request.labels)

            if points.size > 0:
                valid = labels != -1
                points = points[valid]
                labels = labels[valid]
            else:
                points = None
                labels = None

            if request.bboxes:
                bboxes = np.array(request.bboxes, dtype=np.float32)
                if bboxes.shape[0] == 1:
                    bboxes = bboxes[0]
            else:
                bboxes = None

            if points is not None or bboxes is not None:
                masks, scores, logits = self.predictor.predict(
                    point_coords=points,
                    point_labels=labels,
                    box=bboxes,
                    multimask_output=False,
                )
            else:
                masks, scores, logits = np.array([]), np.array([]), np.array([])


            # masks is [1, H, W] after squeeze or indexing
            masks_binary = masks[0]

            # Convert to RLE for the frontend
            rle_mask_list = self.__get_rle_mask_list(
                object_ids=[0], 
                masks=[masks_binary]
            )


            rle = rle_mask_list[0].mask

            # Build COCO RLE object
            coco_rle = {
                "size": rle.size,
                "counts": rle.counts.encode("utf-8")  # pycocotools expects bytes
            }

            # Decode
            # decoded_mask = decode_masks(coco_rle).squeeze().astype(np.uint8)

            # # Save image
            # Image.fromarray(decoded_mask * 255).save("debug_mask_from_rle.png")

            # print("RLE size:", rle.size)
            # print("Decoded mask shape:", decoded_mask.shape)
            # print("Decoded sum:", decoded_mask.sum())

            return PropagateDataResponse(
                frame_index=0, # Always 0 for static image
                results=rle_mask_list,
            )



    def compute_slic_image(self, request: SlicImageRequest) -> PropagateDataResponse:
        with self.autocast_context(), self.inference_lock:
            session = self.__get_session(request.session_id)

            asset = FOVAsset.query.filter_by(id=request.image_id).first()

            print(asset.image_path)

            image = Image.open(asset.image_path)
            image_np = np.array(image.convert("RGB"))

            bbox = np.array(request.bbox)

            masks = self.__slicOnImage(image_np, bbox)


            # Convert to RLE for the frontend
            rle_mask_list = self.__get_rle_mask_list(
                object_ids=list(range(len(masks))),
                masks=masks
            )

            return PropagateDataResponse(
                frame_index=0,  # Always 0 for static image
                results=rle_mask_list,
            )

    def __slicOnImage(self, image: np.ndarray, bbox: List[int], on_full_image: bool = False) -> list[np.ndarray]:
        x0, y0, w, h = map(int, bbox)
        print(w, h )

        if not on_full_image:
            portion = image[y0:y0 + h, x0:x0 + w]
            target_size = 400  # pixels per segment (tune this)
            n_segments = max(10, int((w * h) / target_size))
            segments_slic = slic(portion, n_segments=n_segments, compactness=20, start_label=1)

            binary_mask_list = []
            for seg_id in np.unique(segments_slic):
                # Build a full-image-sized mask, place the segment in the bbox region
                full_mask = np.zeros(image.shape[:2], dtype=bool)
                full_mask[y0:y0 + h, x0:x0 + w] = (segments_slic == seg_id)
                binary_mask_list.append(full_mask)

        else:
            segments_slic = slic(image, n_segments=20, compactness=20, start_label=1)

            # Find which segment IDs have any overlap with the bbox
            bbox_region = segments_slic[y0:y0 + h, x0:x0 + w]
            seg_ids_in_bbox = np.unique(bbox_region)

            binary_mask_list = []
            for seg_id in seg_ids_in_bbox:
                # Full-size mask for each segment (entire segment, not clipped)
                full_mask = (segments_slic == seg_id)
                binary_mask_list.append(full_mask)

        return binary_mask_list

    def __get_rle_mask_list(
        self, object_ids: List[int], masks: np.ndarray
    ) -> List[PropagateDataValue]:
        """
        Return a list of data values, i.e. list of object/mask combos.
        """
        return [
            self.__get_mask_for_object(object_id=object_id, mask=mask)
            for object_id, mask in zip(object_ids, masks)
        ]

    def __get_mask_for_object(
        self, object_id: int, mask: np.ndarray
    ) -> PropagateDataValue:
        """
        Create a data value for an object/mask combo.
        """
        mask_rle = encode_masks(np.array(mask, dtype=np.uint8, order="F"))
        mask_rle["counts"] = mask_rle["counts"].decode()
        return PropagateDataValue(
            object_id=object_id,
            mask=Mask(
                size=mask_rle["size"],
                counts=mask_rle["counts"],
            ),
        )

    def __get_session(self, session_id: str):
        session = self.session_states.get(session_id, None)
        if session is None:
            raise RuntimeError(
                f"Cannot find session {session_id}; it might have expired"
            )
        return session

    def __get_session_stats(self):
        """Get a statistics string for live sessions and their GPU usage."""
        # print both the session ids and their video frame numbers
        live_session_strs = [
            f"'{session_id}' ({session['state']['num_frames']} frames, "
            f"{len(session['state']['obj_ids'])} objects)"
            for session_id, session in self.session_states.items()
        ]
        session_stats_str = (
            "Test String Here - -"
            f"live sessions: [{', '.join(live_session_strs)}], GPU memory: "
            f"{torch.cuda.memory_allocated() // 1024**2} MiB used and "
            f"{torch.cuda.memory_reserved() // 1024**2} MiB reserved"
            f" (max over time: {torch.cuda.max_memory_allocated() // 1024**2} MiB used "
            f"and {torch.cuda.max_memory_reserved() // 1024**2} MiB reserved)"
        )
        return session_stats_str

    def __clear_session_state(self, session_id: str) -> bool:
        session = self.session_states.pop(session_id, None)
        if session is None:
            logger.warning(
                f"cannot close session {session_id} as it does not exist (it might have expired); "
                f"{self.__get_session_stats()}"
            )
            return False
        else:
            logger.info(f"removed session {session_id}; {self.__get_session_stats()}")
            return True
