# Citation audit: wiki/COMPARISON_TO_LITERATURE.md

**Date**: 2026-10-21. **Skill**: ARIS `/citation-audit`, adapted: the audited document is a markdown file, not a LaTeX paper, so the "bib" is three entries written out in the reviewer prompt and the "contexts" are the eight rows of the file's verification table plus a few prose claims. **Reviewer**: fresh Codex thread (`01a160c9-cce0-7052-8c01-e05ab3a5ab6b`), blind to the executor's extraction, web lookups required; verbatim response in `.aris/traces/citation-audit/2026-10-21_run01/reviewer_response.md`. **Independent executor check**: the executor also read the full text of both papers (Tehrani NSF-PAR PDF; Chen arXiv v1 PDF) and agrees with the reviewer on every claim below; that is not independent of the reviewer's outcome but it is the source of the numbers.

## Summary
| Entry | Existence | Metadata | Claims | Verdict |
|---|---|---|---|---|
| [T] Mansouri Tehrani et al., JACS 140, 9844 (2018), doi 10.1021/jacs.8b02717 | yes | correct | T1-T6, T8 supported; **T7 contradicted as worded (fixed)** | KEEP after fix |
| [C] Chen, Niu, Li, Li, Intermetallics 19, 1275-1281 (2011), doi 10.1016/j.intermet.2011.03.026 | yes | correct | C1, C2 supported (for the arXiv v1 preprint) | KEEP |
| [M] matminer `brgoch_superhard_training` | yes | correct | M1 supported | KEEP |

## Findings
1. **FIX (applied): T7 wording.** The file said Tehrani "used predicted B and G, and G/B, as hardness proxies". The paper uses predicted B and G as the hardness proxy and discusses Pugh's ratio G/B only as a ductility indicator (p. 9851); it does not apply Chen's formula (the only "Chen" in the text are co-authors in the reference list). Corrected in COMPARISON_TO_LITERATURE.md item 5. **The same inaccurate phrase is in `wiki/TARGET_RECOMMENDATION.md` ("used them plus G/B as hardness proxies"); not edited here, flagged for its author.**
2. **Version caveat (applied).** The reviewer could not confirm that the NSF-PAR PDF is the accepted manuscript or that its body equals the published article; the file now says so. Tehrani's numbers are verified for the NSF-PAR copy only; the published article was verified for metadata.
3. **Preprint vs published.** Chen's Eq. (11) was verified in arXiv:1102.4063v1, whose title differs from the published title ("Intrinsic Correlation between Hardness and Elasticity in Polycrystalline Materials and Bulk Metallic Glasses" vs "Modeling hardness of polycrystalline materials and bulk metallic glasses"). Published equation numbering was not checked. The file now records both titles.
4. **Unexplained 2572 vs 2574.** The paper reports 2572 final moduli; matminer documents 2574 entries. Neither the reviewer nor the executor can explain the 2-row difference; stated as unexplained in the file.
5. **Not verified / out of scope.** T8 (no fold grouping) is a statement about the *text*: grouping is not described, the actual fold assignment is unknown. Standalone dataset creators/DOI for the matminer record were not verified.

## Numbers in the file that are ours, not from a paper
All B/G errors for our models (`ledger/bg_errors.csv`), including the bootstrap intervals, are our own computations and are outside this audit's scope; they are reproducible with `scripts/bg_errors.py`.
