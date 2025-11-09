from __future__ import annotations

import loguru
from loguru import logger


def as_level_no_dict(levels: loguru.FilterDict) -> dict[str | None, int]:
    return {key: get_level_no(value) for key, value in levels.items()}


def get_level_no(level: bool | int | str) -> int:  # noqa: FBT001
    if level is True:
        return 0
    if level is False:
        return 100
    if isinstance(level, int):
        return level
    return logger.level(level).no


def get_parent(name: str) -> str:
    index: int = name.rfind(".")
    return "" if index < 0 else name[:index]
