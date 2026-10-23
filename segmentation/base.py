from abc import ABC, abstractmethod
from dataclasses import dataclass

from marshmallow import Schema

from models import FOVAsset
from segmentation.outputs import SegmentationOutput


@dataclass
class SegmentationRequest:
    image_id: str


class Segmenter(ABC):
    request_schema: Schema

    @abstractmethod
    def segment(self, asset: FOVAsset, request: SegmentationRequest) -> SegmentationOutput:
        ...
