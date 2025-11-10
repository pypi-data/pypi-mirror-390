from __future__ import annotations

from typing import override

import loguru
from rich.console import RenderableType
from rich.text import AlignMethod, Text

from ._abc import RichSinkColumn


class RichSinkColumnLevel(RichSinkColumn):
    align: AlignMethod = "left"
    icon: bool = False
    width: int = 1

    @override  # impl RichSinkColumn
    def render(self, record: loguru.Record, /) -> RenderableType:
        level: str = record["level"].icon if self.icon else record["level"].name
        text = Text(level, style=f"logging.level.{level.lower()}")
        text.align("left", 2 if self.icon else self.width)
        return text
