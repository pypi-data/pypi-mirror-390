from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Any

import loguru
from loguru import logger

from liblaf.grapes._config import config
from liblaf.grapes.typing import PathLike

from .filters import FilterLike
from .handlers import file_handler, rich_handler
from .helpers import (
    patch_loguru_get_frame,
    setup_excepthook,
    setup_icecream,
    setup_loguru_intercept,
    setup_unraisablehook,
)


def init(
    *,
    file: PathLike | None = None,
    filter: FilterLike = None,  # noqa: A002
    handlers: Sequence[loguru.HandlerConfig] | None = None,
    intercept: Iterable[str] = (),
    level: int | str | None = None,
    link: bool = False,
    time: bool | None = None,
) -> None:
    if file is None:
        file = config.logging.file.get()
    if level is None:
        level = config.logging.level.get()

    if handlers is None:
        handler_config: dict[str, Any] = {}
        if filter is not None:
            handler_config["filter"] = filter
        if level is not None:
            handler_config["level"] = level
        handlers: list[loguru.HandlerConfig] = [
            rich_handler(**handler_config, enable_link=link, time=time)
        ]
        if file:
            handlers.append(file_handler(sink=file, **handler_config))

    patch_loguru_get_frame()
    logger.configure(handlers=handlers)
    setup_excepthook()
    setup_icecream()
    setup_loguru_intercept(intercept)
    setup_unraisablehook()
