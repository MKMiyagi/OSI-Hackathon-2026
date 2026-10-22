"""d_031: atomic fraction of metal atoms, sum_{i in METALS} x_i, with a fixed explicit element list.

Rationale: metallic bonding is delocalised and plastic (low shear-to-bulk ratio k = G/B), while hard covalent networks
(diamond, c-BN, B4C, SiC) are nonmetal-rich. This is the direct metal/nonmetal split that d_019's Pauling-chi cut got wrong
(chi >= 2.0 put Mo, W and the late transition metals in the anion set; see wiki/cycle_log.md cycle 024). No electronegativity
threshold is used: METALS is the explicit list below, declared before any run.
METALS = alkali, alkaline-earth, transition metals (Sc-Zn, Y-Cd, Hf-Hg), lanthanides, actinides, and the post-transition
metals Al, Ga, In, Tl, Sn, Pb, Bi. NOT metals (declared convention): H, noble gases, halogens, chalcogens, pnictogens N/P,
and the metalloids B, Si, Ge, As, Sb, Te (they sit at the metal/nonmetal border and form the covalent networks of interest).
Units: dimensionless atomic fraction in [0, 1]. Expected sign: negative on Hv (and on k = G/B), saturating: elemental metals
and intermetallics (fraction 1) are soft; fractions below ~0.5 are the carbides/nitrides/borides/oxides.
Coverage: every element gets a flag from the list (an element outside the list is a nonmetal), so no NaN and no fallback is needed.
Uses only df["comp"].
"""
import pandas as pd

METALS = frozenset(
    "Li Na K Rb Cs Fr Be Mg Ca Sr Ba Ra "
    "Sc Ti V Cr Mn Fe Co Ni Cu Zn Y Zr Nb Mo Tc Ru Rh Pd Ag Cd Hf Ta W Re Os Ir Pt Au Hg "
    "La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Ac Th Pa U Np Pu Am Cm Bk Cf Es Fm Md No Lr "
    "Al Ga In Tl Sn Pb Bi".split()
)


def _metal_fraction(comp):
    d = comp.get_el_amt_dict()
    return sum(v for k, v in d.items() if k in METALS) / sum(d.values())


def compute(df: pd.DataFrame) -> pd.Series:
    return pd.Series([_metal_fraction(c) for c in df["comp"]], index=df.index, name="d_031")
