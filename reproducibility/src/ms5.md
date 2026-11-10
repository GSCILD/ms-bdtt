# 5. Results and discussion

## 5.1 Main results

Table 5 reports the overall accuracy of MS-BDTT and of the ten baselines in the five scenarios, and Figure 6 summarises the same results. MS-BDTT achieves the highest five-scenario macro-average overall accuracy of 83.9 %, outperforming the strongest baseline COSDA (80.4 %) by 3.6 percentage points (the mean of the per-scenario differences; the difference of the two rounded macro-averages is 3.5 pp) and DT+DA (78.2 %) by 5.7 percentage points. The advantage is most pronounced in the unlabelled-target scenario S5, where MS-BDTT exceeds COSDA by 6.8 percentage points, and remains consistent in the cross-dataset and cross-equipment scenarios S3 and S4, where the margins over COSDA are 2.9 and 3.8 percentage points, respectively. All values in this table are exploratory (three training runs; Section 4.6), and the S3 and S4 columns follow the revised labelling and open-set protocols of Sections 4.2.3 and 4.2.4 after regeneration; the S1, S2 and S5 columns correspond to the audited manifests without protocol changes.

Table 5. Overall accuracy (%) of MS-BDTT and baseline methods in the five cross-domain scenarios (mean ± SD over three independent runs; exploratory, see Section 4.6).

| Method | S1 | S2 | S3 | S4 | S5 | Averageᵃ |
| --- | --- | --- | --- | --- | --- | --- |
| Source-Only | 95.2 ± 0.8 | 78.4 ± 2.1 | 72.1 ± 1.5 | 68.5 ± 2.3 | 58.3 ± 3.1 | 74.5 ± 1.2 |
| Deep CORAL | 93.1 ± 1.0 | 80.2 ± 1.8 | 75.6 ± 1.3 | 71.3 ± 1.9 | 62.1 ± 2.7 | 76.5 ± 1.0 |
| DANN | 94.5 ± 0.9 | 82.1 ± 1.6 | 77.8 ± 1.2 | 73.2 ± 1.7 | 65.4 ± 2.4 | 78.6 ± 0.9 |
| Sim-Only | 88.3 ± 1.2 | 71.5 ± 2.5 | 65.2 ± 1.8 | 61.8 ± 2.8 | 52.1 ± 3.5 | 67.8 ± 1.5 |
| RandomBridge | 91.7 ± 1.0 | 76.3 ± 2.0 | 71.4 ± 1.4 | 67.9 ± 2.1 | 58.6 ± 2.9 | 73.2 ± 1.1 |
| DT-Only | 92.1 ± 0.9 | 79.8 ± 1.7 | 74.5 ± 1.3 | 70.2 ± 1.8 | 63.4 ± 2.5 | 76.0 ± 0.9 |
| DT+DA | 93.5 ± 0.8 | 81.2 ± 1.5 | 76.8 ± 1.2 | 72.5 ± 1.6 | 67.1 ± 2.2 | 78.2 ± 10.0 |
| PI-DA | 94.2 ± 0.9 | 82.8 ± 1.4 | 78.5 ± 1.1 | 74.0 ± 1.5 | 68.5 ± 2.0 | 79.6 ± 9.7 |
| COSDA | 94.8 ± 0.8 | 83.5 ± 1.4 | 79.2 ± 1.1 | 75.1 ± 1.5 | 69.2 ± 2.1 | 80.4 ± 9.6 |
| MS-BDTT | 96.5 ± 0.6 | 86.2 ± 1.0 | 82.1 ± 0.9 | 78.9 ± 1.1 | 76.0 ± 3.5 | 83.9 ± 8.0 |

ᵃ The Average column is the unweighted macro-average of the five per-scenario means. The value after ± in this column is the across-scenario standard deviation of those five means (for MS-BDTT: 96.5, 86.2, 82.1, 78.9, 76.0), which quantifies the spread of difficulty across scenarios and is not a run-to-run uncertainty. Run-to-run uncertainty is the value after ± in each scenario column. Bold values indicate the best performance in each scenario. S3 follows the labelling protocol of Section 4.2.3 and S4 the closed-set track of Section 4.2.4, in both cases after regeneration under the corrected protocols.

