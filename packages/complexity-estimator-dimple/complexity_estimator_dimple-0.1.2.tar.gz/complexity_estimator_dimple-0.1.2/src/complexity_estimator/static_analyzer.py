import ast
import inspect
import textwrap
from typing import Dict

class StaticComplexityAnalyzer(ast.NodeVisitor):
    def __init__(self, func_name: str):
        self.func_name = func_name
        self.max_loop_depth = 0
        self.current_loop_depth = 0
        self.has_recursion = False
        self.comp_count = 0
        self.uses_sort = False  # ✅ New: detect sort() or sorted()

    def visit_For(self, node: ast.For):
        self.current_loop_depth += 1
        self.max_loop_depth = max(self.max_loop_depth, self.current_loop_depth)
        self.generic_visit(node)
        self.current_loop_depth -= 1

    def visit_While(self, node: ast.While):
        self.current_loop_depth += 1
        self.max_loop_depth = max(self.max_loop_depth, self.current_loop_depth)
        self.generic_visit(node)
        self.current_loop_depth -= 1

    def visit_ListComp(self, node: ast.ListComp):
        self.comp_count += 1
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        # ✅ Detect recursion
        if isinstance(node.func, ast.Name) and node.func.id == self.func_name:
            self.has_recursion = True

        # ✅ Detect sorting (.sort() or sorted())
        if (
            (isinstance(node.func, ast.Attribute) and node.func.attr == "sort") or
            (isinstance(node.func, ast.Name) and node.func.id == "sorted")
        ):
            self.uses_sort = True

        self.generic_visit(node)


def guess_from_static(loop_depth: int, has_recursion: bool, uses_sort: bool) -> str:
    """Return Big-O based on static structure."""
    if has_recursion:
        return "O(n)"  # basic estimate
    if uses_sort:
        return "O(n log n)"  # ✅ Sorting detected
    if loop_depth == 0:
        return "O(1)"
    if loop_depth == 1:
        return "O(n)"
    if loop_depth == 2:
        return "O(n^2)"
    return "O(n^3)"


def analyze_source(func_obj) -> Dict[str, str]:
    """Analyze time & space complexity statically."""
    # ✅ If function is decorated, unwrap original function
    real_func = getattr(func_obj, "_original_function", func_obj)

    try:
        source = inspect.getsource(real_func)
    except Exception:
        return {
            "time_static": "Unknown",
            "space_static": "Unknown",
            "notes": "Source not found"
        }

    # ✅ Remove indentation
    source = textwrap.dedent(source)
    tree = ast.parse(source)

    analyzer = StaticComplexityAnalyzer(real_func.__name__)
    analyzer.visit(tree)

    # ✅ Use updated logic (now includes sort detection)
    time_guess = guess_from_static(analyzer.max_loop_depth, analyzer.has_recursion, analyzer.uses_sort)

    # Space logic: if loops or sorting exist, assume O(n)
    space_guess = "O(n)" if analyzer.max_loop_depth >= 1 or analyzer.uses_sort else "O(1)"

    return {
        "time_static": time_guess,
        "space_static": space_guess,
        "notes": f"loops:{analyzer.max_loop_depth}, recursion:{analyzer.has_recursion}, sort:{analyzer.uses_sort}, comps:{analyzer.comp_count}"
    }
