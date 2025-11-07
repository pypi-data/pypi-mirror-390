# coo — Canine Olfactory Optimization (COO)

COO (Canine Olfactory Optimization) is an adaptive, surrogate-assisted, multi-pack black-box optimizer inspired by olfactory search behaviors. It is intended for expensive, noisy, multimodal continuous optimization and hyperparameter tuning.

This repository contains:

- `coo.py` — the COO optimizer implementation
- `examples/` — example scripts (ANN tuning)
- `tests/` — smoke tests
- `docs/` — mathematical explanation and pseudocode

## Features

- Multi-pack population (clusters) for structured exploration
- Lightweight surrogate ensemble (RF/GBM/GP/LGBM) with uncertainty-based selection
- Olfactory map: coarse grid memory guiding attraction between promising regions
- Gradient refinement (finite-difference) on top candidates
- Caching of evaluations to avoid repeated expensive function calls

## Quick usage

```python
from coo import COO
# define bounds as list of (low, high)
bounds = [(-5, -1), (1, 3), (8, 64), (-6, -1), (16, 64), (0, 2)]
opt = COO(bounds=bounds, n_packs=4, init_pack_size=12, max_iterations=100, surrogate_enabled=True)
best_x, best_f, hist, diag, best_pos_hist = opt.optimize(lambda x: -objective(x))
# note: this implementation treats objectives as maximization; to minimize, pass -objective(x)
```