Three observations merit discussion. First, MS-BDTT shows its largest improvement in S5, where it outperforms COSDA by 6.8 percentage points. This is consistent with the advantage of continuous domain interpolation when labelled target data are entirely unavailable: the Bayesian-calibrated bridge supplies physically consistent synthetic data that generalise better than purely statistical adaptation. Second, the improvement in S1 is modest (1.7 percentage points over COSDA), which suggests that when the domain shift is small, simpler methods such as DANN and COSDA are nearly as effective and the additional machinery of MS-BDTT is not warranted. Third, MS-BDTT shows the lowest run-to-run standard deviation across random seeds in four of the five scenarios, indicating robustness to initialisation and to data partitioning; the exception is S5, where the absence of target labels leaves a residual standard deviation of 3.5 percentage points.

[[FIG6]]

Figure 6. Overall accuracy of MS-BDTT and of the ten baselines (Table 5; mean ± SD over three independent runs). (a) Accuracy in each of the five cross-domain scenarios for four representative baselines and MS-BDTT; the margin of MS-BDTT over COSDA widens from 1.7 percentage points in S1 to 6.8 in S5. (b) Five-scenario macro-average accuracy for all eleven methods, with error bars showing the across-scenario standard deviation of the five per-scenario means (Table 5, footnote ᵃ); MS-BDTT attains 83.9 %, exceeding COSDA by 3.6 percentage points. Colour is redundant with hatching, so the panels remain legible in greyscale.

## 5.2 Domain gap analysis

Table 6 and Figs. 7 and 8 quantify how each component of MS-BDTT narrows the distributional discrepancy between source and target domains, measured as relative MMD reduction with respect to the unadapted baseline. The raw per-scenario, per-stage MMD² values, the per-domain sample sizes, the kernel treatment and the estimator details are documented in Appendix C.4 (Table C.2), so that every relative reduction in this section can be recomputed from a single auditable source.

Table 6. Cumulative MMD-based domain gap reduction by component (five-scenario macro-average).

| Configuration | MMD reduction (pp) | Cumulative reduction (pp) |
| --- | --- | --- |
| Baseline (no adaptation) | 0.0 | 0.0 |
| + Continuous bridge (Stage 1) | 43.8 | 43.8 |
| + Bayesian calibration (Stage 2) | 21.9 | 65.7 |
| + Attention weighting (Stage 3) | 7.7 | 73.4 |
| + Adversarial alignment (Stage 3) | 13.2 | 86.6 |

The continuous bridge accounts for the largest single reduction, 43.8 percentage points. Consistently with the discussion of Eq. (14), we interpret this as measured evidence that the populated bridge sequence reduces the estimated discrepancy in this study; the decomposition of Eq. (14) motivates the construction, but the reduction itself is an empirical observation, not a consequence of the triangle inequality. Bayesian calibration removes a further 21.9 percentage points, bringing the cumulative reduction to 65.7 %. The particle filter corrects systematic biases of the mechanistic model, namely stiffness overestimation, damping underestimation and missing noise characteristics, and thereby moves the synthetic distribution closer to the measured target distribution. Attention weighting removes an additional 7.7 percentage points by suppressing bridge samples from irrelevant operating conditions, which amounts to a soft domain selection rather than a hard inclusion or exclusion, and adversarial alignment contributes the final 13.2 percentage points through feature-space adaptation. The total reduction of 86.6 % exceeds that of COSDA (71.2 %) and DT+DA (68.5 %).

[[FIG7]]

Figure 7. Residual source–target domain gap after each stage of MS-BDTT (normalised MMD, five-scenario macro-average; Table 6). Each bar is the gap that remains once the stage is applied: 100.0 % with no adaptation, 56.2 % after the continuous bridge, 34.3 % after Bayesian calibration, 26.6 % after attention weighting and 13.4 % after adversarial alignment. Values outside the bars give the residual gap and values inside give the cumulative reduction, which reaches 86.6 percentage points.

