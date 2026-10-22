"""SVR-vs-formula-vs-literature figures F1-F7 -> wiki/figures/svr_f*.{png,svg} (light and _dark) + ledger/figdata_*.csv.

Usage: uv run python scripts/figures_svr.py

Inputs (all existing artefacts; val only, the test file is never read):
  ledger/baseline_val_preds.csv   SVR B, G, Hv predictions on val (eval/metrics_extra.py refit of eval/tehrani_baseline.py)
  ledger/bg_errors.csv            equations of the symbolic B runs (T1's t1_B_s*, t1_Bd23_s*), re-evaluated here
  ledger/results.csv              every Pareto row of the 9-seed Magpie-only arm and of c020_s0-2 (d_023)
  ledger/nested_cv/ncv_d023.csv   nested grouped CV, one fit per (fold, arm), windows c<=9/12/15
  eval/residuals_d023.py          family rules and the d_023 c8 / c5 formulas
Hv headline quantities are pre-registered (wiki/DECISIONS.md): MAE and its gap-closed rewriting. NOT pre-registered, labelled
exploratory diagnostics in FIGURES.md and the captions: RMSE and R^2 of B and G (the quantities Tehrani 2018 publish, used only
to compare with them), per-family MAE (wiki/RESIDUALS_D023.md) and the F7 error scatter. No other metric is computed.
Published numbers used (each a row of the verification table in wiki/COMPARISON_TO_LITERATURE.md):
  Tehrani 2018 10-fold-CV RMSE B 17.2 / G 16.5 GPa, r^2 B 0.94 / G 0.84 (rows 5, 6), n = 2572 (row 2), 14 structural
  descriptors among 150 (row 3); Chen 2011 Eq. (11) (row 7); Mazhnik-Oganov 2019 Eqs. 7, 10, 11 (row 9). The Tian 2012
  coefficients could NOT be verified in the original paper (row 10), so the Tian oracle line is omitted.
Every Hv number is an error against hv_chen (Chen proxy from DFT B,G), never against measured hardness, and is never set
against a published measured-Hv error. All val numbers are development-set (val, reused) numbers.
"""
import json
import sys
import textwrap
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from eval.chen import chen_hardness  # noqa: E402
from eval.residuals_d023 import FAMILIES, FORMULAS, family  # noqa: E402
from eval.score import eval_equation  # noqa: E402
from eval.tehrani_baseline import element_group  # noqa: E402
from scripts.bg_errors import boot_ci, errs  # noqa: E402
from scripts.progress_plots import REF_RUNS, THEMES, legend, style  # noqa: E402
from sr.run_pysr import featurize  # noqa: E402

plt.rcParams["svg.fonttype"] = "none"  # keep text editable in the SVGs
OUT = ROOT / "wiki/figures"
LEDGER = ROOT / "ledger"
DEV = "development set (val, reused)"
NCV = "nested CV (train+val folds)"

# ---- published numbers (each is a verified row of wiki/COMPARISON_TO_LITERATURE.md, section 3) ----
PUB = dict(rmse_B=17.2, rmse_G=16.5, r2_B=0.94, r2_G=0.84, n=2572, n_struct=14)

# ---- our recorded baselines (wiki/DECISIONS.md, wiki/BASELINES.md) ----
ORACLE_RECORDED = {"Mazhnik-Oganov 2019": 3.125986}  # wiki/BASELINES.md, true DFT B,G -> Chen labels

FAM_LABEL = {"binary_CNB": "binary B/C/N", "oxide": "oxide", "pnictide_chalcogenide": "pnictide/chalcogenide",
             "intermetallic": "intermetallic", "other": "other"}
FAM_MARK = {"intermetallic": "s", "pnictide_chalcogenide": "^", "other": "v", "oxide": "o", "binary_CNB": "D"}
# categorical slots 1,2,3,4,5 of the reference palette, light / dark. Five hues do NOT pass the all-pairs validator
# (scripts/validate_palette.js), so family is also encoded by marker shape (secondary encoding); see the captions.
FAM_COL = {
    "light": {"intermetallic": "#2a78d6", "oxide": "#eb6834", "pnictide_chalcogenide": "#1baf7a", "other": "#eda100",
              "binary_CNB": "#e87ba4"},
    "dark": {"intermetallic": "#3987e5", "oxide": "#d95926", "pnictide_chalcogenide": "#199e70", "other": "#c98500",
             "binary_CNB": "#d55181"},
}
VIOLET = {"light": "#6250d6", "dark": "#9085e9"}


# =========================================================================================== data
def load_val():
    va = pd.read_csv(ROOT / "data/splits/val.csv")
    va, X = featurize(va, ["d_023"])
    va["family"] = [family(c) for c in va["comp"]]
    base = pd.read_csv(LEDGER / "baseline_val_preds.csv", index_col=0)
    assert len(base) == len(va)
    va["pred_const"] = base["train_median"].values
    va["pred_svr"] = base["svr_magpie_BG"].values
    for k, eq in FORMULAS.items():
        va[f"pred_{k}"] = eval_equation(eq, X)
    return va, X, base


def mae(a, b):
    return float(np.mean(np.abs(np.asarray(a) - np.asarray(b))))


def results_clean():
    r = pd.read_csv(LEDGER / "results.csv")
    return r[(r.complexity > 0) & ~r.formula.str.contains("MeltingT|SpaceGroup", na=False)].copy()


def envelope(r, run, cmax=15):
    g = r[r.run_id == run].groupby("complexity").val_mae.min().reindex(range(1, cmax + 1))
    return g.cummin().ffill()


def oracle_mae(va):
    """Mazhnik-Oganov 2019 (Eqs. 7, 10, 11; verification table row 9) from the TRUE val B,G, MAE vs hv_chen.
    Tian 2012 is deliberately not computed: its coefficients are unverified in the original paper (row 10)."""
    B, G = va.bulk_modulus.values, va.shear_modulus.values
    E = 9 * B * G / (3 * B + G)
    nu = (3 * B - 2 * G) / (2 * (3 * B + G))
    chi = (1 - 8.5 * nu + 19.5 * nu**2) / (1 - 7.5 * nu + 12.2 * nu**2 + 19.6 * nu**3)
    mo = 0.096 * chi * E
    out = {"Mazhnik-Oganov 2019": mae(va.hv_chen, mo)}
    for k_, v in out.items():
        assert abs(v - ORACLE_RECORDED[k_]) < 1e-4, (k_, v, ORACLE_RECORDED[k_])
    return out


