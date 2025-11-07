"""
coo_algorithm package

This module exposes the main `COOHolistic` class and an alias `coo`
for convenient imports.

Example:
    from coo_algorithm import COOHolistic
    # or simply
    from coo_algorithm import coo

    optimizer = coo(bounds=[(-5,5), (-5,5)])
    best_x, best_f, history, diag, _ = optimizer.optimize(func)
"""

from .coo import COO

# Convenience alias
coo = COO

__all__ = ["COO", "coo"]
