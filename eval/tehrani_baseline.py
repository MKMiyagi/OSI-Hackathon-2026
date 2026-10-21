"""Tehrani-2018-style baseline: features -> SVR -> B, G -> Chen Hv, scored on data/splits/val.csv.

Usage: uv run python eval/tehrani_baseline.py [--quick]

Reads data/splits/train.csv and val.csv only (never the test file). Hyperparameters are tuned
by grouped 5-fold CV on train (groups = sorted element set, as in make_splits.py), then refit
on all of train and scored once on val. Same metric as eval/score.py: MAE in GPa vs hv_chen.

Feature sets:
  tehrani150   all 150 features shipped with the dataset (brgoch_feats). 18 of them are
               structure-derived (volume per atom, densities, space group, crystal system...),
               so this arm is NOT composition-only; it is the faithful reproduction.
  tehrani_comp the 132 brgoch_feats that are pure functions of composition.
  magpie       full matminer Magpie preset (132 = 22 properties x 6 stats), composition-only.

Routes: "BG" = separate SVRs on log B and log G (as matbench log_kvrh/log_gvrh; keeps moduli
positive), then Chen; "BG_kcap" = same with the Pugh ratio G/B capped at its train maximum
(Chen's input domain). The cap was needed when B, G were fit untransformed (soft halides got k ~ 10, Hv ~ 100 GPa);
with log targets it never binds on val, so BG_kcap == BG;
"direct" = one SVR straight on hv_chen. Writes eval/tehrani_baseline.csv.
"""
import argparse
import ast
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from pymatgen.core import Composition
from sklearn.compose import TransformedTargetRegressor
from sklearn.model_selection import GridSearchCV, GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from eval.chen import chen_hardness  # noqa: E402

# feature families that differ between polymorphs of one composition -> structure-derived
STRUCTURE_FAMILIES = {
    "Gilman_electron_density", "Laue_class", "anisotropy", "crystal_class", "crystal_system",
    "density", "electron_density", "inversion_centre", "outer_shell_electron_density",
    "polar_axis", "reduced_volume", "space_group_number", "valence_electron_density", "volume_per_atom",
}


def element_group(formula):
    return "-".join(sorted(el.symbol for el in Composition(formula).elements))


def attach_brgoch_feats(split):
    """Join the shipped 150 features onto split rows by (formula, B, G)."""
    raw = pd.read_csv(ROOT / "data/raw/brgoch_superhard_training.csv")
    raw = raw[~raw["suspect_value"].astype(bool)]
    key = lambda d: list(zip(d.formula, d.bulk_modulus.round(6), d.shear_modulus.round(6)))
    raw = raw.assign(_k=key(raw)).drop_duplicates("_k").set_index("_k")
    feats = raw.loc[key(split), "brgoch_feats"].map(ast.literal_eval)
    F = pd.DataFrame(list(feats), index=split.index)
    if len(F) != len(split) or F.isna().any().any():
        raise SystemExit("brgoch_feats join failed")
    return F


def magpie_all(split):
    from matminer.featurizers.composition import ElementProperty
    from matminer.featurizers.conversions import StrToComposition

    stc = StrToComposition(target_col_id="comp")
    stc.set_n_jobs(1)
    d = stc.featurize_dataframe(split.copy(), "formula")
    ep = ElementProperty.from_preset("magpie")
    ep.set_n_jobs(1)
    d = ep.featurize_dataframe(d, "comp")
    return d[[c for c in d.columns if c.startswith("MagpieData")]].astype(float)


def feature_sets(tr, va):
    Ftr, Fva = attach_brgoch_feats(tr), attach_brgoch_feats(va)
    comp_cols = [c for c in Ftr.columns if c.rsplit("_feat_", 1)[0] not in STRUCTURE_FAMILIES]
    return {
        "tehrani150": (Ftr, Fva),
        "tehrani_comp": (Ftr[comp_cols], Fva[comp_cols]),
        "magpie": (magpie_all(tr), magpie_all(va)),
    }


