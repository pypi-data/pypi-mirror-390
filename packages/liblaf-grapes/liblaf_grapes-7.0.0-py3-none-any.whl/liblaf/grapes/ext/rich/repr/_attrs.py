import attrs
import rich.repr


def rich_repr_attrs(obj: object) -> rich.repr.Result:
    cls: type = type(obj)
    assert attrs.has(cls)
    for field in attrs.fields(cls):
        field: attrs.Attribute
        if not field.repr:
            continue
        yield field.name, getattr(obj, field.name, attrs.NOTHING), field.default
