# citation-audit trace, 2026-10-21 run01
Target: wiki/COMPARISON_TO_LITERATURE.md (markdown document, 3 bibliographic entries [T], [C], [M], 11 quoted facts)
Reviewer: Codex MCP, model gpt-6-astra requested (xhigh), fresh thread 01a160c9-cce0-7052-8c01-e05ab3a5ab6b, sandbox read-only.
Blind: the prompt contained the entries and the claimed values only, not the executor's extraction. Prompt claims T1-T8, C1-C2, M1.
Response below is verbatim.

---

**[T] — EXISTENCE: YES. VERDICT: FIX T7's wording; retain the citation.**

**METADATA:** Authors and order, year, venue, volume/issue, pages, title, and DOI are **correct as supplied**. [ACS record](https://pubs.acs.org/doi/abs/10.1021/jacs.8b02717).

**Version limitation:** T1–T8 below use indexed text from the [NSF-hosted PDF](https://par.nsf.gov/servlets/purl/10094086), which has journal pagination. Direct retrieval returned 502. Its designation as an **accepted manuscript is UNCERTAIN**; I verified the published metadata/abstract but could not compare the full published body. Differences between versions therefore remain **UNCERTAIN**.

| Claim | Status | Evidence and location in NSF copy |
|---|---|---|
| T1 | **SUPPORTED** | "3248" B/G elastic-modulus entries extracted from Materials Project; methods, p. 9845. |
| T2 | **SUPPORTED** | Filtering reduces the training data to "2572"; methods, p. 9845. |
| T3 | **SUPPORTED** | "150" descriptors: "34" compositional variables with four mathematical summaries, plus "14" structural descriptors; methods, p. 9845. |
| T4 | **SUPPORTED** | RBF SVR; "10-fold" CV for training; "20-fold random split" CV for GA variable selection; methods, p. 9845. |
| T5 | **SUPPORTED** | Bulk RMSECV "17.2 GPa", r² "0.94"; discussion of Figure 1a, p. 9846. |
| T6 | **SUPPORTED** | Shear RMSECV "16.5 GPa", cross-validated r² "0.84"; discussion of Figure 2a, p. 9847. |
| T7 | **CONTRADICTED as worded** | B/G proxy screening is supported; Chen conversion was not found. **G/B assesses ductility**, described as indicating "ductile/brittle behavior"; Figure 3 screening, pp. 9848–49, and p. 9851. |
| T8 | **SUPPORTED for the reported methods** | Polymorph labels are "composition, space group number"; composition/system grouping is **NOT FOUND** in the CV description. Actual fold assignments remain **UNCERTAIN**; methods, p. 9845. |

Correct T7 to: **"The paper screens predicted B and G as hardness proxies; it discusses G/B as a ductility indicator. No application of Chen's hardness formula was found."**

**[C] — EXISTENCE: YES. VERDICT: KEEP.**

**METADATA:** Authors, 2011, *Intermetallics* **19**, 1275–1281, published title, and DOI are **correct as supplied**. The publisher identifies issue **9**; arXiv links this preprint to the same journal reference and DOI. [Publisher contents](https://www.sciencedirect.com/journal/intermetallics/vol/19/issue/9), [arXiv record](https://arxiv.org/abs/1102.4063).

| Claim | Status | Evidence, location, and version |
|---|---|---|
| C1 | **SUPPORTED** | H_v = 2(k²G)^0.585 − 3, **Eq. (11)**; k = G/B is defined alongside Eq. (9). Section 2, p. 3, **arXiv:1102.4063v1 preprint**. G, B, and hardness use GPa. [Preprint](https://arxiv.org/pdf/1102.4063v1#page=3). |
| C2 | **SUPPORTED** | **Preprint:** "Intrinsic Correlation between Hardness and Elasticity in Polycrystalline Materials and Bulk Metallic Glasses". **Published:** "Modeling hardness of polycrystalline materials and bulk metallic glasses". [arXiv title record](https://arxiv.org/abs/1102.4063), [publisher title](https://www.sciencedirect.com/journal/intermetallics/vol/19/issue/9). |

The **Eq. (11)** numbering is verified for the preprint; published equation numbering is **UNCERTAIN**.

**[M] — EXISTENCE: YES. VERDICT: KEEP.**

**METADATA:** Dataset name and platform are **correct**. The supplied Figshare file URL exactly matches matminer's metadata. Its bibliographic reference has the **correct [T] authors, year, venue, volume/pages, title, and DOI**. Standalone dataset creators, publication year, and dataset DOI are **UNCERTAIN**; journal volume/pages are inapplicable to the dataset itself. [Package metadata, `brgoch_superhard_training` record](https://github.com/hackingmaterials/matminer/blob/main/src/matminer/datasets/dataset_metadata.json).

| Claim | Status | Evidence, location, and version |
|---|---|---|
| M1 | **SUPPORTED** | "2574 materials used for training regressors that predict shear and bulk modulus." The dataset section gives 2,574 entries and references [T]. **matminer 0.10.0rc0 documentation**, `brgoch_superhard_training` section. [Dataset documentation](https://hackingmaterials.lbl.gov/matminer/dataset_summary.html#brgoch-superhard-training). |

**Preserve the discrepancy:** [T] reports **2,572**, while matminer documents **2,574**. The reason for the difference is **UNCERTAIN**.
