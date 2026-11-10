# MS-BDTT Confirmatory Re-run Kit (F1–F9)

This kit contains the scripted confirmatory analyses promised in the revised
manuscript (Appendix D.2, Section 5.6, Section 4.2.3/4.2.4, Appendix E.2,
Appendix C.4) plus the one-command pipeline that fills the `⟦FILL-…⟧`
placeholders and rebuilds the two submission documents.

## Order of operations

| Step | Action | Fills | Script | Output |
|------|--------|-------|--------|--------|
| 0 | Plug your pipeline into `adapter.py` (the only file to edit) | — | — | — |
| 1 | Deposit the archive on Zenodo, record the DOI | F1 | manual, see "Zenodo deposit" below | `results/f1_zenodo.json` |
| 2 | Ten-seed paired replication (MS-BDTT vs COSDA, S1–S5) | F2, F2b | `python e1_ten_seed.py` | `results/e1_table9.json` |
| 3 | S4 open-set evaluation (4 methods × 3 runs) | F5a | `python e2_openset_s4.py` | `results/e2_openset.json` |
| 4 | Retention sweep (5 ratios × 5 runs × 5 scenarios) | F3 | `python e3_retention_sweep.py` | `results/e3_retention.json` |
| 5 | Budget sweep (2 rules × 6 budgets × 5 runs) | F4 | `python e4_budget_sweep.py` | `results/e4_budget.json` |
| 6 | XJTU-SY degradation-boundary label budget + SPFD supports | F6, F5b | `python e5_label_budget.py` | `results/e5_counts.json` |
| 7 | Identifiability diagnostics (recovery / PPC / coverage) | F7 | `python e6_identifiability.py` | `results/e6_identifiability.json` |
| 8 | Raw per-scenario per-stage MMD values | F8 | `python e7_mmd_logging.py` | `results/e7_mmd.json` |
| 9 | Verify manifests against Section 4.4 items (i)–(v) | F9 | `python leakage_check.py` | `results/leakage_report.json` |
| 10 | Fill placeholders and rebuild both Word documents | all | `python fill_and_rebuild.py` | `manuscript_major_revision.docx`, `Response_to_Editor_and_Reviewers.docx` |

Every results file must contain `"dry_run": false` before
`fill_and_rebuild.py` accepts it. Files produced with `--dry-run` are for
pipeline testing only and are rejected by the filler.

## Zenodo deposit (F1)

1. Create a Zenodo deposit, upload the reproducibility package (code,
   manifests, seeds, configs, weights, run-level predictions, raw MMD logs,
   one regeneration script per table/figure, plus this kit).
2. Use the provided `.zenodo.json` as the deposit metadata.
3. Publish, copy the DOI (form `10.5281/zenodo.XXXXXXX`), the release tag and
   the commit hash into `results/f1_zenodo.json` (see `f1_zenodo.template.json`).
4. Verify the DOI resolves from an external network before submission.

## Environment

```
pip install numpy scipy
export MS_BDTT_ROOT=/path/to/your/ms-bdtt-repo   # your existing pipeline
export XJTU_ROOT=/path/to/XJTU-SY                # for e5 (35Hz12kN/37.5Hz11kN/40Hz10kN)
export SPFD_MANIFEST=/path/to/spfd_manifest.csv  # for e5 (F5b)
export MANIFEST_DIR=/path/to/manifests           # for leakage_check
```

GPU runs assume your existing PyTorch environment; the kit itself only needs
numpy/scipy for the statistics.

## Running on the GPU machine (the only place e1 can actually run)

The re-runs require the datasets, the pipeline and a CUDA GPU; on a machine
without them `e1_ten_seed.py` stops at the adapter boundary with an explicit
`NotImplementedError` instead of producing numbers. Always check first:

```
python check_env.py            # writes check_env_report.txt, prints the GPU budget
```

Expected budget (single RTX 4090, ~4 min per full pipeline run, from Table 10):

| script | runs | wall clock |
|---|---|---|
| e1_ten_seed.py | 2 methods × 10 seeds × 5 scenarios = 100 | ≈ 6.7 h |
| e2_openset_s4.py | 4 methods × 3 runs = 12 | ≈ 0.8 h |
| e3_retention_sweep.py | 5 ratios × 5 runs × 5 scenarios = 125 | ≈ 8.3 h |
| e4_budget_sweep.py | 2 rules × 6 budgets × 5 runs = 60 | ≈ 4.0 h |
| **total** | **297** | **≈ 19.8 h** |

