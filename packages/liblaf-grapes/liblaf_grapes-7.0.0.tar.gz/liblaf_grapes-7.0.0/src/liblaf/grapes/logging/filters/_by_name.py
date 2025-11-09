from __future__ import annotations

import attrs
import loguru

from ._utils import as_level_no_dict, get_parent


@attrs.define
class FilterByName:
    _levels: dict[str, int] = attrs.field(
        default=None,
        converter=[
            attrs.converters.default_if_none(factory=lambda: {"__main__": "TRACE"}),
            as_level_no_dict,
        ],
    )  # pyright: ignore[reportAssignmentType]

    def __call__(self, record: loguru.Record) -> bool:
        level: int | None = self.get_level(record["name"])
        if level is None:
            return True
        return record["level"].no >= level

    def get_level(self, name: str | None) -> int | None:
        while True:
            if not name:
                return None
            level: int | None = self._levels.get(name)
            if level is not None:
                return level
            name = get_parent(name)
