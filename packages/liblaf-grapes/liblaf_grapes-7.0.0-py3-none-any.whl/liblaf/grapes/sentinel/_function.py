from typing import Never


def nop(*args, **kwargs) -> None: ...


def not_implemented(*args, **kwargs) -> Never:
    raise NotImplementedError
