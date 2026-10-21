"""Fixed comparison protocol for the declared composition -> B,G -> Chen baseline.

Run: uv run python eval/baselines.py --run-id baseline_v1
Only train.csv and val.csv are read. Each run appends six ledger rows and rewrites
wiki/BASELINES.md. This is Tehrani-2018-style, not an exact paper reproduction.
"""

import argparse
import csv
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

import numpy as np
import pandas as pd
from matminer.featurizers.composition import ElementProperty
from pymatgen.core import Composition
from sklearn.impute import SimpleImputer
from sklearn.model_selection import GridSearchCV, GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR

ROOT = Path(__file__).resolve().parent.parent
GRID = {"svr__C": [1, 10, 100], "svr__gamma": ["scale", 0.01, 0.001]}
TAIL_THRESHOLD = 20.0


def element_groups(formulas):
    """Match scripts/make_splits.py: ignore stoichiometry and element order."""
    return np.array([
        "-".join(sorted(el.symbol for el in Composition(f).elements))
        for f in formulas
    ])


def magpie_features(formulas):
    """All 22 properties x six statistics; no B,G, target, or SR exclusions."""
    ep = ElementProperty.from_preset("magpie", impute_nan=False)
    ep.set_n_jobs(1)
    features = ep.featurize_many(
        [Composition(f) for f in formulas], ignore_errors=False, pbar=False
    )
    return pd.DataFrame(features, columns=ep.feature_labels(), dtype=float)


def select_modulus_model(X, y, groups):
    """Select by mean fold modulus MAE, then refit on the complete train split."""
    pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median", keep_empty_features=True)),
        ("scaler", StandardScaler()),
        ("svr", SVR(kernel="rbf", epsilon=0.1, tol=0.001)),
    ])
    search = GridSearchCV(
        pipeline, GRID, scoring="neg_mean_absolute_error",
        cv=GroupKFold(n_splits=5), n_jobs=1, refit=True, error_score="raise",
    )
    search.fit(X, y, groups=groups)
    return search


def positive_moduli(B, G):
    B, G = np.asarray(B, dtype=float), np.asarray(G, dtype=float)
    if not (np.isfinite(B).all() and np.isfinite(G).all()
            and (B > 0).all() and (G > 0).all()):
        raise ValueError("B and G must be finite and positive; no clipping is applied")
    return B, G


def chen_hardness(B, G):
    # B enters squared: preserve the declared equation even for negative SVR B.
    B, G = np.asarray(B, dtype=float), np.asarray(G, dtype=float)
    if not (np.isfinite(B).all() and np.isfinite(G).all()
            and (B != 0).all() and (G >= 0).all()):
        raise ValueError("Chen requires finite nonzero B and nonnegative G; no clipping")
    return 2.0 * ((G / B) ** 2 * G) ** 0.585 - 3.0


def tian_hardness(B, G):
    B, G = positive_moduli(B, G)
    return 0.92 * (G / B) ** 1.137 * G ** 0.708


def mazhnik_oganov_hardness(B, G):
    """Mazhnik & Oganov (2019), doi:10.1063/1.5113622, Eqs. (10)-(11)."""
    B, G = positive_moduli(B, G)
    E = 9 * B * G / (3 * B + G)
    nu = (3 * B - 2 * G) / (2 * (3 * B + G))
    chi = (1 - 8.5 * nu + 19.5 * nu**2) / (
        1 - 7.5 * nu + 12.2 * nu**2 + 19.6 * nu**3
    )
    return 0.096 * chi * E


def metrics(y, pred):
    y, pred = np.asarray(y, dtype=float), np.asarray(pred, dtype=float)
    if pred.shape != y.shape or not np.isfinite(pred).all() or not np.isfinite(y).all():
        raise ValueError("Every row must have a finite target and prediction")
    tail = y >= TAIL_THRESHOLD
    error = np.abs(y - pred)
    return {
        "val_mae": float(error.mean()),
        "tail_mae": float(error[tail].mean()) if tail.any() else None,
        "n_val": len(y), "n_tail": int(tail.sum()),
    }


