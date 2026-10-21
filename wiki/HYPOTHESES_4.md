# Hypotheses 4 — stoichiometry-aware bond-count descriptors (PROPOSED, not run)

Status: proposals only. Per wiki/RESEARCH_REVIEW_3_VERDICT.md, descriptor search on the train/val split is frozen. These are
meant to be evaluated **only inside eval/nested_cv.py** (descriptor fixed in advance as an extra arm, never chosen on outer
folds) or on genuinely new families. Nothing here has been implemented or scored. Signs are pre-registered below.

## Why this family
Every descriptor tried so far (d_001-d_018) is either a Magpie-style fraction-weighted mean or an extremum over elements
(e.g. chi range). Both are blind to **stoichiometry-dependent connectivity**: Ti2N, TiN and TiN2 share a Magpie element
list, and fraction-weighted means move smoothly with x but say nothing about how many bonds per atom exist or which kind
they are. Gao/Šimůnek-style hardness models are driven by bond density and bond type, so a composition-only proxy for those
is the most direct physically motivated gap. The target is Chen's proxy applied to DFT B,G (not measured Hv), so "physical"
here means "plausibly correlated with B,G," not validated against hardness.

## Shared conventions (frozen before any run)
- Inputs: `df["comp"]` only (pymatgen Composition). Element tables from pymatgen only; no target, B, G, or split info.
- Anion set (nonmetal acceptors): the more electronegative elements among {N, O, F, Cl, Br, I, S, Se, Te, P, As, C, B, Si, H}
  taken from the compound as those with Pauling chi >= 2.0, plus any element with chi >= 2.0 regardless of list. The
  threshold rule is declared here so it cannot be tuned. Cations/metals: every other element.
  H, B, C, Si, P, Ge, As are borderline (chi 1.8-2.2); the 2.0 cut is a convention, document misclassifications (Si 1.90
  counts as cation, B 2.04 and C 2.55 as anion). Also log the fraction of rows with no anion (intermetallics, elementals).
- Valence electrons per element v_i = group-based count (main group: group number minus 10 for p-block, 1-2 for s-block;
  transition metals: group number, i.e. d+s electrons). Use pymatgen `Element.group`; lanthanides/actinides fixed at 3 (declared).
- Bond-capacity estimate (for the "bonds per atom" family): each atom i offers b_i = min(v_i, 8 - v_i) for p-block elements
  (octet rule: covalent bonds an atom can form) and b_i = v_i for metals (all valence electrons delocalised). Declared, not tuned.

All fractions are atomic fractions x_i (sum 1). N = atoms per formula unit when normalizing.

## H4.1 Anion/cation fraction ratio — d_019
- Definition: R_ac = (sum of x_i over anions) / (sum of x_i over cations); define 0 when no anion, cap at 1e3 never needed
  (cations absent -> pure nonmetal compound; set R_ac = 10, declared).
- Rationale: stoichiometry in carbides/nitrides/borides sets whether the anion sublattice percolates into covalent
  networks (BN, B4C: R_ac high, hard) or sits as isolated interstitials in a metallic matrix (Ti2N, Mo2C: R_ac low, softer).
- Units: dimensionless. Expected sign: positive on Chen-proxy hardness, saturating, non-monotonic above ~1.5 (anion-anion
  bonds in peroxides/polysulfides are weak). If PySR picks it with a negative sign in the first nested-CV test, record as a
  failed pre-registration (cf. d_017).
- Beyond Magpie means: a Magpie mean of electronegativity or Number mixes the *identity* and *fraction* of every element and
  cannot separate "30% N in Ti" from "30% Ti in N" as a ratio of group sums; the ratio is a different nonlinear function of
  x that the +,-,*,/ search must otherwise assemble from several means at high complexity.

## H4.2 Estimated bonds per atom from valence — d_020
- Definition: B_pa = 0.5 * sum_i x_i * b_i (each bond shared by two atoms; b_i from the capacity rule above). Variant d_020b
  caps the sum by the anion side: B_pa' = min(0.5 * sum x_i b_i, sum_{anions} x_i * b_i) because every bond in a
  metal-nonmetal compound has at least one anion end (declared up front to avoid post-hoc tuning).
- Rationale: covalent hardness scales with bond density and strength; bonds per atom is the crude topological ingredient
  Gao/Šimůnek models need (number of bonds per cell) before the volume is known. Octet-style capacity encodes why diamond
  (b=4, 2 bonds/atom) and B4C beat Na-type sp metals with the same mean valence.
- Units: bonds per atom (dimensionless). Expected sign: positive. Honest caveat: with min(v, 8-v) this equals mean valence
  for early elements and a different function for p-block, so correlation with m_NValence is likely high; the non-redundant
  part is the p-block fold-over. Report the correlation with m_NValence and m_NUnfilled before testing.