def nested():
    d = pd.read_csv(LEDGER / "nested_cv/ncv_d023.csv")
    d = d[d.arm.isin(["median_const", "svr_baseline", "magpie", "magpie+d_023"])]
    return d.pivot_table(index=["arm", "window"], columns="fold", values="test_mae")


# =========================================================================================== plumbing
def save(fig, name, th, t):
    sfx = "" if th == "light" else "_dark"
    for ext, kw in (("png", dict(dpi=300)), ("svg", {})):
        fig.savefig(OUT / f"{name}{sfx}.{ext}", facecolor=t["surface"], **kw)
    plt.close(fig)


def headline(fig, t, head):
    fig.text(0.04, 0.985, head, color=t["text"], fontsize=12.6, fontweight="semibold", va="top")


def caption(fig, t, text, width=150, size=8.2):
    wrapped = textwrap.fill(text, width)
    fig.text(0.04, 0.012, wrapped, color=t["text2"], fontsize=size, va="bottom", ha="left", linespacing=1.35)
    return wrapped.count("\n") + 1


def panel_title(ax, t, text):
    ax.set_title(text, loc="left", fontsize=9.6, color=t["text"], fontweight="semibold", pad=8)


def fam_scatter(ax, df, xcol, ycol, th, t, s=30, legend_on=False):
    for fam in FAMILIES:
        g = df[df.family == fam]
        ax.scatter(g[xcol], g[ycol], s=s, marker=FAM_MARK[fam], color=FAM_COL[th][fam], edgecolor=t["surface"],
                   linewidth=0.6, alpha=0.95, zorder=3, label=f"{FAM_LABEL[fam]} (n = {len(g)})")
    if legend_on:
        legend(ax, t, loc="upper left")


def fam_legend(fig, ax, th, t, ncol=5, y=0.0):
    hs = [plt.Line2D([], [], ls="", marker=FAM_MARK[f], color=FAM_COL[th][f], markeredgecolor=t["surface"],
                     markersize=7, label=FAM_LABEL[f]) for f in FAMILIES]
    leg = fig.legend(handles=hs, loc="lower center", ncol=ncol, frameon=False, fontsize=8.8, bbox_to_anchor=(0.5, y))
    for txt in leg.get_texts():
        txt.set_color(t["text2"])


def stat_box(ax, t, text, loc="tl", size=8.6):
    x, y, ha, va = {"tl": (0.03, 0.97, "left", "top"), "br": (0.97, 0.03, "right", "bottom"),
                    "tr": (0.97, 0.97, "right", "top")}[loc]
    ax.text(x, y, text, transform=ax.transAxes, ha=ha, va=va, fontsize=size, color=t["text"], linespacing=1.4,
            bbox=dict(boxstyle="round,pad=0.35", facecolor=t["surface"], edgecolor=t["axis"], linewidth=0.8))


# =========================================================================================== F1
def moduli_table(va, base, X):
    """RMSE/R^2/95% cluster-bootstrap CI for the SVR variants and the symbolic B forms. Returns DataFrame (figdata_f1)."""
    groups = va.formula.map(element_group).values
    rows = []
    for tag, label in (("tehrani150", "SVR tehrani150 (150 feats, incl. 18 structural)"),
                       ("tehranicomp", "SVR tehrani_comp (132, composition-only)"),
                       ("magpie", "SVR Magpie (132, composition-only; Hv baseline)")):
        for q, col, tgt in (("B", f"svr_{tag}_B", "bulk_modulus"), ("G", f"svr_{tag}_G", "shear_modulus")):
            y, p = va[tgt].values, base[col].values
            rows.append(dict(model=label, kind="ours_svr", quantity=q, n=len(y), **errs(y, p), **boot_ci(y, p, groups),
                             source="ours, val"))
    # symbolic B forms (equations of T1's runs, stored in ledger/bg_errors.csv, re-evaluated on val)
    sr = pd.read_csv(LEDGER / "bg_errors.csv")
    sr = sr[sr.run_id != "baseline"]
    y = va.bulk_modulus.values
    idx = pd.Series(np.arange(len(y))).groupby(groups).apply(np.array).tolist()
    rng = np.random.default_rng(0)
    draws = [np.concatenate([idx[i] for i in rng.integers(0, len(idx), len(idx))]) for _ in range(2000)]

    def sym_row(label, preds, src):
        e = [errs(y, p) for p in preds]
        boots = np.array([np.mean([np.sqrt(np.mean((y[d] - p[d]) ** 2)) for p in preds]) for d in draws])
        lo, hi = np.percentile(boots, [2.5, 97.5])
        r2 = [np.percentile([1 - np.sum((y[d] - p[d]) ** 2) / np.sum((y[d] - y[d].mean()) ** 2) for d in draws], [2.5, 97.5])
              for p in preds]
        return dict(model=label, kind="ours_symbolic", quantity="B", n=len(y), mae=np.mean([x["mae"] for x in e]),
                    rmse=np.mean([x["rmse"] for x in e]), r2=np.mean([x["r2"] for x in e]), rmse_lo=lo, rmse_hi=hi,
                    r2_lo=np.mean([r[0] for r in r2]), r2_hi=np.mean([r[1] for r in r2]), source=src)

    r = sr[(sr.run_id == "t1_Bd23_s0") & (sr.complexity == 3)]
    assert len(r) == 1 and r.formula.iloc[0].startswith("d_023 *")
    rows.append(sym_row("symbolic B = 3.365 d_023 (c3)", [eval_equation(r.formula.iloc[0], X)],
                        "ours, val; T1 run t1_Bd23_s0 (3 seeds identical)"))
    preds = []
    for s in range(3):
        g = sr[(sr.run_id == f"t1_B_s{s}") & (sr.complexity <= 15)]
        preds.append(eval_equation(g.loc[g.mae.idxmin(), "formula"], X))
    rows.append(sym_row("symbolic B, Magpie only (best c<=15, mean of 3 seeds)", preds,
                        "ours, val; T1 runs t1_B_s0-2 (selected on val MAE: optimistic)"))
    t = pd.DataFrame(rows)
    chk = pd.read_csv(LEDGER / "bg_errors.csv")
    chk = chk[chk.run_id == "baseline"].set_index(["model", "quantity"])
    # published rows
    for q in ("B", "G"):
        rows_pub = dict(model="Tehrani 2018 as published (10-fold CV; 14 structural descriptors)", kind="published", quantity=q,
                        n=PUB["n"], mae=np.nan, rmse=PUB[f"rmse_{q}"], r2=PUB[f"r2_{q}"], rmse_lo=np.nan, rmse_hi=np.nan,
                        r2_lo=np.nan, r2_hi=np.nan,
                        source="Tehrani 2018, verification table rows 5/6 (wiki/COMPARISON_TO_LITERATURE.md)")
        t = pd.concat([t, pd.DataFrame([rows_pub])], ignore_index=True)
    # consistency with the committed table: SVR RMSEs must reproduce ledger/bg_errors.csv
    names = {"svr_tehrani150": "SVR tehrani150", "svr_tehranicomp": "SVR tehrani_comp", "svr_magpie": "SVR Magpie"}
    for _, c in chk.reset_index().iterrows():
        label = [m for k, m in names.items() if c.model.startswith(k)][0]
        mine = t[(t.model.str.startswith(label)) & (t.quantity == c.quantity)].iloc[0]
        assert abs(mine.rmse - c.rmse) < 5e-3, (label, c.quantity, mine.rmse, c.rmse)
        assert abs(mine.rmse_lo - c.rmse_lo) < 0.15 and abs(mine.rmse_hi - c.rmse_hi) < 0.15, (label, c.quantity)
    return t


