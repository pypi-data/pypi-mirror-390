from __future__ import annotations

from collections.abc import Hashable

import attrs
import loguru


@attrs.define
class FilterOnce:
    _history: set[Hashable] = attrs.field(factory=set, init=False)

    def __call__(self, record: loguru.Record) -> bool:
        if not record["extra"].get("once", False):
            return True
        record_hash: Hashable = self._hash_record(record)
        if record_hash in self._history:
            return False
        self._history.add(record_hash)
        return True

    def _hash_record(self, record: loguru.Record) -> Hashable:
        return (
            record["function"],
            record["level"].no,
            record["line"],
            record["message"],
            record["name"],
        )
