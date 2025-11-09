from __future__ import annotations

from collections.abc import Mapping

from ._composite import CompositeFilter
from .typing import FilterLike


def new_filter(f: FilterLike | None = None, /) -> FilterLike:
    if f is None:
        return CompositeFilter()
    if isinstance(f, Mapping):
        return CompositeFilter(f)  # pyright: ignore[reportArgumentType]
    return f