- Beyond Magpie means: m_NValence and m_NUnfilled together nearly span this for a single element, but the *fold-over*
  min(v, 8-v) is a per-element nonlinearity applied before averaging, which fraction-weighted means of v or unfilled cannot
  reproduce (the mean of a min is not the min of the means).

## H4.3 Fraction of bonds that are metal-nonmetal vs metal-metal — d_021
- Definition: with M = metals (chi < 2.0, set above) and A = anions, a stoichiometric stub-matching model: bond stubs
  S_M = sum_{metals} x_i b_i, S_A = sum_{anions} x_i b_i. Heteropolar bonds f_MA = min(S_M, S_A); leftover stubs form
  homopolar bonds (metal-metal if S_M > S_A, anion-anion otherwise). Output d_021 = f_MA / (0.5 * (S_M + S_A)) in [0, 1]
  (0 for no anion or no metal; set 0 when S_M + S_A = 0).
  Companion d_021b = metal-metal share of stubs = max(S_M - S_A, 0) / S_M (0 for all-anion-rich compounds).
- Rationale: heteropolar M-X bonds (especially with short TM-light-element distances) carry most of the covalent
  strength in TMCs/TMNs/TMBs; metal-metal bonds are delocalised and plastic, lowering hardness. Cleanly 0/1 limits:
  pure metal ->0 hetero, saturated MX ->1.
- Units: dimensionless fraction. Expected sign: positive for d_021 (more M-X bonding, harder), negative for d_021b.
  Interaction with d_008 (ionicity) is expected: very polar M-X (chi range > ~2) is brittle/soft so the product with d_008
  may carry the signal; do not test the interaction as a separate descriptor first, let SR build it.
- Beyond Magpie means: Magpie means are linear in x and know nothing about stub matching; this is a piecewise
  min() function of the *ratio* of metal to anion stubs. The kink at stoichiometric balance (S_M = S_A) is a feature no
  mean or range captures. Known failure mode: ionic compounds (oxides) are also M-X dominated but soft in this proxy; hence
  the expected interaction with d_008.

## H4.4 Valence-electron count per bond — d_022
- Definition: VEC_b = (sum_i x_i v_i) / B_pa with v_i, B_pa from d_020 (use total valence electrons per atom over bonds per atom).
  Guard: B_pa = 0 -> row left NaN and flagged (not imputed); report the number of such rows in the scoring note.
- Rationale: valence electrons per bond is the covalent bond order proxy (a bond holds 2 electrons: VEC_b ~ 2 for ideal
  octet networks, > 2 means excess electrons filling antibonding/metallic states, < 2 means electron-deficient bonding
  as in borides and boron-rich phases). Hardness in TM borides/carbides is known to peak near an optimal VEC window
  (Lazar-style / Brgoch discussions), so this is expected to be non-monotonic and best entered through
  |VEC_b - 2| or its square rather than raw.
- Units: electrons per bond (dimensionless count ratio). Expected sign: non-monotonic; negative on |VEC_b - 2|
  (pre-registered; raw VEC_b has no pre-registered sign). Include d_022b = |VEC_b - 2| in the same arm.
- Beyond Magpie means: m_NValence is electrons per atom; dividing by bonds per atom (which depends on the fold-over and on
  the cap in d_020b) gives a **ratio of two nonlinear averages**, not a ratio of means. It is the one descriptor of this
  family that is not obviously a rearrangement of m_NValence/m_NUnfilled; highest prior of adding information and highest
  collinearity risk with d_020.

## Evaluation plan (pre-registered)
1. Implement d_019-d_022 (+b variants) as descriptors; print Spearman correlation with each other and with
   m_NValence, m_NUnfilled, d_008 on **train+val pooled, descriptors only (no target)** to document redundancy. No target
   correlation is computed for selection.
2. Add them as fixed extra arms in eval/nested_cv.py (e.g. magpie+d_008+bonds), with arms declared before any run, same
   folds, seeds and config. Do not prune the family after seeing outer-fold results; report all arms.
3. A descriptor counts as supported only if the nested-CV mean test MAE (c<=12) beats the Magpie-only arm by the same
   margin used in CLAUDE.md (>= 0.08 GPa) across >= 3 seeds AND it appears in selected equations in a majority of
   fold-seeds. Because re-partitioning the pooled data re-uses already-consulted labels, this is a predictive-pipeline
   comparison, not independent confirmation (verdict, "Minimum extra evidence").
4. Any wording like "bond" or "ionic" is a motivation, not a result; units remain dimensionless counts/fractions,
   and no formula from this family is called a law unless it survives genuinely new labeled families.

## Risks
- Anion/cation assignment uses a chi cut; borderline elements (B, Si, Ge, As, H, Sb) change the descriptors discretely.
- Valence counts for f-block/Mn/Fe-type elements are crude; the bond-capacity rule ignores coordination and bond length
  (no volume information; Magpie GSvolume_pa is a weighted elemental volume, per the verdict, not compound volume).
- Same composition, different target (BN, V5Si3 in the verdict) is untouched: these are still composition-only.
