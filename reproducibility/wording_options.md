# Wording options conditioned on the ten-seed result (e1)

The sentences below are the ones whose strength depends on the e1 output
(Table 9, Section 5.6). Once `results/e1_table9.json` exists, pick the tier
that matches it and apply the corresponding edits before running
`fill_and_rebuild.py` (the filler refreshes the numbers; this file governs the
prose).

Decision rule (evaluated per scenario and for the five-scenario macro-average):

| e1 outcome | Tier |
|---|---|
| CI of the mean paired ΔOA excludes 0 **and** the ten-seed ΔOA stays within the range implied by the three-seed grid of Table 5 (i.e. the ΔOA values of Table 9 agree with Table 5 to within their run-to-run dispersion) | **A — keep current wording** |
| CI excludes 0 but the ΔOA is materially smaller than the three-seed grid (for example S5 drops from +6.8 pp to below +4 pp) | **B — soften** |
| CI includes 0 in any scenario, or the sign of ΔOA flips | **C — withdraw the comparative claim in that scenario** |

---

## Tier A — keep current wording (no edit)

Abstract, Section 5.1, Section 6.1 and the response letter stand as written:
"+3.6 and +6.8 percentage points", "the improvement is significant in every
scenario". Only the numbers of Table 9 change (automatically).

Optional refinement: state in Section 5.6 that the ten-seed replication
reproduced the three-seed effect sizes within their dispersion, e.g.
"The ten-seed replication reproduces the three-seed effect sizes: the paired
mean differences agree with the grid of Table 5 within their run-to-run
dispersion, and all five confidence intervals exclude zero."

---

## Tier B — soften (replace the strength, keep the direction)

### Abstract (one number to change)

Replace

> MS-BDTT attains a five-scenario macro-average accuracy of 83.9 % (range
> 76.0–96.5 %) and 76.0 ± 3.5 % in the fully unlabelled-target scenario,
> exceeding the strongest baseline by 3.6 and 6.8 percentage points,
> respectively.

with (example for a ten-seed ΔOA of +5.2 pp on S5)

> ... exceeding the strongest baseline by 3.6 percentage points on the
> five-scenario macro-average and by 5.2 percentage points in the fully
> unlabelled-target scenario, where the ten-seed paired comparison gives a
> 95 % confidence interval of [x.x, y.y] percentage points.

### Section 5.1

Replace "the advantage is most pronounced in the unlabelled-target scenario
S5, where MS-BDTT exceeds COSDA by 6.8 percentage points" with the
ten-seed value and its interval, and add one sentence:

> The ten-seed replication of this comparison (Table 9) confirms the
> direction of the effect in every scenario; the effect size in S5 is
> [smaller than the three-run grid suggested], and the grid values should
> accordingly be read as exploratory.

### Section 6.1 / 6.2

Replace "surpasses all baselines by at least 6.8 percentage points" with
"surpasses all baselines by at least [x.x] percentage points in the ten-seed
paired comparison (Table 9)".

### Response letter, point 5

Replace "The improvement is significant in every scenario" with "The
ten-seed replication confirms the direction of the improvement in every
scenario; the confidence intervals are reported in Table 9 of the revised
manuscript." Keep the statement about the corrected three-run p-value.

---

## Tier C — withdraw the comparative claim for that scenario

The claim is removed for the affected scenario only; the framework's
descriptive results remain.

### Abstract

Replace "exceeding the strongest baseline by 3.6 and 6.8 percentage points,
respectively" with

> ... the ten-seed paired replication confirms the improvement over the
> strongest baseline on [S1–S4], while in [S5] the paired confidence interval
> includes zero and no difference is established at that sample size.

### Section 5.1

Delete the margin sentence for the affected scenario and add:

> In [S5], the ten-seed paired comparison yields a mean difference of [x.x]
> percentage points with a 95 % confidence interval of [a, b], which includes
> zero; we therefore do not claim an improvement in that scenario. The
> remaining scenarios are unaffected.

### Section 6.1 / 6.2

Replace "it surpasses all baselines by at least 6.8 percentage points" with
"it surpasses all baselines in [S1–S4]; in S5 the ten-seed paired comparison
does not establish a difference." Also soften the third key finding
("attention weighting is what makes multi-source aggregation safe") to
"attention weighting reduced the negative-transfer risk in the measured
S5 operating points (Fig. 5), an effect that the ten-seed replication does
not resolve at scenario level."

### Table 9

Keep all values, including CIs that include zero, and add a footnote:

> Intervals that include zero indicate that the ten-seed paired comparison
> does not establish a difference in that scenario; no inferential claim is
> made from those rows.

### Response letter, point 5

> We accept the reviewer's requirement of training-level uncertainty and have
> replicated the comparison with ten seeds. The resulting intervals confirm
> the direction of the improvement in [S1–S4]; in [S5] the interval includes
> zero, and we have removed the comparative claim for that scenario
> accordingly rather than retaining a significance statement that the data do
> not support. All grid-level statements remain labelled exploratory.

---

## What never changes

* The metric definitions of Section 4.6 and the bootstrap unit (test record,
  class-stratified, within run) — the reviewer asked for these explicitly.
* The corrected three-run p-value statement (≈ 0.0138 minimum compatible
  value for S5) — it stays whatever the ten-seed outcome is.
* The labelling that the three-run grid is exploratory.
* The qualified (model-inferred) status of the 63 % retention ratio and the
  1.7× budget-efficiency estimate — these are governed by e3/e4, not by e1.
