import contextlib
import contextvars
import types
from collections.abc import Callable
from typing import Any, Self, overload, override

import attrs
import wrapt
from typing_extensions import deprecated

import liblaf.grapes.itertools as it

_depth: contextvars.ContextVar[int] = contextvars.ContextVar("depth", default=0)


@attrs.define
class DepthTrackerDecorator(contextlib.AbstractContextManager):
    _depth_inc: int | None = attrs.field(default=None, alias="depth_inc")
    _token: contextvars.Token[int] | None = attrs.field(default=None, init=False)

    @override  # impl contextlib.AbstractContextManager
    def __enter__(self) -> Self:
        depth_inc: int = it.first_not_none(self._depth_inc, 1)
        self._token = _depth.set(_depth.get() + depth_inc)
        return self

    @override  # impl contextlib.AbstractContextManager
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: types.TracebackType | None,
        /,
    ) -> None:
        assert self._token is not None
        _depth.reset(self._token)
        del self._token

    def __call__[**P, T](self, func: Callable[P, T], /) -> Callable[P, T]:
        @wrapt.decorator
        def wrapper(
            wrapped: Callable[P, T],
            _instance: Any,
            args: tuple[Any, ...],
            kwargs: dict[str, Any],
        ) -> T:
            __tracebackhide__ = True
            depth_inc: int = it.first_not_none(self._depth_inc, 2)
            token: contextvars.Token[int] = _depth.set(_depth.get() + depth_inc)
            try:
                return wrapped(*args, **kwargs)
            finally:
                _depth.reset(token)

        return wrapper(func)


@attrs.define
class DepthTracker:
    @overload
    def __call__(self, /, *, depth: int | None = None) -> DepthTrackerDecorator: ...
    @overload
    def __call__[C: Callable](self, func: C, /, *, depth: int | None = None) -> C: ...
    @deprecated("Use `__tracebackhide__ = True` instead.")
    def __call__(
        self, func: Callable | None = None, /, *, depth: int | None = None
    ) -> Callable:
        decorator = DepthTrackerDecorator(depth_inc=depth)
        if func is None:
            return decorator
        return decorator(func)

    @property
    @deprecated("Use `__tracebackhide__ = True` instead.")
    def depth(self) -> int:
        return _depth.get()


helper: DepthTracker = DepthTracker()
