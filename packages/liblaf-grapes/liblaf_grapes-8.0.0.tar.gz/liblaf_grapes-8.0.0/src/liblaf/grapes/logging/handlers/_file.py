from __future__ import annotations

from typing import Unpack

import loguru

from liblaf.grapes import rt
from liblaf.grapes._config import config
from liblaf.grapes.logging.filters import new_filter
from liblaf.grapes.logging.helpers import new_format


def file_handler(
    **kwargs: Unpack[loguru.FileHandlerConfig],
) -> loguru.FileHandlerConfig:
    if "sink" not in kwargs:
        kwargs["sink"] = config.logging.file.get() or rt.entrypoint().with_suffix(
            ".log"
        )
    if "format" not in kwargs:
        kwargs["format"] = new_format()
    kwargs["filter"] = new_filter(kwargs.get("filter"))
    kwargs.setdefault("mode", "w")
    return kwargs
