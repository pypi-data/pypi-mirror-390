import time
import tracemalloc
from math import log
from typing import Callable, List, Tuple, Dict, Any

def _safe_log(x: float) -> float:
    return log(max(1.0000001, x))

def _candidate_funcs(n: int) -> Dict[str, float]:
    # candidate growth families (no numpy needed)
    return {
        "O(1)": 1.0,
        "O(log n)": _safe_log(n),
        "O(n)": float(n),
        "O(n log n)": float(n) * _safe_log(n),
        "O(n^2)": float(n) ** 2,
        "O(n^3)": float(n) ** 3,
    }

def _best_fit(ns: List[int], ys: List[float]) -> Tuple[str, float]:
    """
    Simple least-squares fit: y ≈ a * f(n).
    For each candidate f(n), compute a and residual error; choose the smallest error.
    Returns (label, confidence in [0..1]).
    """
    best_label = "O(1)"
    best_err = float("inf")

    for label in ["O(1)", "O(log n)", "O(n)", "O(n log n)", "O(n^2)", "O(n^3)"]:
        fvals = [_candidate_funcs(n)[label] for n in ns]
        denom = sum(v*v for v in fvals) or 1e-12
        a = sum(y*v for y, v in zip(ys, fvals)) / denom
        preds = [a * v for v in fvals]
        err = sum((y - p) ** 2 for y, p in zip(ys, preds))
        if err < best_err:
            best_err = err
            best_label = label

    # crude confidence: compare best vs next-best
    errs = []
    for label in ["O(1)", "O(log n)", "O(n)", "O(n log n)", "O(n^2)", "O(n^3)"]:
        fvals = [_candidate_funcs(n)[label] for n in ns]
        denom = sum(v*v for v in fvals) or 1e-12
        a = sum(y*v for y, v in zip(ys, fvals)) / denom
        preds = [a * v for v in fvals]
        err = sum((y - p) ** 2 for y, p in zip(ys, preds))
        errs.append((err, label))
    errs.sort()
    if len(errs) >= 2:
        best, second = errs[0][0], errs[1][0]
        conf = 1.0 - min(1.0, best / (second + 1e-12))
    else:
        conf = 0.5

    return best_label, max(0.0, min(1.0, conf))

def _measure_once(func: Callable, maker: Callable[[int], Tuple[tuple, dict]], n: int) -> Tuple[float, int]:
    """
    maker(n) must return (args_tuple, kwargs_dict) to call func(*args, **kwargs).
    Tracks wall time and peak memory in bytes via tracemalloc.
    """
    args, kwargs = maker(n)

    tracemalloc.start()
    t0 = time.perf_counter()
    func(*args, **kwargs)
    t1 = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    elapsed = max(1e-9, t1 - t0)
    return elapsed, peak

def profile_function(func: Callable, maker: Callable[[int], Tuple[tuple, dict]],
                     sizes: List[int]) -> Dict[str, Any]:
    times: List[float] = []
    mems: List[int] = []

    for n in sizes:
        # warm-up once for stability
        _measure_once(func, maker, max(1, min(n, sizes[0])))
        elapsed, peak = _measure_once(func, maker, n)
        times.append(elapsed)
        mems.append(peak)

    time_class, time_conf = _best_fit(sizes, times)
    space_class, space_conf = _best_fit(sizes, [float(m) for m in mems])

    return {
        "sizes": sizes,
        "times": times,
        "mem_bytes": mems,
        "time_runtime": time_class,
        "time_runtime_confidence": round(time_conf, 2),
        "space_runtime": space_class,
        "space_runtime_confidence": round(space_conf, 2),
    }
