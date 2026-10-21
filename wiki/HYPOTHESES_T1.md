# T1 descriptor hypotheses for the B, G route (PROPOSED, not implemented)

For the search proposed in wiki/TARGET_RECOMMENDATION.md: Hv = Chen(B, G), where B sets the *scale* and the Pugh ratio
k = G/B sets the *bonding character*. IDs start at d_023 so they don't collide with d_019-d_022 (bond-count family,
wiki/HYPOTHESES_4.md, PR #11). Signs and units are pre-registered. Inputs are composition + matminer element tables only.
H1 is **not val-blind**: it was screened on train, and its 2-parameter fit was then scored once on val (R^2 0.81, Chen
MAE 4.45; wiki/TARGET_RECOMMENDATION.md). H2-H5 have not been computed at all.

## H1 Cohesive-energy density — d_023 (target B, also G)
- `160.2 * sum_i x_i E_coh,i / m_GSvolume_pa` in GPa. E_coh is Kittel's cohesive energy from matminer
  `utils/data_files/cohesive_energies.json`, which covers every element in the dataset. Declare `UNITS = "Pa"`.
- Rationale: a modulus is a curvature of energy per volume, B ~ E_coh / V (universal binding-energy relation,
  Rose, Smith, Guinea & Ferrante 1984). It is the only descriptor with the target's dimension. Note `--units`
  does not reward that: constants may carry any unit (PySR dimensionless_constants_only=False), so e.g.
  `2118 / m_GSvolume_pa` also passes as Pa. Only `--dimensionless-constants` makes d_023 (or bandgap/volume) the
  sole route to Pa.
- Expected sign: positive, power ~1. Train-only screen: Spearman 0.88 with B (vs 0.39 for NValence/V, d_002) and
  0.78 with G. The 2-parameter train fit B = 3.26 * d_023^0.994 gives val R^2 0.81 (development-set figure: val was
  consulted).

## H2 Cohen covalent bulk modulus — d_024 (target B)
- `(1971 - 220 * lam) * d^-3.5` in GPa, with d = 2 * harmonic-mean covalent radius (A; cf. d_010) and
  lam = 0 / 1 / 2 for IV-IV / III-V / II-VI-like group differences (lam = |group difference| / 2, clipped to [0, 2]).
- Rationale: Cohen 1985 (PRB 32, 7988) gets B of tetrahedral covalent solids within ~10% from bond length and ionicity.
- Expected sign: positive. It should matter for the covalent subset (B, C, N, Si compounds) and be ignored for
  intermetallics. A useful negative control against H1.

## H3 Atomic size mismatch — d_025 (target k = G/B, or G)
- `delta = sqrt(sum_i x_i (1 - r_i / r_bar)^2)` with covalent radii and r_bar = sum x_i r_i. Dimensionless.
- Rationale: interstitial carbides, nitrides and borides (small nonmetal in a metal lattice; TiC, WC, ZrB2) are the stiff,
  high-k compounds. Large mismatch marks that structural motif, which no mean or EN-range descriptor encodes.
- Expected sign: positive on k. Low confidence: in solid solutions mismatch lowers elastic stiffness, so a negative fit
  would mean the intermetallics dominate. Record either sign.

## H4 Distance from the carbonitride VEC optimum — d_026 (target G, k)
- `(m_NValence - 4.2)^2`. That is valence electrons per atom relative to 8.4 per MX formula unit.
- Rationale: Jhi, Ihm, Louie & Cohen 1999 (Nature 399, 132): C44 and hardness of TM carbonitrides peak at VEC ~ 8.4,
  where sigma-bonding p-d states are filled and the shear-unstable d-t2g states are empty.
- Expected sign: negative on G and k. SR could build this from m_NValence (5 nodes), so supplying it is a test of
  whether a known optimum is too expensive to discover at maxsize 15. Report results for MX-type rows separately.

## H5 Cohesive-energy spread (weakest link) — d_027 (target k)
- `(max_i E_coh,i - min_i E_coh,i) / sum_i x_i E_coh,i`. Dimensionless.
- Rationale: shear resistance is limited by the weakest bonds. A compound that mixes a very cohesive element (W, C, B)
  with a weakly bound one (alkali, Zn, halogen) has soft shear paths even when the average energy density (H1) is high.
- Expected sign: negative on k. This is not an EN-range variant (a retired family): cohesive energy and Pauling chi are
  only weakly correlated across the d-block. Report its Spearman correlation with d_008 before testing.

## Suggested queue for tonight
Reference arms (no descriptor) for B and G first. Then H1 on B, H1 on G, H1+H3 on G, H1+H4 on G, H5 on G.
Then compose Hv = Chen(B, G) on val with eval/compose_hv.py. Use `--units` for every B and G arm.

## Implementation check (2026-10-21 14:05; train only, descriptor-descriptor Spearman, no target)
All five are now in descriptors/ (d_023-d_027) and finite on every train row.
- **d_024 (Cohen) is rank-identical to d_010** (rho = -1.00): lam clips to 2 for almost every compound, so it
  collapses to a monotone function of harmonic radius, a family already tested (cycle 010, noise). Don't queue it.
- **d_026 (VEC optimum) is ~ m_NValence** (rho 0.98). Magpie's NValence also counts filled d10 shells (Ga = 13), so
  the 4.2 e/atom optimum is only meaningful for transition-metal compounds. Low priority.
- d_025 (size mismatch): rho 0.61 with d_008, 0.42 with d_024; partly new.
- **d_027 (E_coh spread): max |rho| 0.40** (with d_008); the most novel of the four.
- d_023 results (direct Hv and Chen(B, k) routes): see wiki/T1_ROUTES.md.
