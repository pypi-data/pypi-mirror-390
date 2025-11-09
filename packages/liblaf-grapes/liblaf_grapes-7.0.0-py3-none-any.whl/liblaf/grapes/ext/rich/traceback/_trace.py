import dataclasses

from rich.traceback import Trace as RichTrace

from ._stack import Stack


@dataclasses.dataclass
class Trace(RichTrace):
    stacks: list[Stack]  # pyright: ignore[reportIncompatibleVariableOverride]
