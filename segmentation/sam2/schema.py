from dataclasses import dataclass
from typing import List

from marshmallow import ValidationError, fields, post_load, validates_schema
from marshmallow.validate import Length

from schema.base import CamelCaseSchema
from segmentation.base import SegmentationRequest


@dataclass
class Sam2Request(SegmentationRequest):
    points: List[List[float]]
    labels: List[int]
    bboxes: List[List[float]]


class Sam2RequestSchema(CamelCaseSchema):
    image_id = fields.Str(required=True)
    points = fields.List(fields.List(fields.Float(), validate=Length(equal=2)), required=True)
    labels = fields.List(fields.Int(strict=True), required=True)
    bboxes = fields.List(fields.List(fields.Float(), validate=Length(equal=4)), required=True)

    @validates_schema
    def validate_labels(self, data, **kwargs):
        if len(data["points"]) != len(data["labels"]):
            raise ValidationError("Must have one label per point.", "labels")

    @post_load
    def make_request(self, data, **kwargs) -> Sam2Request:
        data["bboxes"] = [[x, y, x + w, y + h] for x, y, w, h in data["bboxes"]]
        return Sam2Request(**data)
