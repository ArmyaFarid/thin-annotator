import os
from typing import Tuple

import torch

from app_conf import SAM_PREPROCESSED_IMAGE_PATH
from extensions import db
from models import FOVAsset
from sam2.sam2_image_predictor import SAM2ImagePredictor
from segmentation.images import load_rgb


def ensure_embeddings(predictor: SAM2ImagePredictor, device: torch.device, asset: FOVAsset) -> str:
    if asset.sam_cache_path and os.path.exists(asset.sam_cache_path):
        return asset.sam_cache_path

    print(f"[SAM] JIT Encoding: {asset.image_path}")
    image_np = load_rgb(asset.image_path)

    predictor.set_image(image_np)
    image_embedding = predictor.get_image_embedding()
    high_res_features = predictor.get_high_res_features()

    if device.type == "cpu":
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


def load_embeddings(predictor: SAM2ImagePredictor, device: torch.device, cache_path: str) -> Tuple[int, int]:
    cached = torch.load(cache_path, weights_only=True)
    predictor.reset_predictor()
    predictor.set_image_embedding(
        image_embedding=cached["image_embedding"].to(device),
        img_hw=cached["orig_hw"],
        high_res_features=cached["high_res_features"],
    )
    return cached["orig_hw"]
