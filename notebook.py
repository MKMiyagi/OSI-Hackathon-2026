import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import re
    from pathlib import Path

    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import sympy as sp

    ROOT = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()
    REPO = "https://github.com/MKMiyagi/OSI-Hackathon-2026/blob/main"
    DEV = "development set (val, reused)"
    return DEV, REPO, ROOT, Path, mo, np, pd, plt, re, sp


@app.cell
def _(DEV, mo):
    mo.md(
        f"""
        # hardness-law: compact formulas for the DFT-derived Chen proxy

        **DRAFT for T2.** Target is `hv_chen` (Chen 2011 applied to DFT B, G), not measured hardness. Every MAE below
        is a **{DEV}** number: val was used to choose descriptors, equations and complexity windows, so none is a
        held-out estimate. No formula here is established as a physical law.
        """
    )
    return


@app.cell
def _(ROOT, mo, pd):
    # (a) ledger, without smoke searches and without MeltingT / SpaceGroupNumber formulas
    _raw = pd.read_csv(ROOT / "ledger/results.csv")
    _unphysical = _raw.formula.astype(str).str.contains("MeltingT|SpaceGroup")
    ledger = _raw[(_raw.search != "smoke") & ~_unphysical & (_raw.complexity > 0)].copy()
    mo.md(
        f"Ledger: {len(_raw)} rows read; kept **{len(ledger)}** Pareto rows from "
        f"{ledger.run_id.nunique()} runs and {ledger.descriptor_set.nunique()} descriptor sets "
        f"(dropped {int((_raw.search == 'smoke').sum())} smoke rows, {int(_unphysical.sum())} rows using "
        "m_MeltingT or m_SpaceGroupNumber, and complexity-0 constant rows)."
    )
    return (ledger,)


@app.cell
def _(ledger, mo):
    highlight = mo.ui.multiselect(
        options=sorted(ledger.descriptor_set.unique()),
        value=["magpie_only", "d_008", "d_018"],
        label="highlight descriptor sets",
    )
    highlight
    return (highlight,)


@app.cell
def _(DEV, highlight, ledger, plt):
    # (b) Pareto plot: best val_mae at each complexity, per descriptor set
    REF_RUNS = [f"v008_wo_s{i}" for i in range(5)] + [f"ref_s{i}" for i in range(5, 9)]
    # val MAE of non-formula comparators. SVR: eval/tehrani_baseline.py (T1, 2.82) and the frozen
    # eval/baselines.py protocol on m/baseline (baseline_v1, 2.905). Oracle rows use TRUE DFT B,G.
    LINES = [
        ("Magpie SVR -> B,G -> Chen (T1 tehrani_baseline)", 2.82, "--"),
        ("Magpie SVR -> B,G -> Chen (baseline_v1 protocol)", 2.905, ":"),
        ("train median constant", 5.044, "--"),
        ("oracle Tian (true B,G)", 1.142, "-."),
        ("oracle Mazhnik-Oganov (true B,G)", 3.126, "-."),
    ]

    _fig, _ax = plt.subplots(figsize=(10, 6))
    _best = ledger.groupby(["descriptor_set", "complexity"]).val_mae.min().reset_index()
    _cmap = plt.get_cmap("tab10")
    _n = 0
    for _name, _g in _best.groupby("descriptor_set"):
        _g = _g.sort_values("complexity")
        if _name in highlight.value:
            _ax.plot(_g.complexity, _g.val_mae, "-o", ms=4, lw=1.8, color=_cmap(_n % 10), label=_name, zorder=5)
            _n += 1
        else:
            _ax.plot(_g.complexity, _g.val_mae, lw=0.7, color="0.75", zorder=2)
    _ax.plot([], [], lw=0.7, color="0.75", label="other descriptor sets")

    _ref = ledger[ledger.run_id.isin(REF_RUNS)].pivot_table(index="complexity", columns="run_id", values="val_mae")
    _ref = _ref[_ref.notna().sum(axis=1) >= 5]
    _ax.fill_between(_ref.index, _ref.min(axis=1), _ref.max(axis=1), color="tab:blue", alpha=0.18, lw=0, zorder=3,
                     label="Magpie-only reference, 9 seeds (range)")

    for _label, _y, _ls in LINES:
        _ax.axhline(_y, color="0.35", lw=1, ls=_ls, zorder=1)
        _ax.text(15.4, _y + 0.03, f"{_label}  {_y:.3g}", ha="right", va="bottom", fontsize=8, color="0.3")
    _ax.set_xlim(0.5, 15.6)
    _ax.set_ylim(0.9, 5.6)
    _ax.set_xticks(range(1, 16))
    _ax.set_xlabel("formula complexity (PySR nodes)")
    _ax.set_ylabel("val MAE vs hv_chen (GPa)")
    _ax.set_title(f"Best val MAE vs complexity per descriptor set; {DEV}")
    _ax.legend(frameon=False, fontsize=8, loc="upper right", bbox_to_anchor=(1.0, 0.88))
    for _s in ("top", "right"):
        _ax.spines[_s].set_visible(False)
    _fig.tight_layout()
    _ax
    return LINES, REF_RUNS


