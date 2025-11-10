import functools
from typing import Any

import attrs

from liblaf.grapes.ext.rich.repr import rich_repr_fieldz
from liblaf.grapes.ext.wadler_lindig import pdoc_fieldz, pformat
from liblaf.grapes.functools import wraps


@wraps(attrs.define)
def define(maybe_cls: type | None = None, **kwargs) -> Any:
    if maybe_cls is None:
        return functools.partial(define, **kwargs)
    auto_detect: bool = kwargs.get("auto_detect", True)
    repr_: bool | None = kwargs.get("repr")
    if auto_detect and repr_ is None and "__repr__" not in maybe_cls.__dict__:
        repr_ = True
    if repr_:
        maybe_cls.__repr__ = pformat  # pyright: ignore[reportAttributeAccessIssue]
        kwargs["repr"] = False
    if "__pdoc__" not in maybe_cls.__dict__:
        maybe_cls.__pdoc__ = pdoc_fieldz
    if "__rich_repr__" not in maybe_cls.__dict__:
        maybe_cls.__rich_repr__ = rich_repr_fieldz
    return attrs.define(maybe_cls, **kwargs)
