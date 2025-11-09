from typing import Any, Unpack

import cytoolz as toolz
import pydantic
import wadler_lindig as wl

from liblaf.grapes.ext.wadler_lindig._typing import WadlerLindigOptions

UNSET = wl.TextDoc("<unset>")


def pdoc_pydantic(
    obj: pydantic.BaseModel, **kwargs: Unpack[WadlerLindigOptions]
) -> wl.AbstractDoc | None:
    if not isinstance(obj, pydantic.BaseModel):
        return None
    cls: type[pydantic.BaseModel] = type(obj)
    pairs: list[tuple[str, Any]] = []
    for name, field in cls.model_fields.items():
        if not field.repr:
            continue
        value: object = getattr(obj, name, UNSET)
        if kwargs.get("hide_defaults", True) and value is field.default:
            continue
        pairs.append((name, value))
    show_dataclass_module: bool = kwargs.get("show_dataclass_module", False)
    name_kwargs: dict[str, Any] = toolz.assoc(
        kwargs, "show_type_module", show_dataclass_module
    )
    return wl.bracketed(
        begin=wl.pdoc(type(obj), **name_kwargs) + wl.TextDoc("("),
        docs=wl.named_objs(pairs, **kwargs),
        sep=wl.comma,
        end=wl.TextDoc(")"),
        indent=kwargs.get("indent", 2),
    )
