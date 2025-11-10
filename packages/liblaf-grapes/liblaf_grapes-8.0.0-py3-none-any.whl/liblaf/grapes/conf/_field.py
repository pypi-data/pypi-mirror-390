import contextlib
import contextvars
from collections.abc import Callable, Generator
from typing import Self, TypedDict, Unpack

import attrs
import wadler_lindig as wl
import wrapt
from rich.repr import RichReprResult

from liblaf.grapes.sentinel import MISSING

from ._environ import environ


@attrs.frozen
class Field[T]:
    _var: contextvars.ContextVar[T] = attrs.field(repr=False, alias="var")

    def __init__(
        self,
        name: str,
        default: T | MISSING = MISSING,
        *,
        env: str | None = None,
        factory: Callable[[], T] | None = None,
        type: type[T] | None = None,  # noqa: A002
        **_kwargs,
    ) -> None:
        if env is None:
            env = name.replace(".", "_").upper()
        value: T | MISSING = MISSING
        if value is MISSING and env is not None:
            value = environ.get(env, MISSING, typ=type)
        if value is MISSING and default is not MISSING:
            value = default
        if value is MISSING and factory is not None:
            value = factory()
        var: contextvars.ContextVar[T]
        if value is MISSING:
            var = contextvars.ContextVar(name)
        else:
            var = contextvars.ContextVar(name, default=value)
        self.__attrs_init__(var=var)  # pyright: ignore[reportAttributeAccessIssue]

    def __class_getitem__(cls, item: type[T]) -> type[Self]:
        return wrapt.partial(cls, type=item)  # pyright: ignore[reportReturnType]

    def __repr__(self) -> str:
        # TODO: use wadler-lindig
        return f"Field(name={self.name!r}, value={self.get()!r})"

    def __pdoc__(self, **kwargs) -> wl.AbstractDoc | None:
        pass

    def __rich_repr__(self) -> RichReprResult:
        yield "name", self.name
        yield "value", self.get()

    @property
    def name(self) -> str:
        return self._var.name

    def get(self) -> T:
        return self._var.get()

    def set(self, value: T, /) -> None:
        self._var.set(value)

    @contextlib.contextmanager
    def overrides(self, value: T, /) -> Generator[T]:
        token: contextvars.Token[T] = self._var.set(value)
        try:
            yield value
        finally:
            self._var.reset(token)


class FieldKwargs[T](TypedDict, total=False):
    default: T
    env: str
    factory: Callable[[], T]
    type: type[T]


def field[T](**kwargs: Unpack[FieldKwargs[T]]) -> Field[T]:
    return attrs.field(metadata=kwargs)
