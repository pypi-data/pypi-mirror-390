from __future__ import annotations

import dataclasses
import types
from collections.abc import Generator
from traceback import walk_tb
from typing import TYPE_CHECKING, Self

from rich.traceback import LOCALS_MAX_LENGTH, LOCALS_MAX_STRING, _SyntaxError
from rich.traceback import Stack as RichStack

from ._frame import Frame

if TYPE_CHECKING:
    from ._traceback import Traceback


@dataclasses.dataclass
class Stack(RichStack):
    frames: list[Frame] = dataclasses.field(default_factory=list)  # pyright: ignore[reportIncompatibleVariableOverride]

    @classmethod
    def extract(
        cls,
        exc_type: type[BaseException],
        exc_value: BaseException,
        traceback: types.TracebackType | None,
        *,
        show_locals: bool = True,
        locals_max_length: int = LOCALS_MAX_LENGTH,
        locals_max_string: int = LOCALS_MAX_STRING,
        locals_hide_dunder: bool = True,
        locals_hide_sunder: bool = True,
        _visited_exceptions: set[BaseException],
        # custom parameters
        is_cause: bool = False,
        traceback_cls: type[Traceback],
    ) -> Generator[Self]:
        notes: list[str] = getattr(exc_value, "__notes__", [])
        stack: Self = cls(
            exc_type=exc_type.__name__,
            exc_value=str(exc_value),
            is_cause=is_cause,
            notes=notes,
        )
        if isinstance(exc_value, (BaseExceptionGroup, ExceptionGroup)):
            stack.is_group = True
            for exception in exc_value.exceptions:
                if exception in _visited_exceptions:
                    continue
                _visited_exceptions.add(exception)
                stack.exceptions.append(
                    traceback_cls.extract(
                        type(exception),
                        exception,
                        exception.__traceback__,
                        show_locals=show_locals,
                        locals_max_length=locals_max_length,
                        locals_max_string=locals_max_string,
                        locals_hide_dunder=locals_hide_dunder,
                        locals_hide_sunder=locals_hide_sunder,
                        _visited_exceptions=_visited_exceptions,
                    )
                )
        elif isinstance(exc_value, SyntaxError):
            stack.syntax_error = _SyntaxError(
                offset=exc_value.offset or 0,
                filename=exc_value.filename or "?",
                lineno=exc_value.lineno or 0,
                line=exc_value.text or "",
                msg=exc_value.msg,
                notes=notes,
            )
        for frame, lineno in walk_tb(traceback):
            stack.frames.append(
                Frame.extract(
                    frame,
                    lineno,
                    show_locals=show_locals,
                    locals_max_length=locals_max_length,
                    locals_max_string=locals_max_string,
                    locals_hide_dunder=locals_hide_dunder,
                    locals_hide_sunder=locals_hide_sunder,
                )
            )
        yield stack
        if not _visited_exceptions:
            cause: BaseException | None = exc_value.__cause__
            if cause is not None and cause is not exc_value:
                yield from cls.extract(
                    type(cause),
                    cause,
                    cause.__traceback__,
                    show_locals=show_locals,
                    locals_max_length=locals_max_length,
                    locals_max_string=locals_max_string,
                    locals_hide_dunder=locals_hide_dunder,
                    locals_hide_sunder=locals_hide_sunder,
                    _visited_exceptions=_visited_exceptions,
                    is_cause=True,
                    traceback_cls=traceback_cls,
                )
            cause = exc_value.__context__
            if cause is not None and not exc_value.__suppress_context__:
                yield from cls.extract(
                    type(cause),
                    cause,
                    cause.__traceback__,
                    show_locals=show_locals,
                    locals_max_length=locals_max_length,
                    locals_max_string=locals_max_string,
                    locals_hide_dunder=locals_hide_dunder,
                    locals_hide_sunder=locals_hide_sunder,
                    _visited_exceptions=_visited_exceptions,
                    is_cause=False,
                    traceback_cls=traceback_cls,
                )
