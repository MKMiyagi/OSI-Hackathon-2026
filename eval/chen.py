"""Chen 2011 hardness, Hv = 2 (k^2 G)^0.585 - 3 with k = G/B (GPa), in a module with no side effects.

Same formula as scripts/make_splits.py:chen_hardness, which generated the frozen hv_chen labels; that file is frozen
and writes the quarantined test file from main(), so code that may run near the test set imports this copy instead.
scripts/verify_splits.py checks that this copy reproduces hv_chen on train and val.
"""


def chen_hardness(G, B):
    k = G / B
    return 2.0 * (k**2 * G) ** 0.585 - 3.0
