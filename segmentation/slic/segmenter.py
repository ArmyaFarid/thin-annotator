import numpy as np
from skimage.segmentation import slic

from models import FOVAsset
from segmentation.base import Segmenter
from segmentation.images import load_rgb
from segmentation.outputs import LabelMap
from segmentation.slic.schema import SlicRequest, SlicRequestSchema


class SlicSegmenter(Segmenter):
    request_schema = SlicRequestSchema()

    def segment(self, asset: FOVAsset, request: SlicRequest) -> LabelMap:
        image = load_rgb(asset.image_path)
        x0, y0, w, h = map(int, request.bbox)
        portion = image[y0:y0 + h, x0:x0 + w]
        n_segments = int(20 * (w * h / 1000) ** 0.5)
        n_segments = max(10, min(n_segments, 300))
        labels = slic(portion, n_segments=n_segments, compactness=20, start_label=1)
        return LabelMap(
            image_width=image.shape[1],
            image_height=image.shape[0],
            x=x0,
            y=y0,
            labels=labels.astype(np.uint16),
        )
