# %% coo.py
"""
--------------------

Canine Olfactory Optimization (COO) Algorithm
---------------------------------------------
A surrogate-assisted, adaptive, multi-pack optimizer inspired by canine olfactory behavior.

Key features:
- Adaptive multi-pack search
- Surrogate-assisted learning with uncertainty quantification
- Gradient refinement via finite-difference probing
- Olfactory mapping and cooperative exploration
- Automatic surrogate activation/deactivation using hysteresis
"""

from scipy.optimize import differential_evolution
from typing import Callable, List, Tuple, Optional, Dict, Any
import numpy as np
import math
import time
import os
from joblib import Parallel, delayed
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import KFold
from sklearn.metrics import r2_score
import warnings
warnings.filterwarnings("ignore")

# optional components
try:
    from sklearn.gaussian_process import GaussianProcessRegressor
    from sklearn.gaussian_process.kernels import Matern, WhiteKernel, ConstantKernel
    HAS_GP = True
except Exception:
    HAS_GP = False

try:
    import lightgbm as lgb
    HAS_LGBM = True
except Exception:
    HAS_LGBM = False

try:
    import cma
    HAS_CMA = True
except Exception:
    HAS_CMA = False


# -------------------------
# Lightweight surrogate (fast defaults)
# -------------------------

class FastSurrogate:
    """Small validated surrogate with uncertainty. Fast defaults for toy functions."""

    def __init__(self, kind='rf', random_state=0, n_folds=3, n_jobs=1):
        self.kind = kind
        self.random_state = random_state
        self.n_folds = n_folds
        self.n_jobs = n_jobs
        self.models: List[Tuple[str, Any]] = []
        self.cv_score_ = float('nan')

    def _build(self):
        jobs = []
        if self.kind in ('rf', 'ensemble'):
            # fewer trees for speed on toy functions
            jobs.append(('rf', RandomForestRegressor(n_estimators=40, n_jobs=1,
                                                     random_state=self.random_state, max_depth=12)))
        if self.kind in ('gb', 'ensemble'):
            jobs.append(('gb', GradientBoostingRegressor(n_estimators=80, learning_rate=0.1,
                                                         max_depth=4, random_state=self.random_state)))
        if self.kind == 'lgb' and HAS_LGBM:
            jobs.append(('lgb', lgb.LGBMRegressor(n_estimators=80,
                        random_state=self.random_state, n_jobs=1)))
        if self.kind == 'gp' and HAS_GP:
            kernel = ConstantKernel(
                1.0) * Matern(length_scale=1.0, nu=2.5) + WhiteKernel(1e-6)
            jobs.append(('gp', GaussianProcessRegressor(
                kernel=kernel, normalize_y=True, random_state=self.random_state, n_restarts_optimizer=0)))
        return jobs

    def fit(self, X, y):
        X = np.asarray(X)
        y = np.asarray(y)
        jobs = self._build()
        if not jobs:
            raise RuntimeError(
                "No surrogate models available for kind=%s" % self.kind)

        def _fit_one(item):
            name, model = item
            model.fit(X, y)
            return (name, model)
        n_parallel = min(len(jobs), max(1, self.n_jobs))
        self.models = Parallel(n_jobs=n_parallel)(
            delayed(_fit_one)(it) for it in jobs)
        # quick CV (kfold <= n_samples)
        n_splits = min(self.n_folds, len(y))
        if n_splits < 2:
            self.cv_score_ = 1.0
            return self
        kf = KFold(n_splits=n_splits, shuffle=True,
                   random_state=self.random_state)
        preds, trues = [], []
        for tr, te in kf.split(X):
            fold_preds = []
            for name, m in self.models:
                Cls = m.__class__
                try:
                    clone = Cls(**m.get_params())
                    clone.fit(X[tr], y[tr])
                    fold_preds.append(clone.predict(X[te]))
                except Exception:
                    fold_preds.append(m.predict(X[te]))
            fold_preds = np.vstack(fold_preds).mean(axis=0)
            preds.append(fold_preds)
            trues.append(y[te])
        preds = np.concatenate(preds)
        trues = np.concatenate(trues)
        try:
            self.cv_score_ = float(r2_score(trues, preds))
        except Exception:
            self.cv_score_ = float('-inf')
        return self

    def predict(self, X):
        if not self.models:
            raise RuntimeError("Surrogate not trained")
        X = np.asarray(X)
        preds = []
        for name, m in self.models:
            preds.append(np.asarray(m.predict(X)))
        preds = np.vstack(preds)
        mean = preds.mean(axis=0)
        std = preds.std(axis=0)
        # if rf present, use tree variance
        names = [n for n, _ in self.models]
        if 'rf' in names:
            rf = dict(self.models).get('rf')
            if rf is not None and hasattr(rf, 'estimators_'):
                tree_preds = np.vstack([t.predict(X) for t in rf.estimators_])
                std_tree = tree_preds.std(axis=0)
                std = np.maximum(std, std_tree)
        return mean, std

