import types
from typing import TypedDict, Unpack, cast

import cytoolz as toolz
from rich.text import Text

from liblaf.grapes import pretty
from liblaf.grapes._config import config
from liblaf.grapes.ext.rich.traceback import Traceback


class TracebackOptions(TypedDict, total=False):
    width: int | None


def rich_traceback(
    exc_type: type[BaseException],
    exc_value: BaseException,
    traceback: types.TracebackType | None,
    /,
    **kwargs: Unpack[TracebackOptions],
) -> Traceback:
    kwargs = toolz.merge(config.traceback.get(), kwargs)
    kwargs = cast("TracebackOptions", kwargs)
    # ? dirty hack to avoid long `repr()` output
    # ref: <https://github.com/Textualize/rich/discussions/3774>
    # with unittest.mock.patch("rich.pretty.repr", new=pretty.pformat):
    rich_tb: Traceback = Traceback.from_exception(
        exc_type, exc_value, traceback, **kwargs
    )
    # ? dirty hack to support ANSI in exception messages
    for stack in rich_tb.trace.stacks:
        if pretty.has_ansi(stack.exc_value):
            stack.exc_value = Text.from_ansi(stack.exc_value)  # pyright: ignore[reportAttributeAccessIssue]
    return rich_tb