def fig_f1(tab, th, t):
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 6.9), facecolor=t["surface"], sharey=True)
    fig.subplots_adjust(left=0.07, right=0.985, top=0.80, bottom=0.27, wspace=0.06)
    cols = {"ours_svr": t["series"][0], "ours_symbolic": t["series"][1]}
    for ax, q, tgt in zip(axes, ("B", "G"), ("bulk modulus B", "shear modulus G")):
        style(ax, t)
        d = tab[(tab.quantity == q) & (tab.kind != "published")].reset_index(drop=True)
        x = np.arange(len(d))
        for i, r in d.iterrows():
            c = cols[r.kind]
            ax.bar(i, r.rmse, width=0.62, color=c, linewidth=0, zorder=3)
            ax.errorbar(i, r.rmse, yerr=[[r.rmse - r.rmse_lo], [r.rmse_hi - r.rmse]], color=t["text"], capsize=3.5,
                        linewidth=1.2, zorder=4)
            ax.text(i, r.rmse_hi + 0.9, f"R² {r.r2:.2f}", ha="center", va="bottom", fontsize=8.8, color=t["text"])
            ax.text(i, 0.9, f"{r.rmse:.1f}", ha="center", va="bottom", fontsize=8.8, color=t["surface"], fontweight="semibold")
        pub = tab[(tab.quantity == q) & (tab.kind == "published")].iloc[0]
        ax.axhline(pub.rmse, color=t["text"], linewidth=1.3, linestyle=(0, (5, 3)), zorder=2)
        ph = plt.Line2D([], [], color=t["text"], linewidth=1.3, linestyle=(0, (5, 3)))
        lg = ax.legend([ph], [f"Tehrani 2018, as published: 10-fold-CV RMSE {pub.rmse:.1f} GPa (R² {pub.r2:.2f})"], loc="upper left",
                       frameon=False, fontsize=8.6, borderaxespad=0.6)
        lg.get_texts()[0].set_color(t["text"])
        ax.set_xticks(x)
        ax.set_xticklabels([textwrap.fill(m, 15) for m in d.model], fontsize=7.6)
        ax.set_ylim(0, 52)
        ax.set_xlim(-0.6, len(d) - 0.4)
        panel_title(ax, t, f"{'A' if q == 'B' else 'B'}. {tgt}: RMSE, {DEV}")
        if q == "G":
            ax.text(0.5, 0.55, "no symbolic G runs exist", transform=ax.transAxes, ha="center", fontsize=9,
                    color=t["muted"], style="italic")
        else:
            ax.set_ylabel("RMSE (GPa), bars with 95% cluster-bootstrap CI")
    axes[1].tick_params(labelleft=False)
    hs = [plt.Rectangle((0, 0), 1, 1, color=cols["ours_svr"]), plt.Rectangle((0, 0), 1, 1, color=cols["ours_symbolic"])]
    leg = fig.legend(hs, ["our SVR variants (log-target RBF-SVR)", "our symbolic B forms (T1 runs)"], loc="upper right",
                     bbox_to_anchor=(0.985, 0.865), frameon=False, fontsize=8.6, ncol=2)
    for txt in leg.get_texts():
        txt.set_color(t["text2"])
    headline(fig, t, "A structure-inclusive SVR lands near the published RMSE; composition-only SVRs are higher, symbolic B far higher")
    fig.text(0.04, 0.935, "tehrani150 uses the 150 features shipped with the dataset (18 structure-derived, not composition-only); scored on our grouped val split, not on theirs.",
             color=t["text2"], fontsize=9.5, va="top")
    caption(fig, t,
            f"Caption. Protocol differs: the published numbers are Tehrani et al. (2018)'s 10-fold cross-validation on n = {PUB['n']} moduli "
            f"(fold grouping not described in the paper); ours are single-split, element-set-grouped val, n = 374, so identical RMSE would not "
            f"mean identical difficulty. The published model uses {PUB['n_struct']} structural descriptors among its 150, so it is not "
            f"composition-only; only our Magpie and tehrani_comp arms are. RMSE and R² are exploratory diagnostics (not among the pre-registered Hv metrics), used here because the paper reports them. Bars: RMSE, whiskers: 95% cluster bootstrap (2000 draws over "
            f"element-set groups; for the 3-seed symbolic bar, the mean over the seeds' RMSEs). The symbolic Magpie-only equation is the "
            f"lowest-val-MAE one within c<=15 (optimistic); there are no symbolic G runs. The paper reports no MAE for B or G, so none is "
            f"compared. No published error is shown for Hv, and none of our hv_chen errors is compared with a measured-Hv error.", width=170)
    return fig