[[FIG8]]

Figure 8. Per-component contribution to the cumulative MMD reduction, decomposed from the archived per-stage values of Appendix C.4 (percentage points of reduction with respect to the unadapted baseline of the same scenario). Stacked bars separate the continuous bridge, Bayesian calibration, attention weighting and adversarial alignment; the totals are 89.1 % in S1, 86.0 % in S3 and 93.1 % in S5, the three scenarios for which per-stage features are retained in the analysis logs. The five-scenario average of the same quantities is 86.6 percentage points (Table 6). Colour is redundant with hatching.

## 5.3 Ablation studies

Systematic ablation studies quantify the contribution of each component. Table 7 reports results on S1, S3 and S5; the Avg. column is the unweighted three-scenario macro-average over exactly these three scenarios and is never mixed with the five-scenario macro-average of Table 5 (83.9 %) or with per-scenario values.

Table 7. Ablation study: overall accuracy (%) after removing one component at a time (mean over three runs; exploratory).

| Variant | S1 | S3 | S5 | Avg. (S1/S3/S5) |
| --- | --- | --- | --- | --- |
| MS-BDTT (full) | 96.5 | 82.1 | 76.0 | 84.9 |
| w/o demand-guided sampling | 94.8 | 78.5 | 71.2 | 81.5 |
| w/o Bayesian calibration | 92.1 | 76.3 | 68.5 | 79.0 |
| w/o attention mechanism | 95.0 | 79.8 | 72.1 | 82.3 |
| w/o continuous bridge | 93.2 | 75.1 | 67.8 | 78.7 |
| w/o adversarial loss | 95.5 | 80.2 | 73.5 | 83.1 |
| w/o physical consistency loss | 94.1 | 77.9 | 70.8 | 80.9 |

Removing the continuous bridge causes the largest degradation, 6.2 percentage points on the three-scenario average, which is consistent with continuous interpolation, rather than the transfer network alone, being the primary source of the improvement. Bayesian calibration is the second most influential component, contributing 5.9 percentage points; without it the bridge remains physically plausible but numerically inaccurate, and the resulting signatures mislead the classifier. This ordering is consistent with the domain-gap decomposition of Table 6, in which the bridge and the calibration stage together account for 65.7 of the 86.6 percentage points of total reduction.

The remaining components contribute non-redundantly: the physical consistency loss 4.0 percentage points, demand-guided sampling 3.4, the attention mechanism 2.6 and the adversarial loss 1.8. Two findings deserve emphasis. First, the benefit of the attention mechanism grows with the heterogeneity of the sources: it is worth 2.6 percentage points on the three-scenario average but 3.9 in S5, where four different source datasets are merged and the risk of negative transfer is highest; these are the two measured operating points shown in Fig. 5(b)–(c). Second, removing the adversarial loss costs less than removing any other component, which indicates that most of the distributional alignment is already achieved by the calibrated bridge and that adversarial training plays a complementary, fine-tuning role.

## 5.4 Validation on the synthetic ship propulsion dataset

On SPFD, MS-BDTT attains 76.0 ± 3.5 % sample-weighted overall accuracy over all test samples in the unlabelled-target scenario S5. The sample-weighted OA and the unweighted macro-average over groups are distinct quantities, and both are now reported explicitly: the unweighted mean of the seven per-group OA values of Table 8 is 74.5 %, while the sample-weighted OA — the headline figure — is 76.0 %, the difference arising because the groups have unequal test supports (Table F.5). Wherever the text of this paper quotes a single SPFD figure, it is the sample-weighted OA.

Table 8 and Figure 9 give the per-fault-type and per-regime results. Accuracy increases monotonically with fault severity, from 78.2 % for early bearing wear to 85.3 % for severe bearing wear, whereas propeller cavitation is the most difficult single fault at 68.5 %, presumably because its signature is broadband and overlaps the hull-vibration background below 500 Hz; we note that cavitation classes receive no constraint from L_phy (Section 3.8). Composite faults remain the weakest case at 61.2 %, as discussed in Section 6.3. The severity gradient of the bearing-wear family is read through the explicit defect-area-fraction mapping of Section 4.2.5, which is a modelling assumption rather than a measurement.

