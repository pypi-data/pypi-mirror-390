import functools
from collections.abc import Callable
from typing import Any, overload

import attrs
import pydantic

from ._fieldz import rich_repr_fieldz


@overload
def auto_rich_repr[T: type](cls: T, *, rich_repr: bool | None = None) -> T: ...
@overload
def auto_rich_repr[T: type](*, rich_repr: bool | None = None) -> Callable[[T], T]: ...
def auto_rich_repr(cls: type | None = None, *, rich_repr: bool | None = None) -> Any:
    if cls is None:
        return functools.partial(auto_rich_repr, rich_repr=rich_repr)
    if rich_repr is None:
        rich_repr = "__rich_repr__" not in cls.__dict__
    if rich_repr and (attrs.has(cls) or issubclass(cls, pydantic.BaseModel)):
        cls.__rich_repr__ = rich_repr_fieldz  # pyright: ignore[reportAttributeAccessIssue]
    return cls