`e5`, `e6`, `e7` and `leakage_check` need no training and run on CPU.

### Adapter wiring

`adapter.py` auto-discovers your pipeline. If your repo exposes any of
`ms_bdtt.experiment.run_one`, `ms_bdtt.main.run_one`, `ms_bdtt.train.evaluate`,
`src.experiment.run_one` or `experiment.run_one`, set `MS_BDTT_ROOT` and the
kit wires itself (it prints `[adapter] auto-wired: ...`). Otherwise edit the
five functions in `adapter.py`; the required return schemas are documented in
each docstring.

### Crash safety (important for the long runs)

`e1_ten_seed.py` checkpoints after **every** finished (scenario, method, seed)
triple into `results/e1_table9.json`. If the job dies at run 80, simply
re-issue `python e1_ten_seed.py` — completed triples are skipped (`[skip]`)
and the run continues. Use `--scenarios S5` to work on one scenario at a
time. `fill_and_rebuild.py` refuses any results file carrying
`"dry_run": true`, so dry-run artefacts can never enter the manuscript.

### One command on the GPU machine

```
python run_all.py                 # check -> e1 -> e2 -> e3 -> e4 -> e5/e6/e7
                                  # -> leakage -> tier decision -> (optionally) fill
python run_all.py --through e1    # stop after the ten-seed replication
python run_all.py --skip e3,e4    # only what feeds Table 9
python run_all.py --fill --apply-tier   # also apply the tier wording and rebuild
```

`run_all.py` aborts before regenerating the documents if any required result
file is missing or still flagged `"dry_run": true`, so a half-finished GPU
night can never leak into the manuscript.

### Hand-off back to the submission machine

Copy the `results/` folder from the GPU machine and run, on the machine that
holds the two Word files:

```
python collect_and_finalize.py --from <path-to-results-folder>
```

It refuses dry-run files, copies the results into `kit/results`, runs the
tier check, applies the tier wording (B or C), fills every placeholder,
rebuilds both `.docx` files (content + heading styles) and prints a
verification block (file size, remaining placeholders, styled paragraphs,
number of images). Add `--dry` to inspect without touching the documents.

### Deciding the wording (this is the check you asked for)

```
python check_tier.py              # ten-seed dOA vs the three-seed grid of Table 5
```

It prints, per scenario, the three-seed value, the ten-seed value, the
consistency band, the 95 % CI, p and Cohen's d, and then the recommended
tier:

* **Tier A** — every CI excludes zero and the ten-seed effects agree with the
  grid within max(1.0 pp, 25 %): keep the current wording (optionally add the
  sentence about the replication reproducing the three-seed effect sizes).
* **Tier B** — all CIs exclude zero but the effect shrank systematically
  (e.g. S5 from +6.8 pp to below +4 pp): soften. `python apply_tier.py --tier B`
  rewrites the abstract, Section 5.1, Section 6.1/6.2 and the letter.
* **Tier C** — some CI includes zero: withdraw the comparative claim for that
  scenario only. `python apply_tier.py --tier C`.

The consistency band is deliberately claim-level (absolute 1.0 pp **and**
relative 25 %), not purely statistical: a headline margin that shrinks by 40 %
changes what the abstract may say even when the interval still excludes zero.

### Order for the revision

1. `python e1_ten_seed.py` → **Table 9 and the macro-averages**. This result
   decides whether the abstract and Section 6 keep the current wording
   ("+3.6 and +6.8 percentage points") or must be tightened; compare the
   ten-seed ΔOA against the three-seed grid of Table 5 before touching the
   text.
2. `python e2_openset_s4.py` → Table 8b (open-set results promised to the
   reviewer).
3. `python e3_retention_sweep.py` and `python e4_budget_sweep.py` →
   Tables D.2/D.3, which replace the fit-derived thresholds of Table C.1 and
   Fig. 10 and decide whether the 1.7× figure can be restated as measured.
4. `python e5_label_budget.py`, `python e6_identifiability.py`,
   `python e7_mmd_logging.py`, `python leakage_check.py`.
5. `python fill_and_rebuild.py` → the two final Word documents are regenerated
   with every placeholder filled and the heading styles re-applied.
