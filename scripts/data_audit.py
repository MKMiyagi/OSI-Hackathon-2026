"""Duplicate-composition / target-tail audit of data/splits/{train,val}.csv (no test data). Prints markdown tables."""
import numpy as np
import pandas as pd
from pymatgen.core import Composition

tr = pd.read_csv("data/splits/train.csv"); va = pd.read_csv("data/splits/val.csv")
for d in (tr, va):
    d["comp"] = [Composition(f).reduced_formula for f in d.formula]
T = "hv_chen"
print("rows", len(tr), len(va), "| median train", tr[T].median(), "| val MAE median-const", np.abs(va[T] - tr[T].median()).mean(),
      "| val MAE mean-const", np.abs(va[T] - tr[T].mean()).mean())

def dup_stats(d, name):
    g = d.groupby("comp")[T]
    n = g.size()
    multi = n[n > 1].index
    m = d[d.comp.isin(multi)]
    spread = g.max() - g.min()
    sp = spread[multi]
    med = g.transform("median")
    floor_rows = (d[T] - med).abs()   # best constant per composition under MAE = group median
    print(f"\n## {name}: {len(d)} rows, {d.comp.nunique()} distinct reduced formulas")
    print(f"- compositions with >1 row: {len(multi)} ({len(m)} rows = {100*len(m)/len(d):.1f}% of rows)")
    print(f"- max rows per composition: {n.max()}")
    print(f"- target spread (max-min) over those: median {sp.median():.2f}, mean {sp.mean():.2f}, p90 {sp.quantile(.9):.2f}, max {sp.max():.2f} GPa; "
          f"{(sp>5).sum()} compositions with spread >5 GPa, {(sp>10).sum()} with >10")
    print(f"- within-split irreducible MAE floor (group-median predictor, all rows of {name}): {floor_rows.mean():.4f} GPa; "
          f"restricted to duplicated rows: {floor_rows[d.comp.isin(multi)].mean():.4f}")
    print("- widest groups:", "; ".join(f"{c} ({n[c]} rows, {g.min()[c]:.2f}..{g.max()[c]:.2f})" for c in sp.sort_values(ascending=False).index[:6]))
    return multi

mt = dup_stats(tr, "train"); mv = dup_stats(va, "val")
print("\n## Negative targets / tail")
print(f"- train negative: {(tr[T]<0).sum()}/{len(tr)}; val negative: {(va[T]<0).sum()}/{len(va)} (min val {va[T].min():.2f})")
print(f"- val >=20 GPa: {(va[T]>=20).sum()} rows; train >=20: {(tr[T]>=20).sum()}; val max {va[T].max():.2f}")
t20 = va[va[T]>=20]
print(f"- val >=20 tail share of total absolute deviation from train median: {100*np.abs(t20[T]-tr[T].median()).sum()/np.abs(va[T]-tr[T].median()).sum():.1f}%")
print(f"- val rows whose composition also occurs in train (cross-split leakage by reduced formula): {va.comp.isin(set(tr.comp)).sum()}")

# floor from duplicate spread, pooled train+val (duplicates across the split count too)
al = pd.concat([tr, va], ignore_index=True)
med = al.groupby("comp")[T].transform("median")
print(f"\n## Pooled train+val duplicate floor\n- group-median predictor MAE over all {len(al)} rows: {(al[T]-med).abs().mean():.4f} GPa")
# leave-one-out version for val duplicates inside val: predict each row by median of OTHER rows of same composition
def loo(d):
    out = []
    for c, g in d.groupby("comp"):
        if len(g) < 2: continue
        for i in g.index:
            out.append(abs(d.loc[i, T] - g.drop(i)[T].median()))
    return np.mean(out), len(out)
print("- leave-one-out within-composition (rows with >=1 sibling), train: %.3f over %d rows; val: %.3f over %d rows" % (*loo(tr), *loo(va)))
# sibling-in-train for val rows
sib = va[va.comp.isin(set(tr.comp))]
if len(sib):
    pred = sib.comp.map(tr.groupby("comp")[T].median())
    print(f"- val rows with a train sibling: {len(sib)}; MAE of 'train-sibling median' predictor on them: {np.abs(sib[T]-pred).mean():.3f}")
