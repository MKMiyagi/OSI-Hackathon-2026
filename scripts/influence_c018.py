"""Influence analysis of c018_s0 c12 vs the Magpie c12 equation on val (numpy/scipy only on existing equations; no PySR).
Usage: uv run python scripts/influence_c018.py > wiki/INFLUENCE_c018.md  (prints markdown body)"""
import sys
import numpy as np
import pandas as pd
from pymatgen.core import Composition
from scipy.optimize import minimize

sys.path.insert(0, ".")
from sr.run_pysr import featurize  # noqa: E402

T = "hv_chen"
va, Xv = featurize(pd.read_csv("data/splits/val.csv"), ["d_017"])
tr, Xt = featurize(pd.read_csv("data/splits/train.csv"), ["d_017"])
yv, yt = va[T].values, tr[T].values

def eq_c018(X, c1=1070.5477, c2=3.0097768, gap=True):
    den = np.exp(X.d_017) + X.m_NdValence + c2 - (X.m_GSbandgap if gap else 0)
    return (c1 / den / X.m_GSvolume_pa).values

def eq_mag(X):
    return ((642.6664 / X.m_GSvolume_pa) / (X.m_NValence - X.m_NfValence) + X.m_NpUnfilled * np.sqrt(X.m_NdUnfilled)).values

pc, pm = eq_c018(Xv), eq_mag(Xv)
mae = lambda y, p: float(np.mean(np.abs(y - p)))
print(f"# Influence analysis: c018_s0 c12 vs Magpie c12 (development-set, val reused)\n")
print("Script: `scripts/influence_c018.py`. Equations are taken verbatim from ledger/results.csv (c018_s0 c12; c012_s1 c12, the recurring Magpie-only c12 equation). All MAEs are development-set (val, reused), n=374.\n")
print(f"- c018_s0 c12: `(1070.5477/((exp(d_017)+(NdValence+3.0097768))-GSbandgap))/GSvolume_pa`, val MAE {mae(yv,pc):.4f}")
print(f"- Magpie c12: `642.6664/GSvolume_pa/(NValence-NfValence)+NpUnfilled*sqrt(NdUnfilled)`, val MAE {mae(yv,pm):.4f}")

# ---- 1. jackknife of the gap
ec, em = np.abs(yv - pc), np.abs(yv - pm)
d = em - ec                      # per-row contribution to (MAE_mag - MAE_c018) * n
n = len(d); gap = d.mean()
loo = (n * gap - d) / (n - 1)    # gap with row i removed
se = np.sqrt((n - 1) / n * np.sum((loo - loo.mean()) ** 2))
print(f"\n## 1. Per-row jackknife of the MAE gap\nGap = MAE(Magpie) - MAE(c018_s0) = {gap:.4f} GPa; jackknife SE {se:.4f} (row-level, ignores duplicate-composition correlation and selection; descriptive only). Gap is positive in {(d>0).sum()} rows, negative in {(d<0).sum()}.\n")
order = np.argsort(-np.abs(d))
print("Top-10 influential rows (by |per-row contribution|; contribution = (|err_mag|-|err_c018|)/n; gap without the row in last column):\n")
print("| rank | formula | target | pred c018 | pred Magpie | contribution to gap | gap without row |\n|---|---|---|---|---|---|---|")
for r, i in enumerate(order[:10], 1):
    print(f"| {r} | {va.formula[i]} | {yv[i]:.2f} | {pc[i]:.2f} | {pm[i]:.2f} | {d[i]/n:+.4f} | {loo[i]:.4f} |")
top = order[:10]; keep = np.setdiff1d(np.arange(n), top)
pos = np.argsort(-d)[:10]
print(f"\n- Top-10 by |contribution|: net {d[top].sum()/n:+.4f} of the {gap:.4f} gap ({100*d[top].sum()/d.sum():.1f}%); gap on the remaining {len(keep)} rows = {d[keep].mean():.4f}.")
print(f"- Top-10 by positive contribution only: {d[pos].sum()/n:+.4f} ({100*d[pos].sum()/d.sum():.1f}% of the gap); gap on the other {n-10} rows = {np.delete(d,pos).mean():.4f}.")
# group-level: by reduced formula
grp = pd.Series(d, index=va.formula.map(lambda f: Composition(f).reduced_formula)).groupby(level=0).sum()
gtop = grp.abs().sort_values(ascending=False).index[:10]
print(f"- Dropping the top-10 compositions (group-level, {len(gtop)} compositions): gap = {(d.sum()-grp[gtop].sum())/(n-va.formula.map(lambda f: Composition(f).reduced_formula).isin(gtop).sum()):.4f}.")

