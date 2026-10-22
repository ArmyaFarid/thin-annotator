from marshmallow import fields, validate

from schema.base import CamelCaseSchema


class TaskSchema(CamelCaseSchema):
    id = fields.Str(dump_only=True)
    batch_id = fields.Str(dump_only=True)

    images_folder = fields.Str(required=True)

    is_annotated = fields.Bool(dump_default=False)
    is_current = fields.Bool(dump_default=False)

    order = fields.Int(allow_none=True, validate=validate.Range(min=1))
    annotated_order = fields.Int(allow_none=True, validate=validate.Range(min=1))


class BatchSchema(CamelCaseSchema):
    id = fields.Str(dump_only=True)

    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    root_path = fields.Str(required=True, validate=validate.Length(min=1))
    task_count = fields.Int(dump_only=True)

    tasks = fields.List(fields.Nested(TaskSchema), dump_only=True)


class BatchSummarySchema(CamelCaseSchema):
    """Batch without the task collection — for list endpoints."""

    id = fields.Str(dump_only=True)
    name = fields.Str()
    root_path = fields.Str()
    task_count = fields.Int()


task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)
batch_schema = BatchSchema()
batches_schema = BatchSummarySchema(many=True)