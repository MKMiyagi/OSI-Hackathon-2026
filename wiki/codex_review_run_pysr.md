# Codex review: sr/run_pysr.py (scaffold) — thread 01a15b9c-73f2-7800-8aac-a73906365ffc

Reviewer: gpt-6-astra (ultra). Brief: RESEARCH_REVIEW_RUN_PYSR.md. Not run end-to-end (train.csv absent).

Findings, all addressed in the scaffold (none touch metric or splits):
1. P1: descriptor Series index dropped (`reset_index(drop=True).values`) -> silent row misalignment. Fixed: index must equal df.index, else error.
2. P2: template promises `df["m_*"]` and `comp` but runner didn't provide them. Fixed: compute() receives a view of comp + m_* only.
3. P2: nullable dtypes (Float64/pd.NA) broke np.isfinite. Fixed: coerce to float before masking.
4. Minor: zero finite rows now fails before fit (e.g. d_000 placeholder).
Leakage: only train.csv is read; compute() no longer sees target/moduli columns (earlier it did).

Correct per reviewer: NaN row masking, sympy-safe m_* names (22 pass PySR validator), Chen target formula.

Open caveat (not acted on): target hv_chen is Chen applied to DFT B,G, so "beating Chen" against Chen-derived labels is circular. A team decision for A/the user; not a code change.
