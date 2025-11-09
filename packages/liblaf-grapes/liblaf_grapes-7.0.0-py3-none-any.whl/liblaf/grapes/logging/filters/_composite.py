from __future__ import annotations

import attrs
import loguru

from ._by_name import FilterByName
from ._by_version import FilterByVersion
from ._once import FilterOnce
from ._utils import get_level_no


@attrs.define
class CompositeFilter:
    by_name: FilterByName = attrs.field(factory=FilterByName)
    by_version: FilterByVersion = attrs.field(factory=FilterByVersion)
    level: int = attrs.field(default="INFO", converter=get_level_no)  # pyright: ignore[reportAssignmentType]
    once: FilterOnce = attrs.field(factory=FilterOnce)

    _cache_key: loguru.Record = attrs.field(default=None, init=False)
    _cache_value: bool = attrs.field(default=False, init=False)

    def __init__(self, by_name: loguru.FilterDict | None = None) -> None:
        if by_name is None:
            by_name = {"__main__": "TRACE"}
        level: bool | int | str = by_name.get("", "INFO")
        self.__attrs_init__(by_name=FilterByName(by_name), level=level)  # pyright: ignore[reportAttributeAccessIssue, reportArgumentType]

    def __call__(self, record: loguru.Record) -> bool:
        if record is self._cache_key:
            return self._cache_value
        result: bool = self._filter(record)
        self._cache_key = record
        self._cache_value = result
        return result

    def get_level(self, name: str | None) -> int | None:
        level: int | None = self.by_name.get_level(name)
        if level is not None:
            return level
        level = self.by_version.get_level(name)
        if level is not None:
            return level
        return None

    def _filter(self, record: loguru.Record) -> bool:
        if not self.once(record):
            return False
        level: int | None = self.get_level(record["name"])
        if level is None:
            level = self.level
        return record["level"].no >= level
