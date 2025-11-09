from typing import Sequence, Dict, Any


def _discrete_curvature(series: Sequence[float]) -> list[float]:
    n = len(series)
    if n < 3:
        raise ValueError("Series must have length >= 3")
    return [
        series[i + 1] - 2 * series[i] + series[i - 1]
        for i in range(1, n - 1)
    ]


def _curvature_summary(series: Sequence[float]) -> Dict[str, Any]:
    k = _discrete_curvature(series)
    n = len(k)
    mean = sum(k) / n
    var = sum((x - mean) ** 2 for x in k) / n
    std = var ** 0.5
    return {
        "mean": mean,
        "std": std,
        "max": max(k),
        "min": min(k),
        "n": n,
    }


def curvature_score(series: Sequence[float]) -> Dict[str, Any]:
    return _curvature_summary(series)


def _one_step_smooth(series: Sequence[float], alpha: float) -> list[float]:
    x = list(series)
    n = len(x)
    if n < 3:
        return x
    y = x[:]
    for i in range(1, n - 1):
        y[i] = x[i] + alpha * (x[i - 1] + x[i + 1] - 2 * x[i])
    return y


def stabilize(series: Sequence[float], steps: int = 10, alpha: float = 0.5) -> Dict[str, Any]:
    x0 = list(series)
    x = x0[:]
    for _ in range(steps):
        x = _one_step_smooth(x, alpha)
    curv_initial = _curvature_summary(x0)
    curv_stabilized = _curvature_summary(x)
    return {
        "initial": x0,
        "stabilized": x,
        "curvature_initial": curv_initial,
        "curvature_stabilized": curv_stabilized,
    }

