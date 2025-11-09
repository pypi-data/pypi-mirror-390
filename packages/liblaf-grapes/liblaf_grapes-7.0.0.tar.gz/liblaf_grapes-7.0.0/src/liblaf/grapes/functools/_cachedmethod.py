from collections.abc import Callable

import cachetools


def cachedmethod[C: Callable](
    factory: Callable[[], cachetools.Cache], *args, **kwargs
) -> Callable[[C], C]:
    def wrapper(func: C) -> C:
        def cache(self: object) -> cachetools.Cache:
            cache_name: str = f"_{func.__name__}_cache"
            if not hasattr(self, cache_name):
                setattr(self, cache_name, factory())
            return getattr(self, cache_name)

        return cachetools.cachedmethod(cache, *args, **kwargs)(func)

    return wrapper
