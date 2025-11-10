import contextlib
from collections.abc import Generator, Mapping
from typing import Any, Self

import attrs
import cytoolz as toolz

from ._field import Field


class BaseConfigMeta(type):
    def __new__[T: type](
        mcs: type[T],
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        /,
        **kwargs: Any,
    ) -> T:
        cls: T = super().__new__(mcs, name, bases, namespace)
        if "__attrs_attrs__" in namespace:
            return cls
        kwargs.setdefault("frozen", True)
        kwargs.setdefault("init", False)
        cls = attrs.define(cls, **kwargs)
        return cls


class BaseConfig(metaclass=BaseConfigMeta):
    def __init__(self, name: str = "") -> None:
        kwargs: dict[str, Any] = {}
        cls: type[BaseConfig] = type(self)
        cls = attrs.resolve_types(cls)
        for f in attrs.fields(type(self)):
            f: attrs.Attribute
            if not isinstance(f.type, type):
                continue
            name: str = f"{name}.{f.name}" if name else f.name
            if issubclass(f.type, BaseConfig):
                kwargs[f.name] = f.type(name)
            elif issubclass(_unwrap(f.type), Field):
                kwargs[f.name] = f.type(name, **f.metadata)
        self.__attrs_init__(**kwargs)  # pyright: ignore[reportAttributeAccessIssue]

    def get(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for f in attrs.fields(type(self)):
            f: attrs.Attribute
            value: Any = getattr(self, f.name)
            if isinstance(value, (BaseConfig, Field)):
                result[f.name] = value.get()
        return result

    def set(self, changes: Mapping[str, Any] = {}, /, **kwargs: Any) -> None:
        changes = toolz.merge(changes, kwargs)
        for key, value in changes.items():
            field: BaseConfig | Field = getattr(self, key)
            field.set(value)

    @contextlib.contextmanager
    def overrides(
        self, changes: Mapping[str, Any] = {}, /, **kwargs: Any
    ) -> Generator[Self]:
        changes = toolz.merge(changes, kwargs)
        with contextlib.ExitStack() as stack:
            for key, value in changes.items():
                field: BaseConfig | Field = getattr(self, key)
                stack.enter_context(field.overrides(value))
            yield self


def _unwrap(obj: Any) -> Any:
    return getattr(obj, "__wrapped__", obj)
