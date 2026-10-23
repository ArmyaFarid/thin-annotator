from typing import Dict

from segmentation.base import Segmenter
from segmentation.sam2.segmenter import Sam2Segmenter
from segmentation.slic.segmenter import SlicSegmenter


def build_segmenters() -> Dict[str, Segmenter]:
    return {"sam2": Sam2Segmenter(), "slic": SlicSegmenter()}
