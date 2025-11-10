from __future__ import annotations

import attrs
import loguru

from liblaf.grapes import rt

from ._utils import get_level_no


@attrs.define
class FilterByVersion:
    level_dev: int = attrs.field(default=get_level_no("TRACE"), converter=get_level_no)
    level_pre: int = attrs.field(default=get_level_no("DEBUG"), converter=get_level_no)

    def __call__(self, record: loguru.Record) -> bool:
        level: int | None = self.get_level(record)
        if level is None:
            return True
        return record["level"].no >= level

    def get_level(self, record: loguru.Record) -> int | None:
        file: str = record["file"].path
        name: str | None = record["name"]
        if rt.is_dev_release(file, name):
            return self.level_dev
        if rt.is_pre_release(file, name):
            return self.level_pre
        return None