# =========================================================================================== F2
def fig_f2(va, base, th, t):
    fig, axes = plt.subplots(2, 2, figsize=(10.6, 11.4), facecolor=t["surface"])
    fig.subplots_adjust(left=0.075, right=0.985, top=0.885, bottom=0.185, hspace=0.30, wspace=0.17)
    models = [("magpie", "Magpie SVR, composition-only (the Hv baseline's B, G)"),
              ("tehrani150", "tehrani150 SVR (incl. 18 structure-derived features)")]
    rows = []
    for (r, (tag, mlabel)), letter in zip(enumerate(models), ("A", "C")):
        for c, (q, tgt, lim) in enumerate((("B", "bulk_modulus", 370), ("G", "shear_modulus", 250))):
            ax = axes[r, c]
            style(ax, t)
            ax.grid(axis="x", color=t["grid"], linewidth=0.8)
            d = pd.DataFrame(dict(y=va[tgt].values, p=base[f"svr_{tag}_{q}"].values, family=va.family.values))
            ax.plot([0, lim], [0, lim], color=t["muted"], linewidth=1, zorder=1)
            fam_scatter(ax, d, "y", "p", th, t, s=22)
            ax.set_xlim(0, lim)
            ax.set_ylim(0, lim)
            ax.set_aspect("equal")
            e = errs(d.y, d.p)
            stat_box(ax, t, f"RMSE {e['rmse']:.1f} GPa\nR² {e['r2']:.3f}", "tl")
            stat_box(ax, t, f"Tehrani 2018, published,\nfor reference only:\nR² {PUB[f'r2_{q}']:.2f} (10-fold CV, n = {PUB['n']})",
                     "br", size=7.8)
            ax.set_xlabel(f"true {q} (GPa)")
            ax.set_ylabel(f"predicted {q} (GPa)")
            panel_title(ax, t, f"{letter if c == 0 else chr(ord(letter) + 1)}. {q}, {mlabel.split(',')[0].split(' (')[0]}, {DEV}")
            for i in range(len(d)):
                rows.append(dict(model=tag, quantity=q, formula=va.formula.iloc[i], family=d.family.iloc[i], true=d.y.iloc[i],
                                 pred=d.p.iloc[i]))
    headline(fig, t, "SVR parity for B and G: composition-only (Magpie) vs the 150-feature tehrani150 model")
    fig.text(0.04, 0.945, "Top row: the moduli feeding the Hv baseline. Bottom row: Tehrani-style 150-feature set with structural features.",
             color=t["text2"], fontsize=9.5, va="top")
    fam_legend(fig, axes[1, 0], th, t, ncol=3, y=0.105)
    caption(fig, t,
            "Caption. Predicted vs true DFT modulus on the 374 val rows (element-set grouped split, reused for development). Points are coloured and "
            "shaped by chemical family (rules of wiki/RESIDUALS_D023.md; five hues do not separate under all colour-vision types, so marker shape "
            "carries family too). The published R² (Tehrani 2018, 10-fold CV on n = 2572, 14 structural descriptors) is quoted for reference only: "
            "different protocol and sample. RMSE and R² are exploratory diagnostics, not pre-registered metrics. The published RMSE is shown in F1, not here.", width=150)
    return fig, pd.DataFrame(rows)


# =========================================================================================== F3 / F6 tables
def family_mae(va, cols):
    rows = []
    for fam in FAMILIES + ["ALL"]:
        s = va if fam == "ALL" else va[va.family == fam]
        r = dict(family=fam, n=len(s))
        for c in cols:
            r[f"mae_{c}"] = mae(s[f"pred_{c}"], s.hv_chen)
        rows.append(r)
    return pd.DataFrame(rows)


def fig_f3(va, th, t):
    fig = plt.figure(figsize=(14.0, 8.9), facecolor=t["surface"])
    gs = fig.add_gridspec(2, 3, height_ratios=[3.1, 1.25], left=0.055, right=0.985, top=0.835, bottom=0.215, wspace=0.14,
                          hspace=0.25)
    preds = [("svr", "Magpie SVR (B, G -> Chen)"), ("c8", "d_023 c8 formula"), ("c5", "d_023 c5 formula")]
    tab = family_mae(va, [p for p, _ in preds])
    lim = (-8, 48)
    for j, (p, label) in enumerate(preds):
        ax = fig.add_subplot(gs[0, j])
        style(ax, t)
        ax.grid(axis="x", color=t["grid"], linewidth=0.8)
        ax.plot(lim, lim, color=t["muted"], linewidth=1, zorder=1)
        fam_scatter(ax, va.assign(pred=va[f"pred_{p}"]), "hv_chen", "pred", th, t, s=22)
        ax.set_xlim(*lim)
        ax.set_ylim(*lim)
        ax.set_aspect("equal")
        ax.set_xlabel("true hv_chen (GPa)")
        if j == 0:
            ax.set_ylabel("predicted (GPa)")
        panel_title(ax, t, f"{'ABC'[j]}. {label}\n{DEV}")
        stat_box(ax, t, f"MAE {tab.loc[tab.family == 'ALL', f'mae_{p}'].iloc[0]:.2f} GPa", "br")
        # per-family MAE table below the panel
        tx = fig.add_subplot(gs[1, j])
        tx.axis("off")
        tx.text(0.02, 1.0, f"{'family':<22}{'n':>4}{'MAE':>8}", family="monospace", fontsize=8.8, color=t["text2"], va="top",
                fontweight="semibold", transform=tx.transAxes)
        for i, r in tab.iterrows():
            nm = "all" if r.family == "ALL" else FAM_LABEL[r.family]
            if r.family != "ALL":
                tx.scatter([-0.01], [0.82 - i * 0.145], s=28, marker=FAM_MARK[r.family], color=FAM_COL[th][r.family],
                           transform=tx.transAxes, clip_on=False)
            tx.text(0.02, 0.89 - i * 0.145, f"{nm:<22}{int(r.n):>4}{r[f'mae_{p}']:>8.2f}", family="monospace", fontsize=8.8,
                    color=t["text"], va="top", transform=tx.transAxes,
                    fontweight="semibold" if r.family == "ALL" else "normal")
    headline(fig, t, "On val, the d_023 formulas have a larger positive oxide bias than the SVR")
    fig.text(0.04, 0.945, "Same val rows and axes in all three panels. Tables: MAE (GPa) vs hv_chen per chemical family.",
             color=t["text2"], fontsize=9.5, va="top")
    fam_legend(fig, None, th, t, ncol=5, y=0.115)
    caption(fig, t,
            "Caption. Predicted vs true hv_chen (Chen proxy from DFT B,G; not measured hardness) on the 374 val rows. Oxides have a positive mean signed error "
            "(prediction − hv_chen): +2.6 GPa for c8 and +3.0 GPa for c5, against +0.4 GPa for the SVR (wiki/RESIDUALS_D023.md). Rows above "
            "about 20 GPa are mostly underpredicted by all three models (signed errors for the formulas: wiki/RESIDUALS_D023.md). Families are coloured and shaped (marker shape carries family because "
            "five hues do not separate for every colour-vision type). Per-family MAE in the tables uses n per family as shown; the binary B/C/N family "
            "has only n = 14, so its MAE is imprecise. Per-family MAE and bias are exploratory diagnostics, not pre-registered. Development-set numbers: d_023 was screened on train and scored once on val before adoption.",
            width=170)
    return fig, tab


