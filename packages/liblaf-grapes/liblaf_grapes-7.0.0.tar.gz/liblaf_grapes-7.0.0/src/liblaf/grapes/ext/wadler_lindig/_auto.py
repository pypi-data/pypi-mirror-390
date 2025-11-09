import functools
from collections.abc import Callable
from typing import Any, overload

import attrs
import pydantic

from ._pformat import pformat
from .custom import pdoc_attrs, pdoc_pydantic


@overload
def auto_pdoc[T: type](
    cls: T, *, pdoc: bool | None = None, repr: bool | None = None
) -> T: ...
@overload
def auto_pdoc[T: type](
    *, pdoc: bool | None = None, repr: bool | None = None
) -> Callable[[T], T]: ...
def auto_pdoc(
    cls: type | None = None,
    *,
    pdoc: bool | None = None,
    repr: bool | None = None,  # noqa: A002
) -> Any:
    if cls is None:
        return functools.partial(auto_pdoc, pdoc=pdoc, repr=repr)
    if pdoc is None:
        pdoc = "__pdoc__" not in cls.__dict__
    if repr is None:
        repr = "__repr__" not in cls.__dict__  # noqa: A001
    if pdoc:
        if attrs.has(cls):
            cls.__pdoc__ = pdoc_attrs  # pyright: ignore[reportAttributeAccessIssue]
        elif issubclass(cls, pydantic.BaseModel):
            cls.__pdoc__ = pdoc_pydantic  # pyright: ignore[reportAttributeAccessIssue]
    if repr:
        cls.__repr__ = pformat  # pyright: ignore[reportAttributeAccessIssue]
    return cls
