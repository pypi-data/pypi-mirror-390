import dataclasses
import itertools
import types
from typing import Self

import rich
import rich.pretty
import rich.scope
from rich.pretty import Node
from rich.traceback import LOCALS_MAX_LENGTH, LOCALS_MAX_STRING
from rich.traceback import Frame as RichFrame

from liblaf.grapes import rt


@dataclasses.dataclass
class Frame(RichFrame):
    function: str = dataclasses.field(kw_only=True)
    hide: bool = False

    @classmethod
    def extract(
        cls,
        frame: types.FrameType,
        lineno: int,
        *,
        show_locals: bool = True,
        locals_max_length: int = LOCALS_MAX_LENGTH,
        locals_max_string: int = LOCALS_MAX_STRING,
        locals_hide_dunder: bool = True,
        locals_hide_sunder: bool = True,
    ) -> Self:
        self: Self = cls(
            filename=frame.f_code.co_filename,
            lineno=lineno,
            name=frame.f_globals.get("__name__", "<unknown>"),
            locals=None,
            last_instruction=None,
            function=frame.f_code.co_name,
            hide=cls._extract_traceback_hide(frame),
        )
        if self.hide:
            return self
        self.last_instruction = cls._extract_last_instruction(frame)
        if show_locals:
            self.locals = cls._extract_locals(
                frame,
                locals_max_length=locals_max_length,
                locals_max_string=locals_max_string,
                locals_hide_dunder=locals_hide_dunder,
                locals_hide_sunder=locals_hide_sunder,
            )
        return self

    @classmethod
    def _extract_last_instruction(
        cls,
        frame: types.FrameType,
    ) -> tuple[tuple[int, int], tuple[int, int]] | None:
        instruction_index: int = frame.f_lasti // 2
        start_line: int | None
        end_line: int | None
        start_column: int | None
        end_column: int | None
        start_line, end_line, start_column, end_column = next(
            itertools.islice(
                frame.f_code.co_positions(),
                instruction_index,
                instruction_index + 1,
            )
        )
        if (
            start_line is not None
            and end_line is not None
            and start_column is not None
            and end_column is not None
        ):
            return ((start_line, start_column), (end_line, end_column))
        return None

    @classmethod
    def _extract_locals(
        cls,
        frame: types.FrameType,
        *,
        locals_max_length: int = LOCALS_MAX_LENGTH,
        locals_max_string: int = LOCALS_MAX_STRING,
        locals_hide_dunder: bool = True,
        locals_hide_sunder: bool = True,
    ) -> dict[str, Node]:
        result: dict[str, Node] = {}
        for key, value in frame.f_locals.items():
            if locals_hide_dunder and key.startswith("__"):
                continue
            if locals_hide_sunder and key.startswith("_") and not key.startswith("__"):
                continue
            result[key] = rich.pretty.traverse(
                value, max_length=locals_max_length, max_string=locals_max_string
            )
        return result

    @classmethod
    def _extract_traceback_hide(cls, frame: types.FrameType) -> bool:
        for name in ("__traceback_hide__", "__tracebackhide__"):
            if frame.f_locals.get(name, False):
                return True
        return not rt.is_pre_release(
            file=frame.f_code.co_filename, name=frame.f_globals.get("__name__", None)
        )
