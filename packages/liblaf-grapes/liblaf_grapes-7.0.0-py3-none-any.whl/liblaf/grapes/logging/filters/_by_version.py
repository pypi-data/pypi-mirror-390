from __future__ import annotations

import contextlib
import sys
import types
from collections.abc import Hashable
from typing import Any

import attrs
import cachetools
import loguru
import packaging.version

from ._utils import get_level_no, get_parent


@attrs.define
class FilterByVersion:
    level_dev: int = attrs.field(default="TRACE", converter=get_level_no)  # pyright: ignore[reportAssignmentType]
    level_prerelease: int = attrs.field(default="DEBUG", converter=get_level_no)  # pyright: ignore[reportAssignmentType]
    _get_version_cache: cachetools.Cache[Hashable, packaging.version.Version | None] = (
        attrs.field(factory=lambda: cachetools.LRUCache(maxsize=128))
    )

    def __call__(self, record: loguru.Record) -> bool:
        level: int | None = self.get_level(record["name"])
        if level is None:
            return True
        return record["level"].no >= level

    def get_level(self, name: str | None) -> int | None:
        version: packaging.version.Version | None = self._get_version(name)
        if version is None:
            return None
        if version.is_devrelease:
            return self.level_dev
        if version.is_prerelease:
            return self.level_prerelease
        return None

    def _get_version(self, name: str | None) -> packaging.version.Version | None:
        if not name:
            return None
        module: types.ModuleType | None = sys.modules.get(name)
        if module is not None:
            version: Any = getattr(module, "__version__", None)
            if isinstance(version, tuple):
                with contextlib.suppress(TypeError):
                    version = ".".join(str(part) for part in version)
            if isinstance(version, str):
                try:
                    version = packaging.version.parse(version)
                except packaging.version.InvalidVersion:
                    pass
                else:
                    return version
        name = get_parent(name)
        return self._get_version(name)