# ---- 2. families
def family(f):
    c = Composition(f); els = [e.symbol for e in c.elements]
    if "O" in els: return "oxides"
    if len(els) == 2 and any(e in ("B", "C", "N") for e in els): return "binary carbides/nitrides/borides"
    if all(e.is_metal or e.symbol in ("Si", "Ge", "Sb") for e in c.elements): return "intermetallics"
    return "other"
fam = va.formula.map(family)
print("\n## 2. Per-family MAE\nFamilies (assigned in this order): oxides = contains O; binary C/N/B = exactly two elements, one of B/C/N, no O; intermetallics = every element a metal or Si/Ge/Sb; other = the rest. \n")
print("| family | n | MAE c018_s0 | MAE Magpie c12 | gap (Magpie - c018) | share of total gap | mean target | MAE const (train median) |\n|---|---|---|---|---|---|---|---|")
med = np.median(yt)
for k in ["binary carbides/nitrides/borides", "oxides", "intermetallics", "other"]:
    m = (fam == k).values
    print(f"| {k} | {m.sum()} | {ec[m].mean():.3f} | {em[m].mean():.3f} | {d[m].mean():+.3f} | {100*d[m].sum()/d.sum():.1f}% | {yv[m].mean():.2f} | {np.abs(yv[m]-med).mean():.3f} |")
print(f"| all | {n} | {ec.mean():.3f} | {em.mean():.3f} | {gap:+.3f} | 100% | {yv.mean():.2f} | {np.abs(yv-med).mean():.3f} |")

# ---- 3. GSbandgap ablation
print("\n## 3. GSbandgap ablation\nSame functional form with the `- m_GSbandgap` term deleted: `C1/((exp(d_017)+NdValence+C2)*GSvolume_pa)`. Constants (C1, C2) re-fit three ways, each also done for the full form (control) so the comparison is like for like. Nelder-Mead from several starts; best of starts reported. 'train' fits never see val. 'val (oracle)' fits constants on val itself and is optimistic.\n")
def fit(loss, X, y, gap):
    best = None
    for s1 in (300, 1070, 3000):
        for s2 in (0.5, 3.0, 8.0):
            f = lambda th: loss(y, eq_c018(X, th[0], th[1], gap))
            r = minimize(f, [s1, s2], method="Nelder-Mead", options=dict(xatol=1e-6, fatol=1e-10, maxiter=20000))
            if np.isfinite(r.fun) and (best is None or r.fun < best.fun): best = r
    return best.x
mse = lambda y, p: float(np.mean((y - p) ** 2))
print("| fit | form | C1 | C2 | train MAE | val MAE |\n|---|---|---|---|---|---|")
print(f"| as published (PySR constants) | with GSbandgap | 1070.5 | 3.010 | {mae(yt,eq_c018(Xt)):.4f} | {mae(yv,pc):.4f} |")
for lname, loss, X, y, tag in [("train, MSE", mse, Xt, yt, "train"), ("train, MAE", mae, Xt, yt, "train"), ("val, MAE (oracle)", mae, Xv, yv, "val")]:
    for gap, form in [(True, "with GSbandgap"), (False, "without GSbandgap")]:
        th = fit(loss, X, y, gap)
        print(f"| {lname} | {form} | {th[0]:.1f} | {th[1]:.3f} | {mae(yt,eq_c018(Xt,*th,gap=gap)):.4f} | {mae(yv,eq_c018(Xv,*th,gap=gap)):.4f} |")
print(f"\nGSbandgap in val: mean {Xv.m_GSbandgap.mean():.3f} eV, max {Xv.m_GSbandgap.max():.2f}; in train mean {Xt.m_GSbandgap.mean():.3f}.")
