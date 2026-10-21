"""Shared helpers for the bond-count family (wiki/HYPOTHESES_4.md conventions, declared before any run).

Anion = element with Pauling chi >= 2.0 (convention, not tuned); every other element is a cation/metal.
Valence v_i: lanthanides/actinides 3; p-block group-10 (group 18 -> 8); s-block and d-block: group number
(He is p-block in pymatgen: v=8, b=0). Bond capacity b_i = min(v, 8 - v) for p-block elements, v for all others.
"""
import numpy as np

CHI_ANION = 2.0


def valence(el) -> float:
    if el.is_lanthanoid or el.is_actinoid:
        return 3.0
    if el.block == "p":
        return float(el.group - 10)
    if el.group == 18:
        return 0.0
    return float(el.group)


def capacity(el) -> float:
    v = valence(el)
    return min(v, 8.0 - v) if el.block == "p" else v


def is_anion(el) -> bool:
    chi = el.X
    return bool(np.isfinite(chi) and chi >= CHI_ANION)
