from collections.abc import Iterable
from typing import Literal, override

from rich.console import Console, RenderableType
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    ProgressColumn,
    SpinnerColumn,
    Task,
    TaskID,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.progress import Progress as RichProgress
from rich.table import Column
from rich.text import Text

from liblaf.grapes import itertools as _it
from liblaf.grapes import pretty, timing


class RateColumn(ProgressColumn):
    unit: str = "it"

    def __init__(self, unit: str = "it", table_column: Column | None = None) -> None:
        super().__init__(table_column)
        self.unit = unit

    def render(self, task: Task) -> RenderableType:
        if not task.speed:
            return Text(f"?{self.unit}/s", style="progress.data.speed")
        throughput: str = pretty.pretty_throughput(task.speed, self.unit)
        return Text(throughput, style="progress.data.speed")


class Progress(RichProgress):
    timer: timing.Timer | Literal[False]

    def __init__(
        self,
        *columns: str | ProgressColumn,
        console: Console | None = None,
        timer: timing.Timer | Literal[False] | None = None,
    ) -> None:
        if console is None:
            console = pretty.get_console(stderr=True)
        super().__init__(*columns, console=console)
        if timer is None:
            timer = timing.timer()
        self.timer = timer

    @override
    @classmethod
    def get_default_columns(cls) -> tuple[str | ProgressColumn, ...]:  # pyright: ignore[reportIncompatibleMethodOverride]
        return (
            SpinnerColumn(),
            TextColumn("{task.description}", style="progress.description"),
            BarColumn(),
            TaskProgressColumn(),
            MofNCompleteColumn(),
            "[",
            TimeElapsedColumn(),
            "<",
            TimeRemainingColumn(),
            ",",
            RateColumn(),
            "]",
        )

    @override
    def track[T](
        self,
        sequence: Iterable[T],
        total: float | None = None,
        completed: int = 0,
        task_id: TaskID | None = None,
        description: str = "Working...",
        update_period: float = 0.1,
        *,
        timer: timing.Timer | Literal[False] | None = None,
    ) -> Iterable[T]:
        __tracebackhide__ = True
        if total is None:
            total = _it.len_or_none(sequence)
        if timer := (timer or self.timer):
            sequence = timer(sequence)
            timing.get_timer(sequence).label = description
        yield from super().track(
            sequence,
            total=total,
            completed=completed,
            task_id=task_id,
            description=description,
            update_period=update_period,
        )