@app.cell
def _(REPO, ROOT, mo, re, sp):
    # (c) candidate formulas from wiki/CANDIDATE_FORMULAS.md, rendered with sympy LaTeX
    _text = (ROOT / "wiki/CANDIDATE_FORMULAS.md").read_text()
    _rows = []
    _window = None
    for _line in _text.splitlines():
        _m = re.match(r"## Best 5 at complexity <= (\d+)", _line)
        if _m:
            _window = int(_m.group(1))
        _cells = [c.strip() for c in _line.strip().strip("|").split(" | ")]
        if _window and len(_cells) >= 6 and _cells[0].isdigit():
            _eq = re.search(r"`([^`]+)`", _cells[5])
            _rows.append((_window, _cells[0], _cells[1], _cells[2], _cells[3], _cells[4], _eq.group(1) if _eq else ""))


    def to_latex(expr):
        # identifiers become upright symbols so m_NdValence does not render as a subscript
        _idents = set(re.findall(r"[A-Za-z_][A-Za-z_0-9]*", expr)) - {"exp", "sqrt", "log"}
        _local = {i: sp.Symbol(r"\mathrm{" + i.replace("_", r"\_") + "}") for i in _idents}
        try:
            return sp.latex(sp.sympify(expr, locals=_local, evaluate=False))
        except Exception:  # fall back to the raw string rather than hiding a row
            return r"\text{" + expr.replace("_", r"\_") + "}"


    _table = [
        "| c<= | # | run | c | val MAE (dev. set) | descriptors | formula (GPa, fitted constants) |",
        "|---|---|---|---|---|---|---|",
    ]
    for _w, _n, _run, _c, _mae, _desc, _eq in _rows:
        _table.append(f"| {_w} | {_n} | {_run} | {_c} | {_mae} | {_desc} | ${to_latex(_eq)}$ |")
    mo.md(
        "### Candidate formulas\n\n"
        f"Source: [`wiki/CANDIDATE_FORMULAS.md`]({REPO}/wiki/CANDIDATE_FORMULAS.md). MAEs are **development set (val, "
        "reused)**. Physical readings and units notes are in that file; two Gao-style readings were removed there "
        "because electron count sits in the denominator.\n\n" + "\n".join(_table)
    )
    return (to_latex,)


@app.cell
def _(DEV, ROOT, mo, pd, plt):
    # (d) nested CV, per-fold MAE by arm (files only exist once the nested-CV run is merged)
    _files = sorted((ROOT / "ledger/nested_cv").glob("*.csv"))
    ncv_out = None
    if not _files:
        ncv_out = mo.md(
            "### Nested grouped CV\n\n`ledger/nested_cv/*.csv` not present on this branch (lives on `m/nested-cv`). "
            "This cell will plot per-fold MAE by arm once it is merged."
        )
    else:
        _ncv = pd.concat([pd.read_csv(f).assign(file=f.stem) for f in _files], ignore_index=True)
        _ncv = _ncv[_ncv.window == 12]
        _arms = list(dict.fromkeys(_ncv.arm))
        _fig, _ax = plt.subplots(figsize=(9, 5))
        for _i, _arm in enumerate(_arms):
            _a = _ncv[_ncv.arm == _arm].groupby("fold").test_mae.mean()
            _ax.plot(_a.index + 0.08 * (_i - len(_arms) / 2), _a.values, "o-", lw=1.2, label=_arm)
        _ax.set_xlabel("outer fold (element-set grouped, train+val)")
        _ax.set_ylabel("outer-fold MAE (GPa)")
        _ax.set_xticks(sorted(_ncv.fold.unique()))
        _ax.set_title(f"Per-fold MAE by arm, c<=12; {DEV}: nested CV over train+val")
        _ax.legend(frameon=False, fontsize=8)
        for _s in ("top", "right"):
            _ax.spines[_s].set_visible(False)
        _fig.tight_layout()
        ncv_out = _ax
    ncv_out
    return


@app.cell
def _(REPO, mo):
    # (e) what the reviewer caught
    _w = f"{REPO}/wiki"
    mo.md(
        f"""
        ### What the reviewer caught

        The cross-model reviewer (Codex) ran after every cycle. Five corrections that changed what we claim:

        1. **The c<=9 score was saturated.** All 9 no-descriptor reference seeds returned the same equation (val 4.1946 to
           4.1949), so "improvement" only measured whether a descriptor displaced it. Replaced by a 3-seed headline at
           c<=12 against a stored 9-seed reference. [`DECISIONS.md`]({_w}/DECISIONS.md), [`OVERNIGHT_3_SUMMARY.md`]({_w}/OVERNIGHT_3_SUMMARY.md)
        2. **Two "Gao-like electron-density" readings were algebraically wrong.** `1494/(Row*NValence*V)` and
           `642/(V*(NValence-NfValence))` have electron count in the denominator. Readings removed.
           [`RESEARCH_REVIEW_3_VERDICT.md`]({_w}/RESEARCH_REVIEW_3_VERDICT.md), [`CANDIDATE_FORMULAS.md`]({_w}/CANDIDATE_FORMULAS.md)
        3. **"Beats Chen" is incoherent on this target.** Labels reproduce Chen's formula to float precision, and
           "Magpie ceiling" was never a bound. Reframed as an emulator; wording changed to "best observed under this search
           configuration". [`DECISIONS.md`]({_w}/DECISIONS.md), [`RESEARCH_REVIEW_3_VERDICT.md`]({_w}/RESEARCH_REVIEW_3_VERDICT.md)
        4. **The declared baseline did not exist.** Only constant predictors were implemented; the composition -> B,G -> Chen
           pipeline was added afterwards, plus a train-median comparator.
           [`RESEARCH_REVIEW_3_VERDICT.md`]({_w}/RESEARCH_REVIEW_3_VERDICT.md), [`PROGRESS_EVAL.md`]({_w}/PROGRESS_EVAL.md)
        5. **The best c12 result (3.772) was fragile.** 94.7% of its gain over the Magpie c12 equation comes from ten val
           rows, it adds eV to dimensionless counts, and removing the band-gap term erases the gain.
           [`INFLUENCE_c018.md`]({_w}/INFLUENCE_c018.md), [`cycle_log.md`]({_w}/cycle_log.md)
        """
    )
    return


if __name__ == "__main__":
    app.run()