def tuned_svr(X, y, groups, quick):
    grid = {
        "regressor__svr__C": [1, 10, 100] if quick else [1, 3, 10, 30, 100],
        "regressor__svr__gamma": ["scale"] if quick else ["scale", 0.002, 0.02],
        "regressor__svr__epsilon": [0.05] if quick else [0.02, 0.1],
    }
    est = TransformedTargetRegressor(
        regressor=make_pipeline(StandardScaler(), SVR(kernel="rbf")), transformer=StandardScaler()
    )
    gs = GridSearchCV(est, grid, cv=GroupKFold(n_splits=5), scoring="neg_mean_absolute_error", n_jobs=-1)
    gs.fit(X.values, y, groups=groups)
    return gs


def mae(a, b):
    return float(np.mean(np.abs(np.asarray(a) - np.asarray(b))))


def r2(y, p):
    return float(1 - np.sum((y - p) ** 2) / np.sum((y - np.mean(y)) ** 2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true", help="tiny grid, for smoke testing")
    args = ap.parse_args()

    tr = pd.read_csv(ROOT / "data/splits/train.csv")
    va = pd.read_csv(ROOT / "data/splits/val.csv")
    groups = tr.formula.map(element_group).values
    y_va = va.hv_chen.values
    tail = y_va >= 20
    k_max = float((tr.shear_modulus / tr.bulk_modulus).max())

    rows = []
    for name, (Xtr, Xva) in feature_sets(tr, va).items():
        print(f"\n== {name}: {Xtr.shape[1]} features")
        fits = {}
        for tgt in ("bulk_modulus", "shear_modulus", "hv_chen"):
            log = tgt != "hv_chen"  # moduli fit in log space; cv score is then MAE of log(modulus)
            y = np.log(tr[tgt].values) if log else tr[tgt].values
            gs = tuned_svr(Xtr, y, groups, args.quick)
            fits[tgt] = np.exp(gs.predict(Xva.values)) if log else gs.predict(Xva.values)
            print(f"  {tgt:14s} cv_MAE{'(log)' if log else '     '} {-gs.best_score_:7.3f}  "
                  f"val_MAE {mae(va[tgt], fits[tgt]):7.3f}  val_R2 {r2(va[tgt].values, fits[tgt]):.3f}  {gs.best_params_}")
            if log:
                rows.append(dict(features=name, n_features=Xtr.shape[1], quantity=tgt, route="svr_log",
                                 val_mae=mae(va[tgt], fits[tgt]), val_r2=r2(va[tgt].values, fits[tgt]),
                                 cv_score=-gs.best_score_, params=str(gs.best_params_)))
        B, G = fits["bulk_modulus"], fits["shear_modulus"]
        hv = {"BG": chen_hardness(G, B), "BG_kcap": chen_hardness(np.minimum(G, k_max * B), B), "direct": fits["hv_chen"]}
        for route, pred in hv.items():
            rows.append(dict(features=name, n_features=Xtr.shape[1], quantity="hv_chen", route=route,
                             val_mae=mae(y_va, pred), val_r2=r2(y_va, pred),
                             val_mae_tail20=mae(y_va[tail], pred[tail]), val_mae_nonneg=mae(y_va[y_va >= 0], pred[y_va >= 0])))
            print(f"  Hv via {route:7s}  val_MAE {mae(y_va, pred):7.3f}  R2 {r2(y_va, pred):.3f}  "
                  f"tail(>=20, n={tail.sum()}) MAE {mae(y_va[tail], pred[tail]):6.2f}")

    out = pd.DataFrame(rows)
    out.to_csv(ROOT / "eval/tehrani_baseline.csv", index=False, float_format="%.4f")
    print("\nwrote eval/tehrani_baseline.csv")


if __name__ == "__main__":
    main()
