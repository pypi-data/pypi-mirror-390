import math
from typing import Dict, Any
import numpy as np


def _as_1d_float_array(series):
    arr = np.asarray(series, dtype=float).reshape(-1)
    if arr.shape[0] < 3:
        raise ValueError("series must have length >= 3")
    return arr


def _build_anchor_linear(base_series):
    n = base_series.shape[0]
    start = float(base_series[0])
    end = float(base_series[-1])
    t = np.linspace(0.0, 1.0, n)
    return start + t * (end - start)


def _compute_curvature(series):
    x = _as_1d_float_array(series)
    n = x.shape[0]
    K = np.zeros_like(x)
    if n >= 3:
        K[1:-1] = x[2:] - 2.0 * x[1:-1] + x[:-2]
    return K


def _curvature_stats(series):
    K = _compute_curvature(series)
    if K.shape[0] <= 2:
        return {"mean": 0.0, "std": 0.0, "max": 0.0, "min": 0.0, "n": 0}
    interior = K[1:-1]
    if interior.size == 0:
        return {"mean": 0.0, "std": 0.0, "max": 0.0, "min": 0.0, "n": 0}
    mean = float(np.mean(interior))
    std = float(np.std(interior))
    max_val = float(np.max(interior))
    min_val = float(np.min(interior))
    n = int(interior.shape[0])
    return {"mean": mean, "std": std, "max": max_val, "min": min_val, "n": n}


def zolq_two_branch_bind(
    series,
    steps: int = 64,
    kappa: float = 0.4,
    anchor_mode: str = "linear",
    schedule_mode: str = "fixed",
) -> Dict[str, Any]:
    x0 = _as_1d_float_array(series)
    n = x0.shape[0]
    if anchor_mode == "linear":
        anchor = _build_anchor_linear(x0)
    else:
        raise ValueError(f"unsupported anchor_mode: {anchor_mode}")
    base = x0.copy()
    x = x0.copy()
    gamma = 0.02
    for k in range(steps):
        if schedule_mode == "fixed":
            k_eff = kappa
        elif schedule_mode == "cosine":
            if steps <= 1:
                k_eff = kappa
            else:
                k_eff = 0.5 * kappa * (1.0 + math.cos(math.pi * k / max(steps - 1, 1)))
        else:
            raise ValueError(f"unsupported schedule_mode: {schedule_mode}")
        lam = float(k + 1) / float(steps)
        y = (1.0 - lam) * base + lam * anchor
        K = np.clip(_compute_curvature(x), -1.0, 1.0)
        x_new = x.copy()
        if n > 2:
            x_new[1:-1] = x[1:-1] + k_eff * (y[1:-1] - x[1:-1]) - gamma * K[1:-1]
        x_new[0] = base[0]
        x_new[-1] = base[-1]
        x = x_new
    initial_list = x0.astype(float).tolist()
    stabilized_list = x.astype(float).tolist()
    anchor_list = anchor.astype(float).tolist()
    curv_init = _curvature_stats(x0)
    curv_stab = _curvature_stats(x)
    return {
        "initial": initial_list,
        "stabilized": stabilized_list,
        "anchor": anchor_list,
        "curvature_initial": curv_init,
        "curvature_stabilized": curv_stab,
    }


def stabilize_pro(
    series,
    steps: int = 64,
    kappa: float = 0.4,
    anchor_mode: str = "linear",
    schedule_mode: str = "fixed",
) -> Dict[str, Any]:
    return zolq_two_branch_bind(
        series=series,
        steps=steps,
        kappa=kappa,
        anchor_mode=anchor_mode,
        schedule_mode=schedule_mode,
    )

