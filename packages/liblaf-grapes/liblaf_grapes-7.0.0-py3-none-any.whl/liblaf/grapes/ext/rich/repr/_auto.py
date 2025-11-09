import functools
from collections.abc import Callable
from typing import Any, overload

import attrs
import rich.pretty
import rich.repr

from ._attrs import rich_repr_attrs


@overload
def auto_rich_repr[T: type](
    cls: T, *, repr: bool | None = None, rich_repr: bool | None = None
) -> T: ...
@overload
def auto_rich_repr[T: type](
    *, repr: bool | None = None, rich_repr: bool | None = None
) -> Callable[[T], T]: ...
def auto_rich_repr(
    cls: type | None = None,
    *,
    repr: bool | None = None,  # noqa: A002
    rich_repr: bool | None = None,
) -> Any:
    if cls is None:
        return functools.partial(auto_rich_repr, repr=repr, rich_repr=rich_repr)
    if repr is None:
        repr = "__repr__" in cls.__dict__  # noqa: A001
    if rich_repr is None:
        rich_repr = "__rich_repr__" in cls.__dict__
    if repr:
        cls.__repr__ = rich.pretty.pretty_repr  # pyright: ignore[reportAttributeAccessIssue]
    if rich_repr and attrs.has(cls):
        cls.__rich_repr__ = rich_repr_attrs  # pyright: ignore[reportAttributeAccessIssue]
    return cls
