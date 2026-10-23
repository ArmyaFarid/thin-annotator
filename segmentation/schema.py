import base64

import numpy as np
from marshmallow import fields

from schema.base import CamelCaseSchema
from segmentation.outputs import LabelMap, MaskList, SegmentationOutput


class RleMaskSchema(CamelCaseSchema):
    counts = fields.Str()
    size = fields.List(fields.Int())


class MaskListSchema(CamelCaseSchema):
    kind = fields.Constant("masks")
    image_width = fields.Int()
    image_height = fields.Int()
    masks = fields.List(fields.Nested(RleMaskSchema))


class LabelMapSchema(CamelCaseSchema):
    kind = fields.Constant("labelMap")
    image_width = fields.Int()
    image_height = fields.Int()
    x = fields.Int()
    y = fields.Int()
    width = fields.Function(lambda label_map: label_map.labels.shape[1])
    height = fields.Function(lambda label_map: label_map.labels.shape[0])
    dtype = fields.Constant("uint16")
    data = fields.Method("encode_labels")

    def encode_labels(self, label_map: LabelMap) -> str:
        labels = np.ascontiguousarray(label_map.labels, dtype=np.uint16)
        return base64.b64encode(labels.tobytes()).decode("ascii")


_output_schemas = {MaskList: MaskListSchema(), LabelMap: LabelMapSchema()}


def dump_output(output: SegmentationOutput) -> dict:
    return _output_schemas[type(output)].dump(output)