Table 8. Per-fault-type results on SPFD (unlabelled-target scenario S5; mean over three runs; exploratory).

| Fault type | OA (%) | Precision | Recall | F1 |
| --- | --- | --- | --- | --- |
| Bearing wear (early) | 78.2 | 0.76 | 0.80 | 0.78 |
| Bearing wear (moderate) | 81.5 | 0.82 | 0.81 | 0.81 |
| Bearing wear (severe) | 85.3 | 0.86 | 0.84 | 0.85 |
| Shaft misalignment | 72.1 | 0.70 | 0.74 | 0.72 |
| Propeller cavitation | 68.5 | 0.67 | 0.70 | 0.68 |
| Gear pitting | 74.8 | 0.73 | 0.76 | 0.74 |
| Composite faults | 61.2 | 0.58 | 0.65 | 0.61 |

[[FIG9]]

Figure 9. SPFD results in the unlabelled-target scenario S5 (Table 8). (a) Overall accuracy and F1-score per fault type; accuracy increases monotonically with fault severity from 78.2 % for early bearing wear to 85.3 % for severe bearing wear, propeller cavitation is the most difficult single fault at 68.5 %, and composite faults are the weakest case at 61.2 %. (b) Overall accuracy by operating regime, from 69.8 % at low load (30–50 % MCR) to 81.2 % at high load (75–100 % MCR), with the run-to-run standard deviation over three runs. The dashed line marks the dataset-level sample-weighted overall accuracy of 76.0 %, which differs from the unweighted mean of the per-group values (74.5 %) because the groups have unequal test supports (Section 5.4, Table F.5).

Figure 9(b) shows that accuracy also depends strongly on the operating regime: it rises from 69.8 % at low load (30–50 % MCR) to 81.2 % at high load (75–100 % MCR). Demand-guided sampling allocates about 40 % more bridge samples to low-load regimes, which partly mitigates the disparity, but the fundamental difficulty is the low signal-to-noise ratio of fault signatures at idle conditions. Incorporating signal enhancement, for example ensemble empirical mode decomposition, as a preprocessing step is therefore a promising direction for future work.

### 5.4.1 Open-set evaluation on S4

Table 8b reports the open-set track of Section 4.2.4 for MS-BDTT and the three strongest or most methodologically distinct baselines. The rejection threshold τ_rej is fixed at the 95th percentile of the held-out source-validation maximum-softmax distribution for every method.

Table 8b. Open-set results on S4 (closed-set accuracy over mapped classes, unknown-detection AUROC, open-set accuracy OS and OS*; mean over three runs).

| Method | CCA (%) | AUROC | OS (%) | OS* (%) |
| --- | --- | --- | --- | --- |
| Source-Only | 68.5 | 0.64 | 61.2 | 58.4 |
| DANN | 73.2 | 0.72 | 67.4 | 64.8 |
| COSDA | 75.1 | 0.78 | 70.5 | 68.2 |
| MS-BDTT | 78.9 | 0.87 | 75.2 | 73.6 |

The closed-set track of Table 5 measures transfer over the mapped classes; the open-set track measures the additional ability to withhold predictions on target-private classes. MS-BDTT's attention weighting supplies a sample-level relevance signal that is not available to the baselines, which is the mechanism we expect to benefit unknown rejection; the comparison in Table 8b tests this expectation under the identical, leakage-safe threshold rule.

## 5.5 Sensitivity analysis

This section analyses the sensitivity of MS-BDTT to its key hyperparameters in order to assess robustness and to provide practical tuning guidance. The search ranges and the selected values are summarised in Appendix D.

Demand-map weight α. The weight α balances domain separation against fault sensitivity. Values below 0.4 overemphasise fault sensitivity: the sampler concentrates on high-severity faults and neglects the domain-alignment regions, which costs 3.2 percentage points. Values above 0.8 overemphasise domain separation and allocate excessive samples to boundary regions where the classification boundaries are ambiguous, costing 2.7 percentage points. The selected value α = 0.6 reflects the empirical finding that domain-level discrepancy is the dominant factor in marine cross-domain diagnosis.

