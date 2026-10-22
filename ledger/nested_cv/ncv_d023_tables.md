## Per-fold test MAE (GPa), mean ± sd over 5 outer folds

Runs ncv_d023; niterations=22000, seed=0, procs=4, maxsize=15, timeout=900s, rows=2120, groups=1406.

| arm | window | f0 | f1 | f2 | f3 | f4 | mean ± sd | pooled tail MAE (>=20) | n_tail | folds with d_023 | nonfinite |
|---|---|---|---|---|---|---|---|---|---|---|---|
| median_const | c<=9 | 4.777 | 4.649 | 5.064 | 4.466 | 5.490 | 4.889 ± 0.400 | 21.97 | 103 | 0/5 | 0 |
| median_const | c<=12 | 4.777 | 4.649 | 5.064 | 4.466 | 5.490 | 4.889 ± 0.400 | 21.97 | 103 | 0/5 | 0 |
| median_const | c<=15 | 4.777 | 4.649 | 5.064 | 4.466 | 5.490 | 4.889 ± 0.400 | 21.97 | 103 | 0/5 | 0 |
| svr_baseline | c<=9 | 2.956 | 2.782 | 3.145 | 2.412 | 2.757 | 2.810 ± 0.272 | 8.74 | 103 | 0/5 | 0 |
| svr_baseline | c<=12 | 2.956 | 2.782 | 3.145 | 2.412 | 2.757 | 2.810 ± 0.272 | 8.74 | 103 | 0/5 | 0 |
| svr_baseline | c<=15 | 2.956 | 2.782 | 3.145 | 2.412 | 2.757 | 2.810 ± 0.272 | 8.74 | 103 | 0/5 | 0 |
| svr_fitidx | c<=9 | 3.054 | 2.953 | 3.260 | 2.568 | 2.928 | 2.952 ± 0.252 | 9.06 | 103 | 0/5 | 0 |
| svr_fitidx | c<=12 | 3.054 | 2.953 | 3.260 | 2.568 | 2.928 | 2.952 ± 0.252 | 9.06 | 103 | 0/5 | 0 |
| svr_fitidx | c<=15 | 3.054 | 2.953 | 3.260 | 2.568 | 2.928 | 2.952 ± 0.252 | 9.06 | 103 | 0/5 | 0 |
| magpie | c<=9 | 3.918 | 4.212 | 4.058 | 3.813 | 4.196 | 4.039 ± 0.174 | 14.97 | 103 | 0/5 | 0 |
| magpie | c<=12 | 3.859 | 3.739 | 3.850 | 3.547 | 3.937 | 3.787 ± 0.151 | 12.84 | 103 | 0/5 | 0 |
| magpie | c<=15 | 3.859 | 3.792 | 3.765 | 3.481 | 3.937 | 3.767 ± 0.173 | 12.70 | 103 | 0/5 | 0 |
| magpie+d_023 | c<=9 | 3.642 | 3.669 | 3.626 | 3.383 | 3.772 | 3.618 ± 0.144 | 9.95 | 103 | 5/5 | 0 |
| magpie+d_023 | c<=12 | 3.617 | 3.669 | 3.658 | 3.326 | 3.772 | 3.608 ± 0.168 | 10.07 | 103 | 5/5 | 0 |
| magpie+d_023 | c<=15 | 3.507 | 3.506 | 3.504 | 3.326 | 3.622 | 3.493 ± 0.106 | 10.05 | 103 | 5/5 | 0 |
| magpie+d_023+d_031 | c<=9 | 3.642 | 3.667 | 3.626 | 3.383 | 3.772 | 3.618 ± 0.143 | 9.90 | 103 | 5/5 | 0 |
| magpie+d_023+d_031 | c<=12 | 3.617 | 3.646 | 3.618 | 3.353 | 3.772 | 3.601 ± 0.153 | 10.05 | 103 | 5/5 | 0 |
| magpie+d_023+d_031 | c<=15 | 3.507 | 3.646 | 3.535 | 3.281 | 3.622 | 3.518 ± 0.145 | 9.76 | 103 | 5/5 | 0 |

## Selected equation per fold and window (complexity, inner-val MAE, outer-test MAE)

