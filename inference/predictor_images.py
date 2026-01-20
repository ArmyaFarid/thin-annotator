# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

import contextlib
import logging
import os
import uuid
from pathlib import Path
from threading import Lock
from typing import Any, Dict, Generator, List
from PIL import Image

import numpy as np
import torch
from app_conf import APP_ROOT, MODEL_SIZE
from inference.data_types import (
    AddPointsImageRequest,
    CloseSessionRequest,
    CloseSessionResponse,
    Mask,
    PropagateDataResponse,
    PropagateDataValue,
    StartSessionRequest,
    StartSessionResponse,
)
from pycocotools.mask import decode as decode_masks, encode as encode_masks
from sam2.build_sam import build_sam2
from sam2.sam2_image_predictor import SAM2ImagePredictor

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
            
            # Load the image (using PIL or OpenCV)
            image = Image.open(request.path)
            image_np = np.array(image.convert("RGB"))
            
            # This encodes the image and stores features inside self.predictor
            self.predictor.set_image(image_np)

            # image_embedding = predictor.get_image_embedding()
            # torch.save(image_embedding, "image_embedding.pt")

            # # save the high res features
            # high_res_features = predictor.get_high_res_features()
            # torch.save(high_res_features, "high_res_features.pt")

            session_state = {}
            if self.is_gpu:
                session_state = {
                    "image_embedding": self.predictor.get_image_embedding(),
                    "high_res_features": self.predictor.get_high_res_features(),
                    "orig_hw": image_np.shape[:2],
                }
            else:
                session_state = {
                    "image_embedding": self.predictor.get_image_embedding().cpu(),
                    "high_res_features": self.predictor.get_high_res_features(),
                    "orig_hw": image_np.shape[:2],
                }
            
            # We save the features in the session so we can swap back if 
            # the user changes which image they are working on
            # self.session_states[session_id] = {
            #     "features": self.predictor.get_image_embedding(),
            #     "orig_hw": image_np.shape[:2]
            # }
            self.session_states[session_id] = session_state
            return StartSessionResponse(session_id=session_id)

    def close_session(self, request: CloseSessionRequest) -> CloseSessionResponse:
        is_successful = self.__clear_session_state(request.session_id)
        return CloseSessionResponse(success=is_successful)

    def add_points(self, request: AddPointsImageRequest) -> PropagateDataResponse:
        with self.autocast_context(), self.inference_lock:
            session = self.__get_session(request.session_id)
            
            # Restore the image features for this specific session
            self.predictor.reset_predictor() # Clear old internal state
            
            # print(session["image_embedding"])

            # self.predictor.features = session["features"]
            # self.predictor.orig_hw = session["orig_hw"]
            # self.predictor.is_image_set = True

            # self.predictor.image_embedding = session["image_embedding"].to(self.device)
            # self.predictor.high_res_features = session["high_res_features"].to(self.device)
            # self.predictor.orig_hw = session["orig_hw"]

            self.predictor.set_image_embedding(
                    image_embedding = session["image_embedding"].to(self.device),
                    img_hw = session["orig_hw"],
                    high_res_features = session["high_res_features"]
            )

            # self.predictor.is_image_set = True

            # Run the prediction with the new points
            masks, scores, logits = self.predictor.predict(
                point_coords=np.array(request.points),
                point_labels=np.array(request.labels),
                multimask_output=False, # We usually want the single best mask
            )

            # masks is [1, H, W] after squeeze or indexing
            masks_binary = masks[0] 


            # --- DEBUGGING: SAVE IMAGE TO DISK ---
            # This converts the boolean mask to a grayscale image (0 or 255)
            debug_img = Image.fromarray((masks_binary * 255).astype(np.uint8))
            debug_img.save("debug_mask.png")
            print(f"Debug mask saved. Shape: {masks_binary.shape}, Sum: {np.sum(masks_binary)}")
            # -------------------------------------

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
            decoded_mask = decode_masks(coco_rle).squeeze().astype(np.uint8)

            # Save image
            Image.fromarray(decoded_mask * 255).save("debug_mask_from_rle.png")

            print("RLE size:", rle.size)
            print("Decoded mask shape:", decoded_mask.shape)
            print("Decoded sum:", decoded_mask.sum())

            return PropagateDataResponse(
                frame_index=0, # Always 0 for static image
                results=rle_mask_list,
            )

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