Adversarial loss weight λ. Values below 0.2 weaken domain alignment and leave 4.1 percentage points of unaddressed distributional shift; values above 0.8 cause over-adaptation, in which the feature extractor becomes so domain-invariant that it loses class-discriminative information, costing 5.3 percentage points. The ramped schedule from 0 to λ over epochs 1–20 prevents early over-adaptation while allowing gradual domain alignment.

Physical consistency weight μ. Values above 0.5 over-constrain the model to the simulated physics and reduce accuracy by 6.2 percentage points, because the classifier can no longer learn the deviations of real data from idealised physics. The selected value μ = 0.1 provides sufficient regularisation without dominating the data-driven learning signal.

Attention temperature τ. Values above 2.0 flatten the attention distribution towards uniform weighting and lose 2.9 percentage points, whereas values below 0.5 create excessively peaked distributions that ignore potentially useful bridge samples and lose 1.8 percentage points. The value τ = 1.0 provides a balanced trade-off. This non-monotonicity is consistent with the estimation-term trade-off of Proposition 2, in which a more concentrated weighting reduces the divergence term but lowers the effective sample size (Appendix C.2).

Number of particles N. The particle count trades calibration accuracy against computational cost, and Table 11 reports the measured sensitivity. N = 100 attains 93.2 % on S1 and 71.4 % on S5 at 0.5 s per calibration step; N = 250 attains 95.3 % and 74.8 % at 1.1 s; N = 500 attains 96.5 % and 76.0 % at 2.3 s; N = 1000 attains 97.2 % and 76.7 % at 4.6 s; and N = 2000 attains 97.4 % and 76.9 % at 9.2 s. N = 500 is therefore the recommended default, because it retains 0.7 percentage points on S1 relative to N = 1000 at half the cost, whereas N = 2000 adds a further 0.2 pp for twice the time of N = 1000. The resampling trigger scales with the particle count (ESS < N/2), so the degeneracy risk is unchanged across the sweep.

## 5.6 Statistical significance and run-level uncertainty

The full evaluation grid (Tables 5, 7, 8) is exploratory: it uses three training runs per cell, which is insufficient to support confirmatory claims of the strength originally stated. The confirmatory analysis for the headline comparison therefore replicates MS-BDTT and COSDA with ten independent seeds per scenario, paired by seed, under the manifests and protocols of Section 4. Table 9 reports the ten-seed paired comparison: per-seed paired differences, the two-sided paired t-test over ten seeds, the seed-level bootstrap confidence interval of the mean paired difference (B = 10,000), and Cohen's d for paired data. The resampling unit of every bootstrap in this paper and the aggregation across seeds follow Section 4.6 exactly.

Table 9. Paired comparison of MS-BDTT against COSDA (ΔOA in percentage points; ten seeds per scenario, paired by seed).

| Scenario | ΔOA (pp, mean ± SD) | 95 % CI (seed-level bootstrap) | p-value (paired t, df = 9) | Cohen's d |
| --- | --- | --- | --- | --- |
| S1 | 1.7 ± 0.4 | [1.45, 1.98] | < 0.001 | 4.5 |
| S2 | 2.7 ± 0.5 | [2.28, 3.04] | < 0.001 | 5.1 |
| S3 | 2.9 ± 0.6 | [2.47, 3.35] | < 0.001 | 4.8 |
| S4 | 3.8 ± 0.7 | [3.24, 4.30] | < 0.001 | 5.1 |
| S5 | 6.8 ± 1.2 | [5.94, 7.72] | < 0.001 | 5.5 |
| Macro-average | 3.6 ± 2.0 | [1.86, 5.30] | < 0.001 | — |

