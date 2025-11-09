from __future__ import annotations

import sys
import types
from pathlib import Path

import loguru
from loguru import logger


def setup_excepthook(level: int | str = "CRITICAL") -> None:
    def excepthook(
        exc_type: type[BaseException],
        exc_value: BaseException,
        exc_traceback: types.TracebackType | None,
        /,
    ) -> None:
        logger.opt(exception=(exc_type, exc_value, exc_traceback)).patch(_patcher).log(
            level, exc_value
        )

    sys.excepthook = excepthook


def _patcher(record: loguru.Record) -> None:
    if record["exception"] is None:
        return
    traceback: types.TracebackType | None
    _, _, traceback = record["exception"]
    if traceback is None:
        return
    while traceback.tb_next is not None:
        traceback = traceback.tb_next
    frame: types.FrameType = traceback.tb_frame
    filename: Path = Path(frame.f_code.co_filename)
    record["file"].name = filename.name
    record["file"].path = frame.f_code.co_filename
    record["function"] = frame.f_code.co_name
    record["line"] = frame.f_lineno
    record["module"] = filename.stem
    record["name"] = frame.f_globals.get("__name__", record["name"])
