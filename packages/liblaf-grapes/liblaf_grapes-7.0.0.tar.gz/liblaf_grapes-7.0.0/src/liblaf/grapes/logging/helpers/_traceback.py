import sys
import types
import unittest.mock
from collections.abc import Generator, Iterable
from typing import TypedDict, Unpack, cast

import cytoolz as toolz
from rich.text import Text
from rich.traceback import Traceback

from liblaf.grapes import pretty
from liblaf.grapes.conf import config


class TracebackOptions(TypedDict, total=False):
    width: int | None
    show_locals: bool
    suppress: Iterable[str | types.ModuleType]


def rich_traceback(
    exc_type: type[BaseException],
    exc_value: BaseException,
    traceback: types.TracebackType | None,
    /,
    **kwargs: Unpack[TracebackOptions],
) -> Traceback:
    kwargs = toolz.merge(config.traceback.model_dump(), kwargs)
    kwargs = cast("TracebackOptions", kwargs)
    if kwargs.get("width") is None:
        kwargs["width"] = pretty.get_console(stderr=True).width
    if suppress := kwargs.get("suppress"):
        kwargs["suppress"] = _validate_suppress(suppress)
    traceback = _filter_traceback(traceback)
    # ? dirty hack to avoid long `repr()` output
    # ref: <https://github.com/Textualize/rich/discussions/3774>
    with unittest.mock.patch("rich.pretty.repr", new=pretty.pformat):
        rich_tb: Traceback = Traceback.from_exception(
            exc_type, exc_value, traceback, **kwargs
        )
    # ? dirty hack to support ANSI in exception messages
    for stack in rich_tb.trace.stacks:
        if pretty.has_ansi(stack.exc_value):
            stack.exc_value = Text.from_ansi(stack.exc_value)  # pyright: ignore[reportAttributeAccessIssue]
    return rich_tb


def _filter_traceback(
    traceback: types.TracebackType | None,
) -> types.TracebackType | None:
    if traceback is None:
        return None
    if traceback.tb_frame.f_locals.get("__tracebackhide__"):
        return _filter_traceback(traceback.tb_next)
    traceback.tb_next = _filter_traceback(traceback.tb_next)
    return traceback


def _validate_suppress(
    suppress: Iterable[str | types.ModuleType],
) -> Generator[str | types.ModuleType]:
    for item in suppress:
        yield _validate_suppress_single(item)


def _validate_suppress_single(
    suppress: str | types.ModuleType,
) -> str | types.ModuleType:
    if isinstance(suppress, types.ModuleType):
        return suppress
    return sys.modules.get(suppress, suppress)