# =========================================================================================== F4 / F5
def pareto_data(r):
    arms = {"Magpie only (9 seeds)": REF_RUNS, "+ d_023 (3 seeds, c020)": [f"c020_s{i}" for i in range(3)]}
    rows = []
    for arm, runs in arms.items():
        for run in runs:
            e = envelope(r, run)
            for c, v in e.items():
                rows.append(dict(arm=arm, run_id=run, complexity=c, best_val_mae_le_c=v))
    return pd.DataFrame(rows)


def ncv_summary(nc):
    """Fold means (and ranges) of outer-fold MAE per arm and window; gap closed from the fold means (as NESTED_CV_D023.md)."""
    rows = []
    const, svr = nc.loc[("median_const", 9)], nc.loc[("svr_baseline", 9)]
    for (arm, w), f in nc.iterrows():
        gap_means = (const.mean() - f.mean()) / (const.mean() - svr.mean())
        per_fold = (const - f) / (const - svr)
        rows.append(dict(arm=arm, window=w, mae_mean=f.mean(), mae_sd=f.std(ddof=1), mae_min=f.min(), mae_max=f.max(),
                         gap_closed_foldmean=gap_means, gap_fold_min=per_fold.min(), gap_fold_max=per_fold.max(),
                         const_mean=const.mean(), svr_mean=svr.mean()))
    return pd.DataFrame(rows)


def fig_f4(pdat, ns, orc, svr_val, const_val, th, t):
    fig, ax = plt.subplots(figsize=(10.4, 9.0), facecolor=t["surface"])
    fig.subplots_adjust(left=0.075, right=0.975, top=0.855, bottom=0.44)
    style(ax, t)
    colors = {"Magpie only (9 seeds)": t["series"][0], "+ d_023 (3 seeds, c020)": t["series"][1]}
    for arm, g in pdat.groupby("arm", sort=False):
        pv = g.pivot(index="complexity", columns="run_id", values="best_val_mae_le_c")
        ax.fill_between(pv.index, pv.min(axis=1), pv.max(axis=1), color=colors[arm], alpha=0.18, linewidth=0, zorder=2)
        ax.plot(pv.index, pv.mean(axis=1), color=colors[arm], linewidth=2.2, zorder=4,
                label=f"val, {arm}: best val MAE at complexity <= c (mean, band = seed range)")
    # horizontal reference lines
    ax.axhline(const_val, color=t["muted"], linewidth=1, zorder=1)
    ax.text(15.5, const_val + 0.04, f"train-median constant (val)  {const_val:.2f}", ha="right", va="bottom", fontsize=8.6, color=t["text2"])
    ax.axhline(svr_val, color=t["text"], linewidth=1.3, zorder=1)
    ax.text(0.6, svr_val - 0.05, f"Magpie SVR (val)  {svr_val:.2f}", ha="left", va="top", fontsize=8.6, color=t["text"])
    for name, v, ha, x in (("Mazhnik-Oganov 2019", orc["Mazhnik-Oganov 2019"], "left", 0.6),):
        ax.axhline(v, color=t["muted"], linewidth=1, linestyle=(0, (4, 3)), zorder=1)
        ax.text(x, v + 0.04, f"{name} oracle (val)  {v:.2f}  (needs true B,G)", ha=ha, va="bottom", fontsize=8.6, color=t["text2"])
    # nested-CV fold means at c = 9 / 12 / 15
    sty = {"median_const": ("X", t["muted"], "nested CV, fold-median constant (its own comparator)"),
           "magpie": ("D", t["series"][0], "nested CV, Magpie only"), "magpie+d_023": ("D", t["series"][1], "nested CV, + d_023"),
           "svr_baseline": ("*", t["text"], "nested CV, within-fold Magpie SVR (its own comparator; no complexity axis)")}
    for arm, (m, c, lab) in sty.items():
        g = ns[ns.arm == arm].sort_values("window")
        ax.errorbar(g.window + (0.18 if arm == "magpie+d_023" else -0.18 if arm == "magpie" else 0), g.mae_mean, yerr=g.mae_sd,
                    fmt=m, ms=8.5 if m == "D" else 10 if m == "X" else 12, mfc=t["surface"] if m == "D" else c, mec=c, mew=1.8, color=c, ecolor=c,
                    elinewidth=1, capsize=2.5, zorder=6, label=f"{lab}: fold mean ± fold sd, c<=9/12/15")
    ax.set_xlim(0.5, 15.9)
    ax.set_ylim(2.0, 5.5)
    ax.set_xticks(range(1, 16))
    ax.set_xlabel("formula complexity (PySR nodes)")
    ax.set_ylabel("MAE vs hv_chen (GPa)")
    panel_title(ax, t, f"lines: {DEV};  markers: {NCV}")
    leg = ax.legend(frameon=False, fontsize=8.4, loc="upper center", bbox_to_anchor=(0.5, -0.11), ncol=1)
    for txt in leg.get_texts():
        txt.set_color(t["text2"])
    headline(fig, t, "At c<=9/12/15, formulas sit between the constant and the SVR, on val and in nested CV")
    fig.text(0.04, 0.935, "Hv error against hv_chen (DFT-derived Chen proxy), not measured hardness.", color=t["text2"], fontsize=9.5, va="top")
    caption(fig, t,
            "Caption. Lines: best val MAE among Pareto equations with complexity <= c (envelope selects on val, so optimistic), 9 Magpie-only seeds "
            "and the 3 d_023 seeds of cycle 020. Markers: outer-fold test MAE of the nested grouped CV (5 element-set folds on pooled train+val, "
            "one PySR fit per fold and arm, equation chosen on inner validation; windows c<=9/12/15; whiskers = sd across folds = fold "
            "heterogeneity, not optimizer uncertainty). The two evaluations use different rows (val: 374; nested: 2120 pooled), so their "
            "levels are comparable only roughly. The dashed oracle line applies the published Mazhnik-Oganov (2019) hardness model to the TRUE DFT B,G and "
            "scores it against the Chen-made labels: it needs the DFT moduli, is not composition-only and is not a physical-accuracy "
            "bound; the value is our computation. A Tian (2012) oracle line is omitted because its coefficients could not be verified in "
            "the original paper. The horizontal lines are val-only; the nested markers carry their own constant and SVR. The nested folds are an exploratory "
            "repartition conditional on the previously selected d_023 (descriptor choice was not nested; every held-out row had informed it), so "
            "they do not validate it independently. The SVR uses 132 Magpie statistics with separate log B and log G supervision; the formulas use 22 "
            "Magpie means (+ d_023) with hv_chen supervision, so the gap does not isolate formula compactness. The 9-seed and 3-seed bands are "
            "descriptive ranges of unequal samples, not comparable uncertainty intervals. At c = 1 the formulas are worse than the constant.", width=158)
    return fig


