from __future__ import annotations

from collections.abc import Sequence
from typing import Unpack

import loguru
from rich.console import Console

from liblaf.grapes.logging.filters import new_filter
from liblaf.grapes.logging.sink import RichSink, RichSinkColumn


def rich_handler(
    columns: Sequence[RichSinkColumn] | None = None,
    console: Console | None = None,
    *,
    enable_link: bool = True,
    time: bool | None = None,
    **kwargs: Unpack[loguru.BasicHandlerConfig],
) -> loguru.BasicHandlerConfig:
    kwargs["sink"] = RichSink(
        console=console, columns=columns, link=enable_link, time=time
    )
    kwargs["format"] = ""
    kwargs["filter"] = new_filter(kwargs.get("filter"))
    return kwargs