- magpie c<=9 f0 (c9, inner 4.122, test 3.918, uses -): `((313.5142 / m_NValence) / (m_GSvolume_pa - 4.9109)) + m_NUnfilled`
- magpie c<=9 f1 (c6, inner 3.727, test 4.212, uses -): `exp((m_NUnfilled + 3.5651524) / m_Row)`
- magpie c<=9 f2 (c7, inner 3.778, test 4.058, uses -): `((500.17487 / m_NValence) / m_GSvolume_pa) + m_NUnfilled`
- magpie c<=9 f3 (c7, inner 3.937, test 3.813, uses -): `m_NUnfilled + ((1614.5458 / m_GSvolume_pa) / m_Number)`
- magpie c<=9 f4 (c9, inner 3.373, test 4.196, uses -): `((56671.316 / (m_CovalentRadius * m_NValence)) / m_GSvolume_pa) + m_NUnfilled`
- magpie c<=12 f0 (c10, inner 3.931, test 3.859, uses -): `m_NUnfilled + (m_MendeleevNumber / (exp(m_Row) / (4.0826006 - m_NpValence)))`
- magpie c<=12 f1 (c12, inner 3.686, test 3.739, uses -): `253.16577 / (((exp(m_NpValence) - m_NUnfilled) + (m_NdValence * m_Row)) + m_GSvolume_pa)`
- magpie c<=12 f2 (c12, inner 3.665, test 3.850, uses -): `(((398.1363 - exp(m_NdUnfilled)) / m_NValence) / (m_GSvolume_pa - m_NUnfilled)) + m_NUnfilled`
- magpie c<=12 f3 (c12, inner 3.693, test 3.547, uses -): `((m_MendeleevNumber * ((m_NsValence * 2.2444355) - m_NpValence)) / exp(m_Row)) + m_NUnfilled`
- magpie c<=12 f4 (c12, inner 3.317, test 3.937, uses -): `m_NUnfilled + ((m_MendeleevNumber * ((m_NsValence / 0.4594579) - m_NpValence)) / exp(m_Row))`
- magpie c<=15 f0 (c10, inner 3.931, test 3.859, uses -): `m_NUnfilled + (m_MendeleevNumber / (exp(m_Row) / (4.0826006 - m_NpValence)))`
- magpie c<=15 f1 (c14, inner 3.620, test 3.792, uses -): `251.85307 / ((m_NdValence * m_Row) + ((exp(m_NpValence) + m_GSvolume_pa) - (m_NpUnfilled * m_NdUnfilled)))`
- magpie c<=15 f2 (c14, inner 3.605, test 3.765, uses -): `m_NUnfilled + (((383.34253 - exp(m_NdUnfilled)) / (m_GSvolume_pa - m_NUnfilled)) / (m_NValence - m_NfValence))`
- magpie c<=15 f3 (c15, inner 3.598, test 3.481, uses -): `m_NUnfilled + ((sqrt(m_GSbandgap) + (m_MendeleevNumber / exp(m_Row))) * ((m_NsValence * 2.0500977) - m_NpValence))`
- magpie c<=15 f4 (c13, inner 3.313, test 3.937, uses -): `(m_MendeleevNumber * ((exp(m_NsValence / 1.3458744) - m_NpValence) / exp(m_Row))) + m_NUnfilled`
- magpie+d_023 c<=9 f0 (c8, inner 3.779, test 3.642, uses d_023): `(d_023 / (sqrt(m_Column) + m_NdValence)) + m_NpUnfilled`
- magpie+d_023 c<=9 f1 (c9, inner 3.264, test 3.669, uses d_023): `(d_023 / (m_Electronegativity + (m_NdValence + 0.88324726))) + m_NpUnfilled`
- magpie+d_023 c<=9 f2 (c8, inner 3.419, test 3.626, uses d_023): `(d_023 / (m_NdValence + sqrt(m_Column))) + m_NpUnfilled`
- magpie+d_023 c<=9 f3 (c8, inner 3.509, test 3.383, uses d_023): `(d_023 / (m_NdValence + sqrt(m_Column))) + m_NpUnfilled`
- magpie+d_023 c<=9 f4 (c8, inner 3.346, test 3.772, uses d_023): `(d_023 / (m_NdValence + sqrt(m_Column))) + m_NpUnfilled`
- magpie+d_023 c<=12 f0 (c11, inner 3.660, test 3.617, uses d_023): `(m_NpUnfilled * sqrt(m_NdUnfilled)) + (d_023 / (m_NdValence + sqrt(m_Column)))`
- magpie+d_023 c<=12 f1 (c9, inner 3.264, test 3.669, uses d_023): `(d_023 / (m_Electronegativity + (m_NdValence + 0.88324726))) + m_NpUnfilled`
- magpie+d_023 c<=12 f2 (c12, inner 3.374, test 3.658, uses d_023): `m_NpUnfilled + (d_023 / (((m_Row + m_NdValence) / sqrt(m_NsValence)) + m_NpValence))`
- magpie+d_023 c<=12 f3 (c12, inner 3.422, test 3.326, uses d_023): `(d_023 / (m_NdValence + sqrt(m_Column))) + ((m_NsValence + -0.6164457) * m_NpUnfilled)`
- magpie+d_023 c<=12 f4 (c8, inner 3.346, test 3.772, uses d_023): `(d_023 / (m_NdValence + sqrt(m_Column))) + m_NpUnfilled`
- magpie+d_023 c<=15 f0 (c15, inner 3.499, test 3.507, uses d_023): `(d_023 / (m_NdValence + sqrt(m_NdUnfilled + m_Column))) + (m_NpUnfilled * (sqrt(m_NdUnfilled) + 0.4351303))`
- magpie+d_023 c<=15 f1 (c13, inner 3.181, test 3.506, uses d_023): `(d_023 / (m_Electronegativity + (m_NdValence + log(m_Row)))) + (m_NpUnfilled * sqrt(m_NdUnfilled))`
- magpie+d_023 c<=15 f2 (c14, inner 3.210, test 3.504, uses d_023): `((d_023 + 11.94037) / ((m_Row + m_NpValence) + m_NdValence)) + (m_NpUnfilled * sqrt(m_NdUnfilled))`
- magpie+d_023 c<=15 f3 (c12, inner 3.422, test 3.326, uses d_023): `(d_023 / (m_NdValence + sqrt(m_Column))) + ((m_NsValence + -0.6164457) * m_NpUnfilled)`
- magpie+d_023 c<=15 f4 (c13, inner 3.289, test 3.622, uses d_023): `(sqrt(m_NdUnfilled) * m_NpUnfilled) + (d_023 / (m_NdValence + sqrt(m_NdUnfilled + m_Column)))`
- magpie+d_023+d_031 c<=9 f0 (c8, inner 3.779, test 3.642, uses d_023): `m_NpUnfilled + (d_023 / (sqrt(m_Column) + m_NdValence))`
- magpie+d_023+d_031 c<=9 f1 (c9, inner 3.284, test 3.667, uses d_023+d_031): `d_023 / ((m_Electronegativity * 1.3700607) + (d_031 * m_NdValence))`
- magpie+d_023+d_031 c<=9 f2 (c8, inner 3.419, test 3.626, uses d_023): `m_NpUnfilled + (d_023 / (sqrt(m_Column) + m_NdValence))`
- magpie+d_023+d_031 c<=9 f3 (c8, inner 3.509, test 3.383, uses d_023): `m_NpUnfilled + (d_023 / (m_NdValence + sqrt(m_Column)))`
- magpie+d_023+d_031 c<=9 f4 (c8, inner 3.346, test 3.772, uses d_023): `(d_023 / (sqrt(m_Column) + m_NdValence)) + m_NpUnfilled`
- magpie+d_023+d_031 c<=12 f0 (c11, inner 3.660, test 3.617, uses d_023): `(d_023 / (sqrt(m_Column) + m_NdValence)) + (sqrt(m_NdUnfilled) * m_NpUnfilled)`
- magpie+d_023+d_031 c<=12 f1 (c10, inner 3.258, test 3.646, uses d_023+d_031): `d_023 / ((m_NdValence * d_031) + exp(m_Electronegativity * 0.49487114))`
- magpie+d_023+d_031 c<=12 f2 (c12, inner 3.284, test 3.618, uses d_023+d_031): `(d_023 / (m_NValence - m_NfValence)) + (exp(m_NsValence - d_031) - m_Electronegativity)`
- magpie+d_023+d_031 c<=12 f3 (c12, inner 3.410, test 3.353, uses d_023+d_031): `(d_023 / (sqrt(m_Column) + m_NdValence)) + (m_NpUnfilled * (m_NsValence - d_031))`
- magpie+d_023+d_031 c<=12 f4 (c8, inner 3.346, test 3.772, uses d_023): `(d_023 / (sqrt(m_Column) + m_NdValence)) + m_NpUnfilled`
- magpie+d_023+d_031 c<=15 f0 (c15, inner 3.499, test 3.507, uses d_023): `(d_023 / (m_NdValence + sqrt(m_NdUnfilled + m_Column))) + (m_NpUnfilled * (sqrt(m_NdUnfilled) - -0.43399423))`
- magpie+d_023+d_031 c<=15 f1 (c10, inner 3.258, test 3.646, uses d_023+d_031): `d_023 / ((m_NdValence * d_031) + exp(m_Electronegativity * 0.49487114))`
- magpie+d_023+d_031 c<=15 f2 (c15, inner 3.277, test 3.535, uses d_023+d_031): `(d_023 / ((sqrt(m_Column) + m_NdValence) + 0.33464015)) + (m_NpUnfilled * (sqrt(m_NUnfilled) - d_031))`
- magpie+d_023+d_031 c<=15 f3 (c13, inner 3.371, test 3.281, uses d_023+d_031): `(m_NpUnfilled * (sqrt(m_NUnfilled) - d_031)) + (d_023 / (m_NdValence + sqrt(m_Column)))`
- magpie+d_023+d_031 c<=15 f4 (c13, inner 3.289, test 3.622, uses d_023): `(d_023 / (sqrt(m_NdUnfilled + m_Column) + m_NdValence)) + (sqrt(m_NdUnfilled) * m_NpUnfilled)`