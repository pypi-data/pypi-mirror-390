import argparse
import importlib.util
import sys
from .estimator import estimate_report

def _load_function(file_path: str, func_name: str):
    """
    Load a function or class method from a Python file.

    Supports:
    - normal_function
    - ClassName.methodName
    """
    spec = importlib.util.spec_from_file_location("user_module", file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["user_module"] = module
    spec.loader.exec_module(module)

    # ✅ If it’s a class method (e.g. Solution.findMedianSortedArrays)
    if "." in func_name:
        class_name, method_name = func_name.split(".")
        cls = getattr(module, class_name)
        instance = cls()   # create object of the class
        func = getattr(instance, method_name)
    else:
        func = getattr(module, func_name)

    return func, module


def main():
    parser = argparse.ArgumentParser(description="Estimate time/space complexity of a Python function or class method.")
    parser.add_argument("file", help="Path to Python file")
    parser.add_argument("function", help="Function or ClassName.methodName")
    parser.add_argument("--sizes", nargs="+", type=int, default=[50, 100, 200, 400],
                        help="Input sizes to test")
    parser.add_argument("--no-run", action="store_true",
                        help="Only do static analysis (skip runtime)")
    args = parser.parse_args()

    func, module = _load_function(args.file, args.function)

    # ✅ Generate correct types of inputs based on number of parameters
    def default_maker(n: int):
        import random, inspect
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())

        # If function takes 2 arguments → return two lists (like LeetCode problems)
        if len(params) >= 2:
            arr1 = [random.randint(0, 10000) for _ in range(n)]
            arr2 = [random.randint(0, 10000) for _ in range(n)]
            return (arr1, arr2), {}

        # If function takes 1 argument → return a single list
        elif len(params) == 1:
            arr = [random.randint(0, 10000) for _ in range(n)]
            return (arr,), {}

        # If no params, just return number n
        else:
            return (n,), {}

    if args.no_run:
        report = estimate_report(func)
    else:
        report = estimate_report(func, maker=default_maker, sizes=args.sizes)

    print("=== Complexity Estimate ===")
    print(f"Time:  {report['time_estimate']}")
    print(f"Space: {report['space_estimate']}")

    print("\n-- Static Hints --")
    for k, v in report["static"].items():
        print(f"{k}: {v}")

    if report["runtime"]:
        print("\n-- Runtime Profile --")
        print("sizes      :", report['runtime']['sizes'])
        print("times (s)  :", [round(time, 6) for time in report['runtime']['times']])
        print("mem (bytes):", report['runtime']['mem_bytes'])
        print(f"time_runtime: {report['runtime']['time_runtime']} (conf {report['runtime']['time_runtime_confidence']})")
        print(f"space_runtime: {report['runtime']['space_runtime']} (conf {report['runtime']['space_runtime_confidence']})")


if __name__ == "__main__":
    main()
