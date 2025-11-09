from typing import Callable, Dict, Any, List
from .static_analyzer import analyze_source
from .runtime_profiler import profile_function

def combine(static_guess: str, runtime_guess: str) -> str:
    if static_guess == runtime_guess:
        return f"{runtime_guess} (high agreement)"
    return f"{runtime_guess} (runtime) vs {static_guess} (static)"

def estimate_report(func: Callable,
                    maker: Callable[[int], tuple] | None = None,
                    sizes: List[int] | None = None) -> Dict[str, Any]:
    """
    Estimate time & space with both static + runtime signals.
    - func: function to analyze
    - maker: function n -> (args, kwargs). If None, we try a default for list-arg functions.
    - sizes: increasing sizes (e.g., [50, 100, 200, 400])
    """
    if sizes is None:
        sizes = [50, 100, 200, 400]

    static = analyze_source(func)

    runtime = {}
    if maker is not None:
        runtime = profile_function(func, maker, sizes)

    result = {
        "time_estimate": combine(static["time_static"], runtime.get("time_runtime", static["time_static"])) if runtime else static["time_static"],
        "space_estimate": combine(static["space_static"], runtime.get("space_runtime", static["space_static"])) if runtime else static["space_static"],
        "static": static,
        "runtime": runtime
    }
    return result