def fig_f5(pdat, ns, svr_val, const_val, th, t):
    fig, ax = plt.subplots(figsize=(10.0, 7.5), facecolor=t["surface"])
    fig.subplots_adjust(left=0.08, right=0.975, top=0.835, bottom=0.34)
    style(ax, t)
    colors = {"Magpie only (9 seeds)": t["series"][0], "+ d_023 (3 seeds, c020)": t["series"][1]}
    gap = lambda m: (const_val - m) / (const_val - svr_val)
    out = []
    for arm, g in pdat.groupby("arm", sort=False):
        pv = g.pivot(index="complexity", columns="run_id", values="best_val_mae_le_c").apply(gap)
        ax.fill_between(pv.index, pv.min(axis=1), pv.max(axis=1), color=colors[arm], alpha=0.18, linewidth=0, zorder=2)
        ax.plot(pv.index, pv.mean(axis=1), color=colors[arm], linewidth=2.2, zorder=4, label=f"val, {arm} (mean, band = seed range)")
        for run in pv.columns:
            for c in pv.index:
                out.append(dict(source="val", arm=arm, run_id=run, complexity=c, gap_closed=pv.loc[c, run]))
    ax.axhline(1.0, color=t["text"], linewidth=1.3, zorder=1)
    ax.text(0.7, 1.012, "1.0 = black box (Magpie SVR)", fontsize=8.8, color=t["text"], va="bottom")
    ax.axhline(0.0, color=t["muted"], linewidth=1, zorder=1)
    ax.text(9.6, 0.012, "0 = train-median constant", fontsize=8.8, color=t["text2"], va="bottom")
    sty = {"magpie": ("D", t["series"][0], "nested CV, Magpie only", -0.18), "magpie+d_023": ("D", t["series"][1], "nested CV, + d_023", 0.18)}
    for arm, (m, c, lab, dx) in sty.items():
        g = ns[ns.arm == arm].sort_values("window")
        ax.errorbar(g.window + dx, g.gap_closed_foldmean, yerr=[g.gap_closed_foldmean - g.gap_fold_min, g.gap_fold_max - g.gap_closed_foldmean],
                    fmt=m, ms=8.5, mfc=t["surface"], mec=c, mew=1.8, color=c, ecolor=c, elinewidth=1, capsize=2.5, zorder=6,
                    label=f"{lab}: gap closed from fold means, whiskers = per-fold range")
    # annotate 62%
    nd = ns[(ns.arm == "magpie+d_023") & (ns.window == 12)].iloc[0]
    assert round(nd.gap_closed_foldmean * 100) == 62
    ax.annotate(f"{nd.gap_closed_foldmean * 100:.0f}%  nested CV, + d_023, c<=12", (12.2, 0.63), xytext=(9.7, 0.93), color=t["text"],
                fontsize=9, ha="center", arrowprops=dict(arrowstyle="-", color=t["muted"], linewidth=0.9))
    v8 = gap(pdat[(pdat.arm == "+ d_023 (3 seeds, c020)") & (pdat.complexity == 8)].best_val_mae_le_c.mean())
    ax.annotate(f"{v8 * 100:.0f}%  val, + d_023, c<=8", (8.0, v8 + 0.01), xytext=(5.0, 0.80), color=t["text"], fontsize=9, ha="center",
                arrowprops=dict(arrowstyle="-", color=t["muted"], linewidth=0.9))
    ax.set_xlim(0.5, 15.9)
    ax.set_ylim(-0.12, 1.12)
    ax.set_xticks(range(1, 16))
    ax.set_xlabel("formula complexity (PySR nodes)")
    ax.set_ylabel("gap closed  (const − model) / (const − SVR)")
    panel_title(ax, t, f"lines: {DEV};  markers: {NCV}")
    leg = ax.legend(frameon=False, fontsize=8.4, loc="upper center", bbox_to_anchor=(0.5, -0.11), ncol=1)
    for txt in leg.get_texts():
        txt.set_color(t["text2"])
    headline(fig, t, f"With d_023, formulas close about {nd.gap_closed_foldmean * 100:.0f}% of the constant-to-SVR gap; Magpie-only about half")
    fig.text(0.04, 0.935, "Gap closed is a rewriting of MAE (wiki/DECISIONS.md), not a new metric. Target: hv_chen, not measured hardness.",
             color=t["text2"], fontsize=9.5, va="top")
    caption(fig, t,
            "Caption. Val: per seed, (constant − best-so-far val MAE)/(constant − SVR) with the train-median constant 5.04 and the Magpie SVR 2.84 "
            "(envelope selects on val: optimistic). Nested CV: the same ratio from fold-mean outer-fold MAEs, against the fold-mean median constant "
            "and the fold-mean within-fold SVR, as in wiki/NESTED_CV_D023.md; whiskers are the per-fold ratios' range. The val and nested "
            "levels use different constants, rows and selection, so agreement between them is descriptive and not independent corroboration. "
            "The nested folds are an exploratory repartition conditional on the previously selected d_023 (descriptor choice was not nested, every "
            "held-out row had informed it); they do not validate it independently. The SVR has different inputs and supervision (132 Magpie statistics, "
            "separate log B and log G) from the formulas (22 means + d_023, hv_chen), so the gap closed does not isolate formula compactness; the 9-seed "
            "and 3-seed bands are descriptive ranges of unequal samples.", width=148)
    return fig, pd.DataFrame(out)


# =========================================================================================== F6
def ref_c12_preds(va, X, r):
    """Per-seed best-val c<=12 Magpie-only equation (the headline selection), evaluated on val: list of (run, formula, pred)."""
    out = []
    for run in REF_RUNS:
        g = r[(r.run_id == run) & (r.complexity <= 12)]
        row = g.loc[g.val_mae.idxmin()]
        p = eval_equation(row.formula, X)
        assert abs(mae(va.hv_chen, p) - row.val_mae) < 1e-4, (run, mae(va.hv_chen, p), row.val_mae)
        out.append((run, int(row.complexity), row.formula, p))
    return out


