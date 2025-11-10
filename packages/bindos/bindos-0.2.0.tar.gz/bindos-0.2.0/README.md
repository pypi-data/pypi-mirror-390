
# BindOS

BindOS is a small library and CLI that flattens the curvature of numeric time series.
It was born from quantum experiments where it turned noisy fidelity trajectories into almost geodesic curves.

## Install

BindOS is in local development mode:

```bash
pip install -e .

from bindos.core import stabilize

series = [0.8, 0.82, 0.79, 0.81]
res = stabilize(series, steps=10, alpha=0.5)
print("Initial curvature:", res["curvature_initial"])
print("Stabilized curvature:", res["curvature_stabilized"])

Initial curvature: {'mean': 5.55e-17, 'std': 0.05, 'max': 0.05, 'min': -0.05, 'n': 2}
Stabilized curvature: {'mean': 0.0, 'std': 4.88e-05, 'max': 4.88e-05, 'min': -4.88e-05, 'n': 2}

bindos-run hybrid_qgeo_two_branch_hist.csv --column-index 2 --max-rows 100 --steps 20 --alpha 0.4 --output hybrid_qgeo_two_branch_hist_stab.csv

Header: ['iter', 'purity', 'fidelity', 'k1', 'k2', 'D_base', 'D_ghz', 't1', 't2', 'alpha']
Loaded points: 100
Score: {...}
Initial curvature: {...}
Stabilized curvature: {...}
Wrote stabilized CSV to: hybrid_qgeo_two_branch_hist_stab.csv

iter,purity,fidelity,...,fidelity_stabilized
0,0.9861,0.9930,...,0.9930
1,0.9791,0.9894,...,0.9923
2,0.9784,0.9891,...,0.9917


## BindOS Pro: ZOL-Q Two-Branch Engine (IBM Fez demo)

BindOS includes an experimental Pro engine (`stabilize_pro`) implementing a ZOL-Q
two-branch geodesic binding step.

Example on a 4-step purity trajectory derived from an IBM Fez-style Bell experiment:

```python
from bindos import stabilize_pro

series = [1.0, 0.862592, 0.751633, 0.662069]
res = stabilize_pro(
    series,
    steps=16,
    kappa=0.4,
    anchor_mode="linear",
    schedule_mode="cosine",
)

print(res["curvature_initial"])
print(res["curvature_stabilized"])

