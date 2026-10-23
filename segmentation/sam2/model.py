import os
from pathlib import Path

import torch

from app_conf import APP_ROOT, MODEL_SIZE
from sam2.build_sam import build_sam2
from sam2.sam2_image_predictor import SAM2ImagePredictor

CHECKPOINTS = {
    "tiny": ("configs/sam2.1/sam2.1_hiera_t.yaml", "checkpoints/sam2.1_hiera_tiny.pt"),
    "small": ("configs/sam2.1/sam2.1_hiera_s.yaml", "checkpoints/sam2.1_hiera_small.pt"),
    "large": ("configs/sam2.1/sam2.1_hiera_l.yaml", "checkpoints/sam2.1_hiera_large.pt"),
    "base_plus": ("configs/sam2.1/sam2.1_hiera_b+.yaml", "checkpoints/sam2.1_hiera_base_plus.pt"),
}


def select_device() -> torch.device:
    force_cpu = os.environ.get("SAM2_DEMO_FORCE_CPU_DEVICE", "0") == "1"
    if torch.cuda.is_available() and not force_cpu:
        return torch.device("cuda")
    if torch.backends.mps.is_available() and not force_cpu:
        return torch.device("mps")
    return torch.device("cpu")


def build_predictor(device: torch.device) -> SAM2ImagePredictor:
    cfg, ckpt = CHECKPOINTS.get(MODEL_SIZE, CHECKPOINTS["base_plus"])
    model = build_sam2(cfg, str(Path(APP_ROOT) / ckpt), device=device)
    return SAM2ImagePredictor(model)
