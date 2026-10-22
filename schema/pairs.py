from marshmallow import fields

from app_conf import API_URL
from data.data_types import PolarizedFilterType
from schema.base import CamelCaseSchema


class PairsQuerySchema(CamelCaseSchema):
    pairs_code = fields.Str(required=True)
    sample_id = fields.Str(required=True)


class ImageSchema(CamelCaseSchema):
    id = fields.Str(attribute="code")
    path = fields.Str()
    url = fields.Method("get_url")
    width = fields.Int()
    height = fields.Int()

    def get_url(self, image):
        return f"{API_URL}/image/{image.code}"


class AcquiredImageSchema(CamelCaseSchema):
    polarized_filter_type = fields.Enum(PolarizedFilterType)
    gamma = fields.Int(allow_none=True)
    rotation = fields.Int(allow_none=True)
    image = fields.Nested(ImageSchema)


class PairsSchema(CamelCaseSchema):
    pairs_code = fields.Str()
    sample_id = fields.Str()
    polarized_filter_types = fields.List(fields.Enum(PolarizedFilterType))
    rotations = fields.List(fields.Int(allow_none=True))
    gammas = fields.List(fields.Int(allow_none=True))
    acquired_images = fields.List(fields.Nested(AcquiredImageSchema))


pairs_query_schema = PairsQuerySchema()
pairs_schema = PairsSchema()
