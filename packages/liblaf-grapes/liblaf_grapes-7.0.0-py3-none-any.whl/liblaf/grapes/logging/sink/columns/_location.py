from __future__ import annotations

import sys
import types
from typing import override

import attrs
import loguru
from rich.console import RenderableType
from rich.text import Text

from liblaf.grapes import pretty

from ._abc import RichSinkColumn


@attrs.define
class RichSinkColumnLocation(RichSinkColumn):
    abbr_name: bool = True
    enable_link: bool = True
    width: int | None = None

    @override  # impl RichSinkColumn
    def render(self, record: loguru.Record, /) -> RenderableType:
        name: str | None = self.render_name(record)
        location: Text = pretty.rich_location(
            name=name,
            function=record["function"],
            line=record["line"],
            file=record["file"].path,
            enable_link=self.enable_link,
            width=self.width,
        )
        location.style = "log.path"
        return location

    def render_name(self, record: loguru.Record) -> str | None:
        name: str | None = record["name"]
        if name is None:
            return None
        if not self.abbr_name:
            return name
        function: str = record["function"]
        start: int = 0
        while True:
            index: int = name.find(".", start)
            if index < 0:
                return name
            module_name: str = name[:index]
            module: types.ModuleType | None = sys.modules.get(module_name)
            if module is None:
                return name
            if hasattr(module, function):
                return module_name
            start = index + 1
