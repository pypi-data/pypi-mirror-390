import fieldz
from rich.repr import RichReprResult

from liblaf.grapes.sentinel import MISSING


def rich_repr_fieldz(obj: object) -> RichReprResult:
    for field in fieldz.fields(obj):
        if not field.repr:
            continue
        yield field.name, getattr(obj, field.name, MISSING), field.default
