"""
An LRU cache with a time-to-live (TTL) feature.

Source: https://towardsdatascience.com/implement-a-cache-decorator-with-ttl-feature-in-python-1d6969b7ca3f

Usage:

```
@ttl_cache(maxsize=128, ttl=40)
def total_count(n):
    result = 0
    for _ in range(n):
        result += n
    return result
```

"""
from functools import lru_cache, update_wrapper
from typing import Callable, Any
from math import floor
import time


def ttl_cache(maxsize: int = 128, typed: bool = False, ttl: int = -1):
    if ttl <= 0:
        ttl = 65536

    hash_gen = _ttl_hash_gen(ttl)

    def wrapper(func: Callable) -> Callable:
        @lru_cache(maxsize, typed)
        def ttl_func(ttl_hash,  *args, **kwargs):
            return func(*args, **kwargs)

        def wrapped(*args, **kwargs) -> Any:
            th = next(hash_gen)
            return ttl_func(th, *args, **kwargs)
        return update_wrapper(wrapped, func)
    return wrapper


def _ttl_hash_gen(seconds: int):
    start_time = time.time()

    while True:
        yield floor((time.time() - start_time) / seconds)