def append_results(path, rows):
    """Honor the on-disk ledger schema, including its existing search column."""
    with path.open(newline="") as f:
        header = next(csv.reader(f))
    if set(header) != set(rows[0]):
        raise ValueError(f"Unexpected ledger header: {header}")
    with path.open("a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writerows(rows)


def render_report(results, searches, train, val, X, prediction_checks, run_id, timestamp, branch):
    groups = element_groups(train.formula)
    val_groups = element_groups(val.formula)
    lines = [
        "# Baselines on the validation development set", "",
        f"Run `{run_id}`; {timestamp}; branch `{branch}`.", "",
        "All errors are MAE in GPa against `hv_chen`, a Chen proxy derived from DFT",
        "elastic moduli, not measured hardness. Val has been reused during formula",
        "development; these are descriptive development-set comparisons.", "",
        "| Baseline | Inputs at inference | Overall MAE | MAE for target >= 20 GPa |",
        "|---|---|---:|---:|",
    ]
    for result in results:
        tail = result["tail_mae"]
        tail_text = "n/a (empty subset)" if tail is None else f"{tail:.6f}"
        lines.append(
            f"| {result['label']} | {result['inputs']} | {result['val_mae']:.6f} | {tail_text} |"
        )
    lines += [
        "", f"Train: {len(train)} rows / {len(set(groups))} element-set groups. "
        f"Val: {len(val)} rows / {len(set(val_groups))} groups; "
        f"{results[0]['n_tail']} rows have **true target** `hv_chen >= 20`.", "",
        "## Exact fixed protocol", "",
        "1. Read only `data/splits/train.csv` and `data/splits/val.csv`. Keep every row,",
        "   including negative Chen targets. Reject nonfinite labels/predictions and",
        "   nonpositive true DFT moduli. Do not clip hardness. Verify train/val",
        "   element-set groups are disjoint. No split files are changed.",
        "2. From formulas alone, use matminer `ElementProperty.from_preset('magpie',",
        "   impute_nan=False)`: all **132 features**, 22 elemental properties times",
        "   minimum, maximum, range, mean, average deviation, and mode. Include all",
        "   properties (also MeltingT and SpaceGroupNumber); no SR exclusions or",
        "   descriptor modules. Element tables are fixed, not learned from this dataset.",
        "3. Each estimator is `SimpleImputer(strategy='median', keep_empty_features=True)`",
        "   -> `StandardScaler()` -> `SVR(kernel='rbf', epsilon=0.1, tol=0.001)`.",
        "   Median imputation and scaling are fitted inside each training fold; an",
        "   entirely missing training column is filled with zero. No target scaling.",
        "4. Fit bulk_modulus and shear_modulus separately in GPa. For each, select",
        "   C in `[1, 10, 100]` and gamma in `['scale', 0.01, 0.001]` by",
        "   `GridSearchCV(scoring='neg_mean_absolute_error', cv=GroupKFold(5),",
        "   n_jobs=1, refit=True)`. Groups are the sorted unique element symbols",
        "   joined with `-`, exactly as in `scripts/make_splits.py`; folds are",
        "   deterministic, unshuffled, and identical for B and G. Minimize the",
        "   unweighted mean of the five held-out **modulus** MAEs. Ties take the first",
        "   grid candidate in the stated order. All other SVR defaults are unchanged.",
        "   The selected pipeline is refitted on all train rows. Val is read only",
        "   after both model selections/refits; no val-based selection is performed.",
        "5. Predict B and G from val formulas and apply the declared Chen equation",
        "   directly, with no clipping or positivity projection. Unconstrained SVR",
        "   can predict nonphysical negative moduli. Negative B still gives a real",
        "   Chen value because B enters squared; retain it and report its count.",
        "   Zero B or negative G would make Chen undefined; fail rather than drop",
        "   rows or invent a prediction. Keep all negative hardness outputs.",
        "   This is a simple **Tehrani-2018-style composition-only baseline**, not an",
        "   exact reproduction of the paper or an extensively tuned competitor.",
        f"6. Constants are train `hv_chen` mean = {train.hv_chen.mean():.12g} and",
        f"   median = {train.hv_chen.median():.12g}; neither uses val labels to fit.",
        "7. Compute all three elastic formulas from **true val DFT B,G** separately.",
        "   These are **oracle / privileged-input upper bounds**, not composition-only",
        "   baselines. Only Chen is an exact target-reconstruction bound. Tian and",
        "   Mazhnik–Oganov are oracle-input comparators, not guaranteed mathematical",
        "   error bounds. Their error against Chen labels cannot rank physical accuracy.",
        "8. Report row-weighted overall MAE and MAE restricted by true `hv_chen >= 20`,",
        "   using the same rows for every method. No rounding precedes scoring.", "",
        "## Elastic formulas", "",
        "All B, G, E and H values are in GPa; k = G/B.", "",
        "- Chen (2011): `H = 2 (k^2 G)^0.585 - 3`.",
        "- Tian (2012): `H = 0.92 k^1.137 G^0.708`.",
        "- Mazhnik–Oganov (2019): `E = 9BG/(3B+G)`, `nu = (3B-2G)/(2(3B+G))`,",
        "  `chi = (1-8.5nu+19.5nu^2)/(1-7.5nu+12.2nu^2+19.6nu^3)`,",
        "  `H = 0.096 chi E`. See [original paper, Eqs. 10–11](https://uspex-team.org/static/file/mazhnik2019.pdf).",
        "", "## Train-only model selection", "",
        "| Modulus | Selected C | Selected gamma | Mean CV modulus MAE (GPa) |",
        "|---|---:|---|---:|",
    ]
    for target, search in searches.items():
        params = search.best_params_
        lines.append(f"| {target} | {params['svr__C']} | {params['svr__gamma']} | {-search.best_score_:.6f} |")
    lines += ["", "All fixed grid candidates (mean of five fold MAEs, GPa):", "",
              "| C | gamma | B CV MAE | G CV MAE |", "|---:|---|---:|---:|"]
    b_cv, g_cv = [search.cv_results_ for search in searches.values()]
    for i, params in enumerate(b_cv["params"]):
        lines.append(f"| {params['svr__C']} | {params['svr__gamma']} | "
                     f"{-b_cv['mean_test_score'][i]:.6f} | {-g_cv['mean_test_score'][i]:.6f} |")
    folds = GroupKFold(5).split(X, groups=groups)
    lines += ["", "CV held-out fold sizes (rows / element-set groups): " + ", ".join(
        f"{len(idx)} / {len(set(groups[idx]))}" for _, idx in folds
    ) + ".", "", "## Reproduce and provenance", "", "```bash",
        f"uv sync --frozen\nuv run python eval/baselines.py --run-id {run_id}", "```", "",
        "Each invocation appends six rows to `ledger/results.csv` using its existing",
        "header: `descriptor_set=baseline_<name>`, `complexity=0`, `search=baseline`,",
        "`split=val`, `val_mae` = overall MAE. JSON `notes` store tail MAE, subset",
        "counts, oracle labels, and selected SVR parameters. Reruns append a new block",
        "and overwrite this report; they do not deduplicate prior ledger rows.", "",
    ]
    for name in ("train", "val"):
        path = ROOT / f"data/splits/{name}.csv"
        lines.append(f"- `{path.relative_to(ROOT)}` SHA256: `{hashlib.sha256(path.read_bytes()).hexdigest()}`")
    lines.append("- Versions: " + ", ".join(
        f"{package} {version(package)}" for package in ("numpy", "pandas", "scikit-learn", "matminer", "pymatgen")
    ) + ".")
    lines.append(f"- Raw nonfinite feature entries before fold-local imputation: train {int((~np.isfinite(X)).to_numpy().sum())}.")
    lines.append("- Raw predicted-modulus diagnostics on val (no clipping): " + json.dumps(prediction_checks, sort_keys=True) + ".")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", default="baseline_v1")
    args = parser.parse_args()
    train = pd.read_csv(ROOT / "data/splits/train.csv")
    positive_moduli(train.bulk_modulus, train.shear_modulus)
    if not np.isfinite(train.hv_chen).all():
        raise ValueError("Nonfinite training targets")
    groups = element_groups(train.formula)
    X = magpie_features(train.formula)
    searches = {}
    for target in ("bulk_modulus", "shear_modulus"):
        search = select_modulus_model(X, train[target], groups)
        searches[target] = search
        print(f"{target}: {search.best_params_}; CV MAE = {-search.best_score_:.6f} GPa", flush=True)

    # Model selection/refitting is finished before validation is even loaded.
    val = pd.read_csv(ROOT / "data/splits/val.csv")
    if set(groups) & set(element_groups(val.formula)):
        raise ValueError("Train/val element-set group leakage")
    X_val = magpie_features(val.formula)
    raw_predictions = {target: search.predict(X_val) for target, search in searches.items()}
    prediction_checks = {
        target: {"n_nonpositive": int((pred <= 0).sum()), "minimum_raw_GPa": float(pred.min())}
        for target, pred in raw_predictions.items()
    }
    B_pred, G_pred = raw_predictions.values()
    B, G = val.bulk_modulus, val.shear_modulus
    predictions = [
        ("tehrani2018_svr", "Tehrani-style Magpie → SVR(B,G) → Chen", "Composition only", chen_hardness(B_pred, G_pred)),
        ("mean", "Train mean", "Train target constant", np.full(len(val), train.hv_chen.mean())),
        ("median", "Train median", "Train target constant", np.full(len(val), train.hv_chen.median())),
        ("oracle_chen", "Oracle upper bound: Chen (2011)", "True DFT B,G", chen_hardness(B, G)),
        ("oracle_tian2012", "Oracle upper bound: Tian (2012)", "True DFT B,G", tian_hardness(B, G)),
        ("oracle_mazhnik_oganov2019", "Oracle upper bound: Mazhnik–Oganov (2019)", "True DFT B,G", mazhnik_oganov_hardness(B, G)),
    ]
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip()
    results, rows = [], []
    for name, label, inputs, prediction in predictions:
        result = {"name": name, "label": label, "inputs": inputs, **metrics(val.hv_chen, prediction)}
        results.append(result)
        notes = {**result, "oracle": name.startswith("oracle_")}
        if name == "tehrani2018_svr":
            notes["raw_modulus_diagnostics"] = prediction_checks
            notes["selected"] = {target: {**search.best_params_, "cv_mae": -search.best_score_}
                                 for target, search in searches.items()}
        rows.append({
            "run_id": args.run_id, "timestamp": timestamp, "branch": branch,
            "descriptor_set": f"baseline_{name}", "split": "val", "complexity": 0,
            "val_mae": f"{result['val_mae']:.6f}", "formula": label,
            "notes": json.dumps(notes, sort_keys=True), "search": "baseline",
        })
        print(f"{label}: MAE = {result['val_mae']:.6f}; tail MAE = {result['tail_mae']}")
    report = render_report(results, searches, train, val, X, prediction_checks, args.run_id, timestamp, branch)
    append_results(ROOT / "ledger/results.csv", rows)
    (ROOT / "wiki/BASELINES.md").write_text(report)
    print("Appended six ledger rows and wrote wiki/BASELINES.md")


if __name__ == "__main__":
    main()