For transparency we record the correction of a previous statistical error: the three-run S5 comparison printed a p-value of 0.009 that is not compatible with the displayed means and standard deviations, whose minimum compatible two-sided p-value is approximately 0.0138. The ten-seed paired analysis above replaces the three-run test throughout, and all conclusions that previously relied on the three-run t-test are now bounded by the ten-seed intervals of Table 9. The ten-seed replication also yields five-scenario macro-averages of 84.0 ± 2.0 for MS-BDTT and 80.4 for COSDA; the remaining grid tables retain the three-seed protocol and are explicitly exploratory.

## 5.7 Computational efficiency

Table 10 and Figure 10 summarise the computational cost. The measured particle-count sensitivity is reported in Table 11.

Table 10. Computational cost on an NVIDIA RTX 4090 GPU.

| Method | Training (min) | Inference (ms/sample) | Parameters (M) |
| --- | --- | --- | --- |
| Source-Only | 12 | 0.8 | 1.1 |
| Deep CORAL | 18 | 0.8 | 1.1 |
| DANN | 22 | 0.9 | 1.4 |
| DT+DA | 64 | 1.1 | 1.6 |
| PI-DA | 48 | 1.0 | 1.6 |
| COSDA | 31 | 1.0 | 1.6 |
| RandomBridge | 70 | 1.2 | 2.3 |
| MS-BDTT | 85 | 1.2 | 2.3 |
| MS-BDTT on Jetson AGX Orin | — (offline) | 4.6 | 2.3 |

Figure 10 shows the accuracy reached as a function of the number of bridge samples generated per operating condition, measured over six budget levels and five runs per point for both allocation rules (Appendix D.2, Table D.3). Demand-guided sampling attains 61.8 %, 71.5 %, 75.5 %, 79.2 %, 82.1 % and 83.9 % at 20, 40, 60, 80, 100 and 120 samples per condition, against 52.4 %, 64.1 %, 70.2 %, 75.8 %, 81.4 % and 86.8 % for the uniform grid. Two budget-efficiency statements follow from these measurements, and we report both because they answer different questions. Expressed as the budget each rule needs to reach 90 % of its own full-budget accuracy, the demand-guided rule needs 60 samples per condition against 100 for the uniform grid, a measured gain of 1.67×. Expressed at the common accuracy level of 75.5 %, the demand-guided rule needs 60 samples against 80 for the uniform grid, a gain of 1.33×. An earlier version of this manuscript quoted a fit-derived uniform-grid threshold of approximately 102 samples and a 1.7× gain; the measured sweep supersedes both. We report for completeness that the uniform grid reaches a higher full-budget accuracy (86.8 % versus 83.9 %): the demand-guided rule is recommended for its steeper early budget curve, not for a higher ceiling.

[[FIG10]]

Figure 10. Measured budget sweep: five-scenario macro-average accuracy against the number of bridge samples per operating condition for uniform grid sampling (squares) and demand-guided sampling (circles), with error bars giving the standard deviation over five runs per point. The dotted line marks 75.5 %, which is 90 % of the demand-guided full-budget accuracy (83.9 %). Demand-guided sampling reaches that level with 60 samples per condition, whereas the uniform grid reaches it with 80; measured against 90 % of each rule's own full-budget accuracy the comparison is 60 against 100 samples, i.e. a measured budget-efficiency gain of 1.67×.

## 5.8 Threats to validity

Five threats to the validity of these results should be kept in mind. First, the marine target domain is synthetic: SPFD is generated by the same simulator that produces the bridge, so shared modelling assumptions may yield an optimistic estimate of the simulator-to-measurement gap reduction, even though the target data are generated with independent noise and sea-state realisations and no target label is used. Second, all fault signatures are single-fault or, in the composite group, pairwise combinations; the interaction of three or more simultaneous degradation modes is not covered. Third, the comparison uses the baselines' published configurations with hyperparameters retuned on the S1 validation split only, which is fair but may favour methods with fewer hyperparameters. Fourth, the label protocols of Sections 4.2.3 and 4.2.5 — the degradation-boundary labelling of XJTU-SY and the defect-area-fraction severity mapping — are stated modelling assumptions whose mis-specification would propagate to S3 and S5. Fifth, the three-run evaluation grid is exploratory, and effect sizes smaller than the run-to-run dispersion should not be interpreted as established differences.
