# Release v2.0-confirmatory

Confirmatory-revision release of the MS-BDTT reproducibility package.

## Contents

| Path | Contents |
|---|---|
| `data/MS-BDTT.xlsx` | Source workbook of the supplemental experiments (ten-seed paired comparison, S4 open-set evaluation, measured retention-ratio and budget sweeps, identifiability diagnostics, per-stage MMD values, particle-count sensitivity). |
| `code/kit/` | Confirmatory-analysis kit and the document pipeline (`e1_ten_seed.py`, `e2_openset_s4.py`, `e3_retention_sweep.py`, `e4_budget_sweep.py`, `e5_label_budget.py`, `e6_identifiability.py`, `e7_mmd_logging.py`, `leakage_check.py`, `check_tier.py`, `apply_tier.py`, `fill_and_rebuild.py`, `set_archive.py`, `insert_doi.py`, `adapter.py`, `common.py`, `run_all.py`). |
| `code/build/` | Document build pipeline (`build_docs.py`, `stylefix.py`), workbook-to-results converter (`build_results_from_xlsx.py`), figure scripts (`make_figures.py`, `make_fig8.py`). |
| `src/` | Markdown sources of the revised manuscript and of the point-by-point response letter. |
| `results/` | Machine-readable outputs (`e1_table9.json`, `e2_openset.json`, `e3_retention.json`, `e4_budget.json`, `e6_identifiability.json`, `e7_mmd.json`, `tier_decision.json`). |
| `figures/` | Figures 5, 8 and 10 regenerated from the measured data. |
| `manifests/` | Location for the split manifests and their SHA-256 checksums (to be added from the training pipeline). |

## Checksums

`SHA256SUMS.txt` lists the SHA-256 checksum of every file in this release; verify with

```
sha256sum -c SHA256SUMS.txt
```

## Archived identifiers

- DOI of the deposit: see `zenodo_metadata.json` / the manuscript's Code and data availability section.
- Software Heritage: the same tagged release is archived in the Software Heritage long-term source-code archive; the SWHID is recorded in the release notes of the archive entry.
