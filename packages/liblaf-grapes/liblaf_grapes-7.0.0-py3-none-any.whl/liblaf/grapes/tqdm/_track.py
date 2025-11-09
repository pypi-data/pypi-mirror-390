from collections.abc import Iterable
from typing import Literal

from liblaf.grapes import timing

from ._progress import Progress


def track[T](
    sequence: Iterable[T],
    total: float | None = None,
    completed: int = 0,
    description: str = "Working...",
    update_period: float = 0.1,
    *,
    progress: Progress | None = None,
    timer: timing.Timer | Literal[False] | None = None,
) -> Iterable[T]:
    __tracebackhide__ = True
    if timer is None:
        timer = timing.timer(name=description)
    if progress is None:
        progress = Progress(timer=timer)
    with progress:
        yield from progress.track(
            sequence,
            total=total,
            completed=completed,
            description=description,
            update_period=update_period,
            timer=timer,
        )
