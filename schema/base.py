from marshmallow import Schema


def camelcase(s: str) -> str:
    head, *tail = s.split("_")
    return head + "".join(word.capitalize() for word in tail)


class CamelCaseSchema(Schema):
    """Serializes snake_case attributes to camelCase keys, and back on load."""

    def on_bind_field(self, field_name, field_obj):
        field_obj.data_key = camelcase(field_obj.data_key or field_name)
