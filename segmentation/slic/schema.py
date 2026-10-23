from dataclasses import dataclass
from typing import List

from marshmallow import fields, post_load
from marshmallow.validate import Length

from schema.base import CamelCaseSchema
from segmentation.base import SegmentationRequest


@dataclass
class SlicRequest(SegmentationRequest):
    bbox: List[float]


class SlicRequestSchema(CamelCaseSchema):
    image_id = fields.Str(required=True)
    bbox = fields.List(fields.Float(), validate=Length(equal=4), required=True)

    @post_load
    def make_request(self, data, **kwargs) -> SlicRequest:
        return SlicRequest(**data)
