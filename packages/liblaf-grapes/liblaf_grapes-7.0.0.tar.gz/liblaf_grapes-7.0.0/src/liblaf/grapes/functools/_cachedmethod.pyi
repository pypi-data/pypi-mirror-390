import contextlib
import threading
from collections.abc import Callable, MutableMapping
from typing import Any

def cachedmethod[C: Callable, KT](
    factory: Callable[[], MutableMapping[KT, Any] | None],
    key: Callable[..., KT] = ...,
    lock: Callable[[Any], contextlib.AbstractContextManager[Any]] | None = None,
    condition: threading.Condition | None = None,
) -> Callable[[C], C]: ...
