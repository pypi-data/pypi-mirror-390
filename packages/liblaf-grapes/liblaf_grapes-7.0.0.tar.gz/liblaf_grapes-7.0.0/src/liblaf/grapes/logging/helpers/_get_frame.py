import types
import unittest.mock
from collections.abc import Callable, Generator
from pathlib import Path

from loguru._get_frame import load_get_frame_function

from liblaf.grapes.conf import config

from ._traceback import _validate_suppress

_get_frame_original: Callable[[int], types.FrameType | None] = load_get_frame_function()


def _get_frame(depth: int = 0, /) -> types.FrameType | None:
    __tracebackhide__ = True
    frame: types.FrameType | None = _get_frame_original(0)
    while frame is not None:
        if not _should_hide(frame):
            if depth <= 0:
                return frame
            depth -= 1
        frame = frame.f_back
    if frame is None:
        msg = "call stack is not deep enough"
        raise ValueError(msg)
    return frame


def _should_hide(frame: types.FrameType) -> bool:
    if frame.f_locals.get("__tracebackhide__"):
        return True
    file: Path = Path(frame.f_code.co_filename)
    suppressed: bool = any(file.is_relative_to(path) for path in _get_suppress_paths())
    return suppressed


def _get_suppress_paths() -> Generator[Path]:
    suppress = _validate_suppress(config.traceback.suppress)
    for item in suppress:
        if isinstance(item, str):
            yield Path(item)
        else:
            file: str | None = getattr(item, "__file__", None)
            if file is None:
                continue
            yield Path(file).parent


def patch_loguru_get_frame(
    new: Callable[[int], types.FrameType | None] = _get_frame,
) -> None:
    # ! dirty hack
    patcher = unittest.mock.patch("loguru._logger.get_frame", new)
    patcher.start()