# -------------------------
# COO class
# -------------------------


class COO:
    """COO Algorithm."""

    def __init__(self,
                 bounds: List[Tuple[float, float]],
                 n_packs: int = 3,
                 init_pack_size: int = 12,
                 min_pack_size: int = 6,
                 max_iterations: int = 200,
                 surrogate_enabled: bool = True,
                 surrogate_kind: str = 'rf',
                 surrogate_min_samples: int = 20,
                 surrogate_retrain_freq: int = 15,
                 surrogate_min_r2_activate: float = 0.55,
                 surrogate_min_r2_deactivate: float = 0.45,
                 uncertainty_threshold: float = 0.18,
                 elitist_diversity_threshold: float = 1e-3,
                 grad_refinement_pct_init: float = 0.08,
                 gradient_step_init: float = 0.03,
                 random_state: Optional[int] = None,
                 verbose: bool = False):
        self.bounds = np.asarray(bounds)
        self.dim = len(bounds)
        self.lower = self.bounds[:, 0]
        self.upper = self.bounds[:, 1]

        # population / packs
        self.n_packs = n_packs
        self.init_pack_size = init_pack_size
        self.min_pack_size = min_pack_size

        # control
        self.max_iterations = max_iterations
        self.random_state = random_state
        self.rng = np.random.RandomState(random_state)
        self.verbose = verbose

        # surrogate
        self.surrogate_enabled = surrogate_enabled
        self.surrogate_kind = surrogate_kind
        self.surrogate_min_samples = surrogate_min_samples
        self.surrogate_retrain_freq = surrogate_retrain_freq
        self.surrogate_min_r2_activate = surrogate_min_r2_activate
        self.surrogate_min_r2_deactivate = surrogate_min_r2_deactivate
        self.uncertainty_threshold = uncertainty_threshold
        self.surrogate: Optional[FastSurrogate] = None
        self.surrogate_active = False
        self.surrogate_last_cv = float('-inf')

        # movement hyperparams (will be adapted)
        self.momentum_base = 0.6
        self.local_attraction_base = 0.3
        self.global_coop_base = 0.4

        # adaptive gradient refinement
        self.grad_refinement_pct_init = grad_refinement_pct_init
        self.gradient_step_init = gradient_step_init

        # elitist exchange criteria
        self.elitist_diversity_threshold = elitist_diversity_threshold
        self.elitist_count = 0

        # olfactory map (coarse grid)
        self.map_cells_per_dim = max(6, int(np.ceil(self.dim * 2)))
        self.olfactory_map: Dict[Tuple[int, ...], float] = {}

        # caches and diagnostics
        self.evaluation_cache: Dict[Tuple, float] = {}
        self.best_position: Optional[np.ndarray] = None
        self.best_fitness = -np.inf
        self.convergence_history: List[float] = []
        self.best_position_history: List[np.ndarray] = []
        self.diversity_history: List[float] = []
        self.surrogate_cv_history: List[float] = []
        self.retrain_log: List[Dict[str, Any]] = []
        self.exact_evals = 0
        self.surrogate_calls = 0
        self.gradient_refinements = 0

    # -----------------------------------------------------------------
    # Internal utilities
    # -----------------------------------------------------------------
    def _params_to_key(self, params: np.ndarray) -> Tuple:
        return tuple(np.round(params, 8).tolist())

    def _cached_eval(self, x: np.ndarray, func: Callable) -> float:
        key = self._params_to_key(x)
        if key not in self.evaluation_cache:
            v = float(func(x))
            self.evaluation_cache[key] = v
            self.exact_evals += 1
        return self.evaluation_cache[key]

    def _batch_eval(self, X: np.ndarray, func: Callable) -> np.ndarray:
        return np.array([self._cached_eval(x, func) for x in X])

    def _init_packs(self):
        packs = []
        for _ in range(self.n_packs):
            pos = self.lower + \
                self.rng.rand(self.init_pack_size, self.dim) * \
                (self.upper - self.lower)
            vel = np.zeros_like(pos)
            packs.append({'positions': pos, 'velocities': vel})
        return packs

    # olfactory map helpers
    def _cell_index(self, pos: np.ndarray):
        # map pos to grid cell index tuple
        rel = (pos - self.lower) / (self.upper - self.lower + 1e-12)
        idx = tuple(np.minimum(np.floor(
            rel * self.map_cells_per_dim).astype(int), self.map_cells_per_dim - 1).tolist())
        return idx

    def _update_olfactory(self, pos: np.ndarray, fitness: float):
        idx = self._cell_index(pos)
        cur = self.olfactory_map.get(idx, -np.inf)
        if fitness > cur:
            self.olfactory_map[idx] = fitness

    def _olfactory_attraction(self, pos: np.ndarray):
        # find best neighboring cell and return vector toward its center
        idx = self._cell_index(pos)
        best_idx = idx
        best_val = self.olfactory_map.get(idx, -np.inf)
        # check neighbors within radius 1
        rng = range(-1, 2)
        for offsets in np.ndindex(*(3,) * self.dim):
            nbr = tuple(min(max(i + off - 1, 0), self.map_cells_per_dim - 1)
                        for i, off in zip(idx, offsets))
            v = self.olfactory_map.get(nbr, -np.inf)
            if v > best_val:
                best_val = v
                best_idx = nbr
        # return vector to center of best_idx
        center_rel = (np.array(best_idx) + 0.5) / self.map_cells_per_dim
        center = self.lower + center_rel * (self.upper - self.lower)
        return center - pos

    # -----------------------------------------------------------------
    # Surrogate retraining
    # -----------------------------------------------------------------
    # surrogate retrain with hysteresis

    def _retrain_surrogate_if_needed(self, iteration: int, X_hist: List[np.ndarray], y_hist: List[float]):
        if not self.surrogate_enabled:
            return None
        total = len(X_hist)
        if total < self.surrogate_min_samples:
            return None
        # decide on retrain frequency adaptively: early retrain allowed, later less frequent
        # We use surrogate_retrain_freq as base but increase it if surrogate is active
        effective_freq = self.surrogate_retrain_freq * \
            (1 if not self.surrogate_active else 3)
        if iteration % max(1, effective_freq) != 0:
            return None
        X = np.vstack(X_hist)
        y = np.asarray(y_hist)
        s = FastSurrogate(kind=self.surrogate_kind,
                          random_state=self.rng.randint(0, 10000), n_folds=3)
        try:
            s.fit(X, y)
            cv = float(s.cv_score_)
            self.surrogate_cv_history.append(cv)
            prev_active = self.surrogate_active
            # hysteresis
            if not self.surrogate_active and cv >= self.surrogate_min_r2_activate:
                self.surrogate_active = True
            elif self.surrogate_active and cv < self.surrogate_min_r2_deactivate:
                self.surrogate_active = False
            self.surrogate = s
            self.surrogate_last_cv = cv
            self.retrain_log.append(
                {'iter': iteration, 'cv': cv, 'active': self.surrogate_active, 'samples': total})
            return s
        except Exception as e:
            if self.verbose:
                print("Surrogate train failed:", e)
            return None
    # -----------------------------------------------------------------
    # Gradient estimation
    # -----------------------------------------------------------------
    # compute numerical gradient (for exact and surrogate)

    def _num_grad(self, position: np.ndarray, func: Callable, eps: float = 1e-4) -> np.ndarray:
        g = np.zeros(self.dim)
        for j in range(self.dim):
            a = position.copy()
            b = position.copy()
            a[j] += eps
            b[j] -= eps
            fa = self._cached_eval(a, func)
            fb = self._cached_eval(b, func)
            g[j] = (fa - fb) / (2 * eps)
        return g

    def _surrogate_grad(self, position: np.ndarray, eps: float = 1e-4) -> np.ndarray:
        # estimate gradient of surrogate mean by finite difference on surrogate.predict
        if not self.surrogate:
            return np.zeros(self.dim)
        base, _ = self.surrogate.predict(position.reshape(1, -1))
        g = np.zeros(self.dim)
        for j in range(self.dim):
            a = position.copy()
            a[j] += eps
            b = position.copy()
            b[j] -= eps
            ma, _ = self.surrogate.predict(a.reshape(1, -1))
            mb, _ = self.surrogate.predict(b.reshape(1, -1))
            g[j] = (ma[0] - mb[0]) / (2 * eps)
        return g

    # dynamic adaptation helpers
    def _adaptive_coeffs(self, iteration: int):
        t = iteration / max(1, self.max_iterations)
        # exploration ratio: large early, small late
        exploration = math.exp(-3.0 * t)
        momentum = 0.85 * exploration + 0.25 * \
            (1 - exploration)  # more momentum early
        local_attr = 0.15 * exploration + 0.6 * (1 - exploration)
        coop = 0.3 * exploration + 0.5 * (1 - exploration)
        return momentum, local_attr, coop

    def _pack_diversity(self, packs: List[Dict]):
        all_pos = np.vstack([p['positions'] for p in packs])
        # diversity = mean std over dimensions
        return float(np.mean(np.std(all_pos, axis=0)))

    # -----------------------------------------------------------------
    # Main optimization loop
    # -----------------------------------------------------------------
    def optimize(self, objective_function: Callable[[np.ndarray], float]):
        packs = self._init_packs()
        X_history: List[np.ndarray] = []
        y_history: List[float] = []
        self.evaluation_cache.clear()
        self.best_fitness = -np.inf
        self.best_position = None
        self.convergence_history.clear()
        self.diversity_history.clear()
        self.surrogate_cv_history.clear()
        self.retrain_log.clear()
        self.exact_evals = 0
        self.surrogate_calls = 0
        self.gradient_refinements = 0
        start_time = time.time()

        for iteration in range(self.max_iterations):
            momentum, local_attr, coop_base = self._adaptive_coeffs(iteration)
            # Try retrain surrogate adaptively
            self._retrain_surrogate_if_needed(iteration, X_history, y_history)

            pack_bests = []
            # compute pack diversity
            div = self._pack_diversity(packs)
            self.diversity_history.append(div)
            # dynamic pack size shrinking if diversity low
            if div < 1e-3:
                for p in packs:
                    size = p['positions'].shape[0]
                    if size > self.min_pack_size:
                        newsize = max(self.min_pack_size, size - 1)
                        p['positions'] = p['positions'][:newsize]
                        p['velocities'] = p['velocities'][:newsize]

            for p_idx, pack in enumerate(packs):
                pos = pack['positions']
                vel = pack['velocities']
                n = pos.shape[0]
                # evaluate using surrogate if active
                if self.surrogate_enabled and self.surrogate and self.surrogate_active:
                    try:
                        mean_pred, std_pred = self.surrogate.predict(pos)
                        self.surrogate_calls += len(pos)
                        # mask uncertain
                        rel_std = std_pred / (np.abs(mean_pred) + 1e-12)
                        uncertain = rel_std > self.uncertainty_threshold
                        # ensure top candidates are exactly evaluated
                        n_exact = max(1, n // 2)
                        top_idx = np.argsort(-mean_pred)[:n_exact]
                        eval_mask = np.logical_or(
                            uncertain, np.isin(np.arange(n), top_idx))
                        fitness = mean_pred.copy()
                        if np.any(eval_mask):
                            exact_vals = self._batch_eval(
                                pos[eval_mask], objective_function)
                            # blend exact with surrogate using trust weight
                            for j, idx in enumerate(np.where(eval_mask)[0]):
                                m = mean_pred[idx]
                                s = std_pred[idx]
                                exact_v = exact_vals[j]
                                w = math.exp(-(s / (max(self.uncertainty_threshold,
                                             1e-6) * (abs(m) + 1e-12))) ** 2)
                                fitness[idx] = w * m + (1 - w) * exact_v
                    except Exception as e:
                        if self.verbose:
                            print("Surrogate predict failed:", e)
                        fitness = self._batch_eval(pos, objective_function)
                else:
                    fitness = self._batch_eval(pos, objective_function)

                # update olfactory map with each pos
                for i in range(n):
                    self._update_olfactory(pos[i], float(fitness[i]))

                # find local best and maybe update global best
                local_idx = int(np.argmax(fitness))
                local_pos = pos[local_idx].copy()
                local_val = float(fitness[local_idx])
                if local_val > self.best_fitness:
                    self.best_fitness = local_val
                    self.best_position = local_pos.copy()

                pack_bests.append((local_val, local_pos))

                # movement: include local attraction, global cooperation, momentum, olfactory bias, surrogate gradient hint
                global_dir = (
                    self.best_position - pos) if self.best_position is not None else np.zeros((n, self.dim))
                # surrogate direction hint (small)
                if self.surrogate and self.surrogate_active:
                    for i in range(n):
                        # compute surrogate gradient and add small bias
                        # small cost (surrogate predict used)
                        sg = self._surrogate_grad(pos[i])
                        # normalize and scale
                        gnorm = np.linalg.norm(sg) + 1e-12
                        global_dir[i] += 0.02 * \
                            (sg / gnorm) if gnorm > 1e-12 else 0.0

                # olfactory attract
                for i in range(n):
                    od = self._olfactory_attraction(pos[i])
                    # combine velocities
                    vel[i] = (momentum * vel[i]
                              + local_attr * (local_pos - pos[i])
                              + coop_base * global_dir[i] / (n + 1)
                              + 0.05 * od)
                    # update position with noise decaying over time
                    sigma = 0.3 * math.exp(-0.03 * iteration)
                    pos[i] = pos[i] + vel[i] + sigma * self.rng.randn(self.dim)
                    pos[i] = np.clip(pos[i], self.lower, self.upper)
                pack['positions'] = pos
                pack['velocities'] = vel

            # diversity-based elitist exchange (if diversity low)
            if div < self.elitist_diversity_threshold:
                sorted_bests = sorted(pack_bests, key=lambda x: -x[0])
                elites = [
                    p for _, p in sorted_bests[:min(3, len(sorted_bests))]]
                for pack in packs:
                    vals = self._batch_eval(
                        pack['positions'], objective_function)
                    worst = int(np.argmin(vals))
                    for e in elites:
                        pert = e + self.rng.randn(self.dim) * 0.01
                        pack['positions'][worst] = np.clip(
                            pert, self.lower, self.upper)
                        self.elitist_count += 1

            # adaptive gradient refinement: fewer picks later
            pct = max(0.02, self.grad_refinement_pct_init *
                      (1 - iteration / max(1, self.max_iterations)))
            all_pos = np.vstack([p['positions'] for p in packs])
            all_f = self._batch_eval(all_pos, objective_function)
            n_top = max(1, int(len(all_pos) * pct))
            top_idx = np.argsort(-all_f)[:n_top]
            for idx in top_idx:
                pos0 = all_pos[idx].copy()
                curf = all_f[idx]
                grad = self._num_grad(pos0, objective_function)
                gnorm = np.linalg.norm(grad) + 1e-12
                step = np.clip(self.gradient_step_init * (1 - iteration /
                               max(1, self.max_iterations)) * (grad / gnorm), -0.07, 0.07)
                newp = np.clip(pos0 + step, self.lower, self.upper)
                newf = self._cached_eval(newp, objective_function)
                if newf > curf:
                    # place back into corresponding pack
                    offset = 0
                    for pack in packs:
                        s = pack['positions'].shape[0]
                        if idx < offset + s:
                            local = idx - offset
                            pack['positions'][local] = newp
                            pack['velocities'][local] *= 0.3
                            self.gradient_refinements += 1
                            break
                        offset += s

            self.convergence_history.append(self.best_fitness)
            self.best_position_history.append(np.copy(
                self.best_position) if self.best_position is not None else np.full(self.dim, np.nan))

            if self.verbose and iteration % max(1, self.max_iterations // 10) == 0:
                print(f"Iter {iteration:4d} | Best {self.best_fitness:.6e} | Cache {len(self.evaluation_cache)} | Exact {self.exact_evals} | SurCalls {self.surrogate_calls} | Div {div:.4e}")

            # early stopping (no improvement recently)
            if len(self.convergence_history) > 10:
                window = self.convergence_history[-10:]
                if max(window) - min(window) < 2e-6:  # weaker early stop (earlier it was 1e-9:)
                    if self.verbose:
                        print(
                            f"Early stopping at iter {iteration} (flat window)")
                    break

        duration = time.time() - start_time
        diagnostics = {
            'cache_size': len(self.evaluation_cache),
            'exact_evals': self.exact_evals,
            'surrogate_calls': self.surrogate_calls,
            'iterations': len(self.convergence_history),
            'time_s': duration,
            'diversity_history': list(self.diversity_history),
            'surrogate_cv_history': list(self.surrogate_cv_history),
            'retrain_log': list(self.retrain_log),
            'elitist_count': self.elitist_count,
            'gradient_refinements': self.gradient_refinements
        }
        return self.best_position, self.best_fitness, self.convergence_history, diagnostics, self.best_position_history
