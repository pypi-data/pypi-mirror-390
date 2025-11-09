from complexity_estimator.estimator import estimate_report

def f(arr):
    s = 0
    for x in arr:
        s += x
    return s

def maker(n):
    return ([0]*n,), {}

def test_estimate_runs():
    rep = estimate_report(f, maker=maker, sizes=[10, 20, 40])
    assert "time_estimate" in rep
    assert "space_estimate" in rep
