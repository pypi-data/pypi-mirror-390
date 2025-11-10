from __future__ import annotations

import attrs
import loguru

from ._utils import as_level_no_dict


@attrs.define
class FilterByName:
    _levels: dict[str | None, int] = attrs.field(
        converter=as_level_no_dict,
        factory=lambda: as_level_no_dict({"__main__": "TRACE"}),
    )

    def __call__(self, record: loguru.Record) -> bool:
        level: int | None = self.get_level(record)
        if level is None:
            return True
        return record["level"].no >= level

    def get_level(self, record: loguru.Record) -> int | None:
        name: str | None = record["name"]
        while True:
            if not name:
                return None
            level: int | None = self._levels.get(name)
            if level is not None:
                return level
            name = _get_parent(name)


def _get_parent(name: str) -> str:
    index: int = name.rfind(".")
    return "" if index < 0 else name[:index]
