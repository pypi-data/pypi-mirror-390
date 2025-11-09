from typing import Callable, List, Tuple
from .estimator import estimate_report
import functools

def default_list_maker(n: int) -> Tuple[tuple, dict]:
    import random
    arr = [random.randint(0, 1000) for _ in range(n)]
    return (arr,), {}

def analyze(func: Callable | None = None, *,
            sizes: List[int] | None = None,
            maker: Callable[[int], Tuple[tuple, dict]] | None = None):
    """
    Decorator:
    @analyze() → static only
    @analyze(sizes=[...]) → runtime + static analysis
    """
    def wrapper(real_func: Callable):
        @functools.wraps(real_func)
        def inner(*args, **kwargs):
            return real_func(*args, **kwargs)

        # ✅ Store original function so static analyzer can access it
        inner._original_function = real_func

        # ✅ Attach method to compute complexity
        inner._complexity_estimate = lambda: estimate_report(
            real_func,
            maker if maker else None,
            sizes if sizes else None
        )
        return inner

    return wrapper if func is None else wrapper(func)
