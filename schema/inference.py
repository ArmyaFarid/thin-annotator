from marshmallow import fields, post_load

from inference.data_types import AddPointsImageRequest, SlicImageRequest
from schema.base import CamelCaseSchema


class AddPointsRequestSchema(CamelCaseSchema):
    image_id = fields.Str(required=True)
    labels = fields.List(fields.Int(strict=True), required=True)
    points = fields.List(fields.List(fields.Float()), required=True)
    bboxes = fields.List(fields.List(fields.Float()), required=True)

    @post_load
    def make_request(self, data, **kwargs) -> AddPointsImageRequest:
        return AddPointsImageRequest(type="add_points", **data)


class SlicRequestSchema(CamelCaseSchema):
    image_id = fields.Str(required=True)
    bbox = fields.List(fields.Float(), required=True)

    @post_load
    def make_request(self, data, **kwargs) -> SlicImageRequest:
        return SlicImageRequest(type="slic", **data)


class RleMaskSchema(CamelCaseSchema):
    counts = fields.Str()
    size = fields.List(fields.Int())


class ObjectMaskSchema(CamelCaseSchema):
    object_id = fields.Int()
    rle_mask = fields.Nested(RleMaskSchema, attribute="mask")


class MaskListSchema(CamelCaseSchema):
    rle_mask_list = fields.List(fields.Nested(ObjectMaskSchema), attribute="results")


class BBoxSchema(CamelCaseSchema):
    x = fields.Int()
    y = fields.Int()
    w = fields.Int()
    h = fields.Int()


class SlicLabelMapSchema(CamelCaseSchema):
    data = fields.Str()      # base64 of the raw uint16 buffer, C-order, row-major
    height = fields.Int()
    width = fields.Int()
    dtype = fields.Str()
    bbox = fields.Nested(BBoxSchema)


add_points_request_schema = AddPointsRequestSchema()
slic_request_schema = SlicRequestSchema()
mask_list_schema = MaskListSchema()
slic_label_map_schema = SlicLabelMapSchema()
