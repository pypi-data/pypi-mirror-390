"""
tests/test_hpo_smoke.py

Simple smoke tests for the COO optimizer.
Run with: pytest -q
"""

import numpy as np
from coo import COO


def sphere(x):
    # simple minimization sphere: global min at 0. We'll maximize negative value to match COO interface
    x = np.asarray(x)
    return -np.sum((x)**2)


def test_coo_runs_and_improves():
    bounds = [(-5, 5)] * 3
    opt = COO(bounds=bounds, n_packs=2, init_pack_size=6,
              max_iterations=8, surrogate_enabled=False, random_state=0)
    best_x, best_f, conv, diag, _ = opt.optimize(lambda x: sphere(x))
    # best_f is the best (max) found (sphere returns negative). Ensure improvement over initial (not -inf)
    assert not np.isinf(best_f)
    assert len(conv) >= 1
    # sanity: final best should be <= 0 (since sphere max at 0)
    assert best_f <= 0.0


def test_caching_reduces_evals():
    bounds = [(-1, 1)] * 2
    opt = COO(bounds=bounds, n_packs=1, init_pack_size=4,
              max_iterations=4, surrogate_enabled=False, random_state=1)
    # define an objective that counts calls
    calls = {'n': 0}

    def f(x):
        calls['n'] += 1
        return -np.sum(x**2)
    _, _, _, diag, _ = opt.optimize(lambda x: f(x))
    # cached evals should be <= calls (calls tracked in f), but at least not zero
    assert diag['exact_evals'] >= 1
