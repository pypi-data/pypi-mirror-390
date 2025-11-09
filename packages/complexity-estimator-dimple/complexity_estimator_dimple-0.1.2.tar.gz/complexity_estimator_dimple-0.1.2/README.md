# complexity-estimator

Estimate (not prove) Big-O time & space complexity of Python functions.

## Features
- Static hints (loops, recursion)
- Runtime profiling (time + peak memory via `tracemalloc`)
- Model fit to {O(1), O(log n), O(n), O(n log n), O(n^2), O(n^3)}
- Decorator `@analyze` and CLI `complexity-analyze`

## Quick Start
```bash
pip install complexity-estimator