def fig_f6(va, X, r, th, t):
    refs = ref_c12_preds(va, X, r)
    tab = family_mae(va, ["const", "svr", "c5", "c8"])
    ref_rows = []
    for fam in FAMILIES + ["ALL"]:
        m = np.array([mae(va.hv_chen[(va.family == fam) | (fam == "ALL")], p[((va.family == fam) | (fam == "ALL")).values])
                      for _, _, _, p in refs])
        ref_rows.append(dict(family=fam, mean=m.mean(), lo=m.min(), hi=m.max()))
    ref = pd.DataFrame(ref_rows)
    assert abs(ref.loc[ref.family == "ALL", "mean"].iloc[0] - 3.9802) < 5e-3  # reference mean c<=12 (CLAUDE.md)
    fig, ax = plt.subplots(figsize=(11.6, 6.9), facecolor=t["surface"])
    fig.subplots_adjust(left=0.07, right=0.985, top=0.835, bottom=0.31)
    style(ax, t)
    series = [("const", "train-median constant", t["context"]), ("svr", "Magpie SVR (black box)", t["text"]),
              ("c5", "d_023 c5 formula", t["series"][1]), ("c8", "d_023 c8 formula", VIOLET[th]),
              ("ref", "Magpie-only, best c<=12 (mean of 9 seeds, bars = range)", t["series"][0])]
    w, n = 0.16, len(series)
    data = []
    for i, (key, lab, col) in enumerate(series):
        x = np.arange(len(tab)) + (i - (n - 1) / 2) * (w + 0.012)
        v = ref["mean"].values if key == "ref" else tab[f"mae_{key}"].values
        ax.bar(x, v, width=w, color=col, linewidth=0, zorder=3, label=lab)
        if key == "ref":
            ax.errorbar(x, v, yerr=[v - ref.lo.values, ref.hi.values - v], fmt="none", ecolor=t["text"], elinewidth=1, capsize=2, zorder=4)
        for f, vv, nn in zip(tab.family, v, tab.n):
            data.append(dict(family=f, n=nn, method=lab, mae=vv, seed_min=ref.set_index("family").lo[f] if key == "ref" else np.nan,
                             seed_max=ref.set_index("family").hi[f] if key == "ref" else np.nan))
    ax.set_xticks(range(len(tab)))
    ax.set_xticklabels([("all" if f == "ALL" else FAM_LABEL[f]) + f"\n(n = {k})" for f, k in zip(tab.family, tab.n)], fontsize=9)
    ax.set_ylabel("MAE vs hv_chen (GPa)")
    panel_title(ax, t, f"{DEV}: MAE per chemical family")
    leg = ax.legend(frameon=False, fontsize=8.6, loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=3)
    for txt in leg.get_texts():
        txt.set_color(t["text2"])
    headline(fig, t, "Every family trails the SVR; the formulas' deficit is largest for oxides and binary B/C/N compounds")
    fig.text(0.04, 0.935, "Oxides: both d_023 formulas are worse than the constant. Target: hv_chen, not measured hardness.",
             color=t["text2"], fontsize=9.5, va="top")
    caption(fig, t,
            "Caption. Per-family MAE on the 374 val rows (reused development set). Family rules: wiki/RESIDUALS_D023.md; the binary B/C/N family has "
            "n = 14 and the oxide family n = 36, so those bars are imprecise. Magpie-only bars: each of the 9 reference seeds contributes its "
            "best-val equation at complexity <= 12 (the CLAUDE.md headline selection; mean 3.98 overall), the mean over seeds is drawn and the "
            "whiskers span the seeds. c5 and c8 are single equations from c020_s0 chosen as frozen candidates before the residual analysis; they "
            "are not seed-averaged, and d_023 was screened on train and scored once on val before adoption. Per-family MAE is an exploratory diagnostic, not "
            "pre-registered; the SVR and the formulas differ in inputs and supervision, so the deficit does not isolate formula compactness.", width=170)
    return fig, pd.DataFrame(data), tab, refs


# =========================================================================================== F7
def fig_f7(va, base, th, t):
    B, G = base["svr_magpie_B"].values, base["svr_magpie_G"].values
    d = va[["formula", "family", "hv_chen", "bulk_modulus", "shear_modulus"]].copy()
    d["hv_pred_via_chen"] = chen_hardness(G, B)
    assert abs(mae(d.hv_chen, d.hv_pred_via_chen) - mae(va.hv_chen, va.pred_svr)) < 1e-4
    d["B_pred"], d["G_pred"] = B, G
    d["err_hv"] = d.hv_pred_via_chen - d.hv_chen
    d["err_B"], d["err_G"] = B - d.bulk_modulus, G - d.shear_modulus
    # first-order (delta-method) propagation through Chen: Hv+3 = 2 G^1.755 B^-1.17  =>  dHv = 1.755 (Hv+3) dG/G - 1.17 (Hv+3) dB/B
    h3 = d.hv_chen + 3
    d["err_hv_linearised"] = 1.755 * h3 * d.err_G / d.shear_modulus - 1.17 * h3 * d.err_B / d.bulk_modulus
    fig, axes = plt.subplots(1, 3, figsize=(14.2, 6.1), facecolor=t["surface"])
    fig.subplots_adjust(left=0.06, right=0.985, top=0.74, bottom=0.30, wspace=0.26)
    spec = [("err_G", "G error: predicted − DFT (GPa)", "A. Hv error vs shear-modulus error", None),
            ("err_B", "B error: predicted − DFT (GPa)", "B. Hv error vs bulk-modulus error", None),
            ("err_hv_linearised", "linearised Chen propagation of B, G errors (GPa)",
             "C. Hv error vs the linearised Chen estimate", None)]
    for ax, (xc, xl, tt, _) in zip(axes, spec):
        style(ax, t)
        ax.grid(axis="x", color=t["grid"], linewidth=0.8)
        ax.axhline(0, color=t["muted"], linewidth=1, zorder=1)
        if xc != "err_hv_linearised":
            ax.axvline(0, color=t["muted"], linewidth=1, zorder=1)
        fam_scatter(ax, d, xc, "err_hv", th, t, s=22)
        ax.set_xlabel(xl)
        ax.set_ylabel("Hv error: SVR route − hv_chen (GPa)")
        panel_title(ax, t, f"{tt}\n{DEV}")
    lim = float(np.ceil(max(d.err_hv.abs().max(), d.err_hv_linearised.abs().max()) * 1.1 / 5) * 5)
    axes[2].plot([-lim, lim], [-lim, lim], color=t["muted"], linewidth=1, zorder=1)
    axes[2].set_xlim(-lim, lim)
    axes[2].set_ylim(-lim, lim)
    axes[2].set_aspect("equal")
    axes[0].text(0.03, 0.97, "Chen (2011), Eq. 11:\nHv = 2 (k² G)^0.585 − 3,  k = G/B\n⇒ Hv + 3 = 2 G^1.755 B^−1.17",
                 transform=axes[0].transAxes, ha="left", va="top", fontsize=8.4, color=t["text"], linespacing=1.4,
                 bbox=dict(boxstyle="round,pad=0.35", facecolor=t["surface"], edgecolor=t["axis"], linewidth=0.8))
    fam_legend(fig, None, th, t, ncol=5, y=0.135)
    headline(fig, t, "On the SVR route, Hv inherits the moduli errors through Chen's form")
    fig.text(0.04, 0.925, "Magpie SVR, composition → log B, log G → Chen. Errors are signed (prediction − DFT value).",
             color=t["text2"], fontsize=9.5, va="top")
    caption(fig, t,
            "Caption. One point per val row (n = 374, reused development set). A, B: signed Hv error (against hv_chen, the DFT-derived Chen proxy) "
            "against the signed error of the SVR's G and B. Over-predicted shear modulus tends to raise Hv, over-predicted bulk modulus tends to lower "
            "it at fixed G, and the two errors co-vary, so neither panel is expected to be a clean line. C: the same Hv errors against the first-order "
            "propagation of both modulus errors through Chen's Eq. (11) (derivatives evaluated at the true values), which is an algebraic consequence "
            "of the equation and not a fitted model; most rows lie close to the identity line, with a few departures (the largest is Sb2O3). "
            "No statistic is computed. Chen's equation is verified against the arXiv preprint (verification table row 7).", width=170)
    return fig, d.drop(columns=[])


