from functools import _lru_cache_wrapper
from .core import _solve_name, _get_type_hints
from .action import _method_1st_arg
from .shash import _code

caches: list[_lru_cache_wrapper] = [
    _solve_name,
    _get_type_hints,
    _method_1st_arg,
    _code,
]


def clear():
    for cache in caches:
        cache.cache_clear()
