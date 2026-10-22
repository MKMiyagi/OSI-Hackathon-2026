"""Shared helper for d_028-d_030: composition-weighted elemental moduli from pymatgen.

Fallback (fixed before any run): an element with no pymatgen value (Element.rigidity_modulus / bulk_modulus is None)
makes the whole composition NaN, so the row is dropped from training (sr/run_pysr.py drops non-finite rows) and
eval/score.py refuses to score a val set that contains it. No value is imputed, fitted or borrowed from another source.
pymatgen's values are the WebElements / CRC Handbook room-temperature elemental-solid numbers (GPa).
"""
import warnings

import numpy as np
from pymatgen.core import Element


def elem_value(symbol, attr):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        v = getattr(Element(symbol), attr)
    return None if v is None else float(v)


def weighted_mean(comp, attr):
    vals = [(comp.get_atomic_fraction(el), elem_value(el.symbol, attr)) for el in comp.elements]
    if any(v is None for _, v in vals):
        return float("nan")
    return sum(x * v for x, v in vals)
