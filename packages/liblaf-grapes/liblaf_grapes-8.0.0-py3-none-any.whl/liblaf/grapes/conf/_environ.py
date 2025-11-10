import types
import typing
from typing import Any, Protocol

import attrs
from environs import env

from liblaf.grapes.sentinel import MISSING


class EnvGetter(Protocol):
    def __call__(self, name: str, default: Any) -> Any: ...


@attrs.frozen
class Environ:
    _registry: dict[type, EnvGetter] = attrs.field(
        repr=False,
        init=False,
        factory=lambda: {
            int: env.int,
            bool: env.bool,
            str: env.str,
            list: env.list,
            dict: env.dict,
        },
    )

    def get[T](
        self, name: str, default: T | MISSING = MISSING, typ: type[T] | None = None
    ) -> T | MISSING:
        getter: EnvGetter = self._dispatch(typ)
        return getter(name, default)

    def _dispatch(self, typ: type | None) -> EnvGetter:
        if typ is None:
            return env
        getter: EnvGetter | None = self._registry.get(typ)
        if getter is not None:
            return getter
        if isinstance(typ, types.GenericAlias):
            return self._dispatch(typing.get_origin(typ))
        return env


environ = Environ()