# =========================================================================================== main
def main():
    OUT.mkdir(exist_ok=True)
    va, X, base = load_val()
    for k, expected in (("svr", 2.8391), ("c8", 3.6939), ("c5", 3.9077), ("const", 5.0442)):
        got = mae(va.hv_chen, va[f"pred_{k}"])
        assert abs(got - expected) < 5e-4, (k, got, expected)
    r = results_clean()
    svr_val, const_val = mae(va.hv_chen, va.pred_svr), mae(va.hv_chen, va.pred_const)
    orc = oracle_mae(va)
    nc = nested()
    ns = ncv_summary(nc)
    pdat = pareto_data(r)

    tab1 = moduli_table(va, base, X)
    tab1.to_csv(LEDGER / "figdata_f1_moduli_benchmark.csv", index=False, float_format="%.5g")

    for th, t in THEMES.items():
        save(fig_f1(tab1, th, t), "svr_f1_moduli_benchmark", th, t)
        fig, f2 = fig_f2(va, base, th, t)
        save(fig, "svr_f2_parity_moduli", th, t)
        fig, f3tab = fig_f3(va, th, t)
        save(fig, "svr_f3_parity_hv", th, t)
        save(fig_f4(pdat, ns, orc, svr_val, const_val, th, t), "svr_f4_pareto_blackbox", th, t)
        fig, f5 = fig_f5(pdat, ns, svr_val, const_val, th, t)
        save(fig, "svr_f5_gap_closed", th, t)
        fig, f6, f6tab, refs = fig_f6(va, X, r, th, t)
        save(fig, "svr_f6_family_mae", th, t)
        fig, f7 = fig_f7(va, base, th, t)
        save(fig, "svr_f7_error_propagation", th, t)

    f2.to_csv(LEDGER / "figdata_f2_parity_moduli.csv", index=False, float_format="%.5g")
    cols = ["formula", "family", "hv_chen", "pred_svr", "pred_c8", "pred_c5"]
    va[cols].to_csv(LEDGER / "figdata_f3_parity_hv.csv", index=False, float_format="%.5g")
    f3tab.to_csv(LEDGER / "figdata_f3_family_mae.csv", index=False, float_format="%.5g")
    p = pdat.copy()
    p["source"] = "val (development set, reused)"
    ns.assign(source="nested CV (train+val folds)").to_csv(LEDGER / "figdata_f4_nested_foldmeans.csv", index=False, float_format="%.5g")
    p.to_csv(LEDGER / "figdata_f4_pareto_val.csv", index=False, float_format="%.5g")
    refs_tab = pd.DataFrame(dict(name=["train-median constant (val MAE)", "Magpie SVR (val MAE)",
                                       "Mazhnik-Oganov 2019 oracle, true B,G (val MAE vs Chen labels)"],
                                 mae=[const_val, svr_val, orc["Mazhnik-Oganov 2019"]],
                                 source=["our computation", "our computation",
                                         "our computation; coefficients: verification table row 9 (Tian 2012 omitted, row 10 unverified)"]))
    refs_tab.to_csv(LEDGER / "figdata_f4_reference_lines.csv", index=False, float_format="%.5g")
    f5.to_csv(LEDGER / "figdata_f5_gap_closed_val.csv", index=False, float_format="%.5g")
    ns[["arm", "window", "gap_closed_foldmean", "gap_fold_min", "gap_fold_max", "const_mean", "svr_mean"]].assign(
        source="nested CV (train+val folds)").to_csv(LEDGER / "figdata_f5_gap_closed_nested.csv", index=False, float_format="%.5g")
    f6.to_csv(LEDGER / "figdata_f6_family_mae.csv", index=False, float_format="%.5g")
    pd.DataFrame([dict(run_id=a, complexity=b, formula=c) for a, b, c, _ in refs]).to_csv(
        LEDGER / "figdata_f6_magpie_only_c12_equations.csv", index=False)
    f7.to_csv(LEDGER / "figdata_f7_error_propagation.csv", index=False, float_format="%.5g")
    print(tab1[["model", "quantity", "rmse", "rmse_lo", "rmse_hi", "r2"]].round(3).to_string(index=False))
    print(ns.round(3).to_string(index=False))
    print(f3tab.round(2).to_string(index=False))
    print(refs_tab.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
