from typing import Any, Unpack

import cytoolz as toolz
import fieldz
import wadler_lindig as wl

from liblaf.grapes.ext.wadler_lindig._typing import WadlerLindigOptions
from liblaf.grapes.sentinel import MISSING


def pdoc_fieldz(
    obj: object, **kwargs: Unpack[WadlerLindigOptions]
) -> wl.AbstractDoc | None:
    cls: type = type(obj)
    pairs: list[tuple[str, Any]] = []
    try:
        fields: tuple[fieldz.Field, ...] = fieldz.fields(obj)
    except TypeError:
        return None
    for field in fields:
        if not field.repr:
            continue
        value: Any = getattr(obj, field.name, MISSING)
        if kwargs.get("hide_defaults", True) and value is field.default:
            continue
        pairs.append((field.name, value))
    show_dataclass_module: bool = kwargs.get("show_dataclass_module", False)
    name_kwargs: dict[str, Any] = toolz.assoc(
        kwargs, "show_type_module", show_dataclass_module
    )
    return wl.bracketed(
        begin=wl.pdoc(cls, **name_kwargs) + wl.TextDoc("("),
        docs=wl.named_objs(pairs, **kwargs),
        sep=wl.comma,
        end=wl.TextDoc(")"),
        indent=kwargs.get("indent", 2),
    )
