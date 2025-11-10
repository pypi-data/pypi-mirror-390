import linecache
import types
from collections.abc import Iterable
from typing import Self, override

import rich.console
from rich.console import ConsoleRenderable, RenderResult
from rich.scope import render_scope
from rich.syntax import Syntax
from rich.text import Text
from rich.traceback import LOCALS_MAX_LENGTH, LOCALS_MAX_STRING, _iter_syntax_lines
from rich.traceback import Traceback as RichTraceback

from liblaf.grapes import rt

from ._frame import Frame
from ._stack import Stack
from ._trace import Trace


class Traceback(RichTraceback):
    @override
    @classmethod
    def extract(
        cls,
        exc_type: type[BaseException],
        exc_value: BaseException,
        traceback: types.TracebackType | None,
        *,
        show_locals: bool = False,
        locals_max_length: int = LOCALS_MAX_LENGTH,
        locals_max_string: int = LOCALS_MAX_STRING,
        locals_hide_dunder: bool = True,
        locals_hide_sunder: bool = False,
        _visited_exceptions: set[BaseException] | None = None,
    ) -> Trace:
        if _visited_exceptions is None:
            _visited_exceptions = set()
        stacks: list[Stack] = list(
            Stack.extract(
                exc_type,
                exc_value,
                traceback,
                show_locals=show_locals,
                locals_max_length=locals_max_length,
                locals_max_string=locals_max_string,
                locals_hide_dunder=locals_hide_dunder,
                locals_hide_sunder=locals_hide_sunder,
                _visited_exceptions=_visited_exceptions,
                is_cause=False,
                traceback_cls=cls,
            )
        )
        return Trace(stacks=stacks)

    @override
    @classmethod
    def from_exception(
        cls,
        exc_type: type[BaseException],
        exc_value: BaseException,
        traceback: types.TracebackType | None,
        *,
        width: int | None = None,
        code_width: int | None = 88,
        extra_lines: int = 1,
        theme: str | None = None,
        word_wrap: bool = False,
        show_locals: bool = True,
        locals_max_length: int = LOCALS_MAX_LENGTH,
        locals_max_string: int = LOCALS_MAX_STRING,
        locals_hide_dunder: bool = True,
        locals_hide_sunder: bool = True,
        indent_guides: bool = True,
        suppress: Iterable[str | types.ModuleType] = (),
        max_frames: int = 100,
    ) -> Self:
        return super().from_exception(
            exc_type,
            exc_value,
            traceback,
            width=width,
            code_width=code_width,
            extra_lines=extra_lines,
            theme=theme,
            word_wrap=word_wrap,
            show_locals=show_locals,
            locals_max_length=locals_max_length,
            locals_max_string=locals_max_string,
            locals_hide_dunder=locals_hide_dunder,
            locals_hide_sunder=locals_hide_sunder,
            indent_guides=indent_guides,
            suppress=suppress,
            max_frames=max_frames,
        )  # pyright: ignore[reportReturnType]

    def _render_frame(self, frame: Frame) -> RenderResult:
        location: Text = Text.assemble(
            (rt.abbr_path(frame.filename), "pygments.string"),
            (":", "pygments.text"),
            (str(frame.lineno), "pygments.number"),
            (" in ", "pygments.text"),
            (frame.function + "()", "pygments.function"),
        )
        if frame.hide:
            location.append(" --- hidden")
            location.stylize("dim")
        yield location
        if frame.hide:
            return
        try:
            syntax: Syntax | None = self._render_syntax(frame)
        except Exception as err:
            if isinstance(err, (KeyboardInterrupt, SystemExit)):
                raise
            yield Text(f"{err}", "traceback.error")
        else:
            if syntax is not None:
                yield syntax
        yield from self._render_locals(frame)

    def _render_locals(self, frame: Frame) -> Iterable[ConsoleRenderable]:
        if not frame.locals:
            return
        yield render_scope(
            frame.locals,
            title="locals",
            indent_guides=self.indent_guides,
            max_length=self.locals_max_length,
            max_string=self.locals_max_string,
        )

    @override
    @rich.console.group()
    def _render_stack(self, stack: Stack) -> RenderResult:
        exclude_start: int
        exclude_end: int
        if self.max_frames != 0:
            exclude_start: int = self.max_frames // 2
            exclude_end: int = len(stack.frames) - self.max_frames // 2
        else:
            exclude_start = 0
            exclude_end = 0
        for frame_idx, frame in enumerate(stack.frames):
            if exclude_start <= frame_idx < exclude_end:
                if frame_idx == exclude_start:
                    yield Text(
                        f"\n...{exclude_end - exclude_start} frames hidden...",
                        style="traceback.error",
                        justify="center",
                    )
                continue
            yield from self._render_frame(frame)

    def _render_syntax(self, frame: Frame) -> Syntax | None:
        code_lines: list[str] = linecache.getlines(frame.filename)
        code: str = "".join(code_lines)
        if not code:
            return None
        lexer: str = self._guess_lexer(frame.filename, code)
        syntax = Syntax(
            code,
            lexer,
            theme=self.theme,
            dedent=False,
            line_numbers=True,
            line_range=(
                frame.lineno - self.extra_lines,
                frame.lineno + self.extra_lines,
            ),
            highlight_lines={frame.lineno},
            code_width=self.code_width,
            word_wrap=self.word_wrap,
            indent_guides=self.indent_guides,
        )
        if frame.last_instruction is not None:
            start: tuple[int, int]
            end: tuple[int, int]
            start, end = frame.last_instruction
            # Stylize a line at a time
            # So that indentation isn't underlined (which looks bad)
            for line1, column1, column2 in _iter_syntax_lines(start, end):
                try:
                    if column1 == 0:
                        line: str = code_lines[line1 - 1]
                        column1: int = len(line) - len(line.lstrip())  # noqa: PLW2901
                    if column2 == -1:
                        column2: int = len(code_lines[line1 - 1])  # noqa: PLW2901
                except IndexError:
                    # Being defensive here
                    # If last_instruction reports a line out-of-bounds, we don't want to crash
                    continue
                syntax.stylize_range(
                    style="traceback.error_range",
                    start=(line1, column1),
                    end=(line1, column2),
                )
        return syntax
